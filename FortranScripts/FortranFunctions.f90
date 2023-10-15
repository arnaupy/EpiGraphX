module NetworkEncoder 
    implicit none
contains
! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
! /////////////////////////////////SIM_COMFINAMENT_SIRS////////////////////////////
! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    subroutine SIM_Confinament_SIRS(network_path, save_path, IRatio, restriction, lambda, beta, daymax, daylength)
        implicit none
    ! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    !                             DEFINICIÓ DE VARIABLES
    ! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    ! VARIABLES PER BUCLES I SEED
        integer iter1, iter2, s, daymax, iter3
    ! NOMS DEL ARXIUS
        character*200 network_path, save_path, sim_path, file_path
    ! PARÀMETRES
        real*8 lambda, beta, Pinf, Prec, Psus, IRatio,tau, time, daylength, rand_number, restriction, a, R0
        real*8 NItot_actual, NItot_anterior
        integer, allocatable :: I(:), R(:), Ilinks(:), NInew(:)
        integer NI, NR, Nlinks, infected, susceptible, recovered, day, wave, condition, mesures_time
    ! DADES XARXA
        integer, allocatable :: links(:), degree(:), Pini(:), Pfin(:)
        integer N, E
        Namelist/parameters/ file_path, N, E 
        Namelist/network/ links, degree, Pini, Pfin 
    ! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    !                               PROGRAMA PRINCIPAL
    ! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    ! S'INICIALITZA LA SEED
        s = 20255
        call init_genrand(s)

    ! ES GUARDEN ELS PARÀMETRES DE LA XARXA 
        open(10,file = network_path)
        read(10, nml = parameters)
        allocate(links(1:2*E), degree(1:N), Pini(1:N), Pfin(1:N))
        read(10, nml = network)
        close(10)

    ! PARÀMETRES SIMULACIÓ
        write(*,*)repeat("%&", 32)
        write(*,*)"#Xarxa: ", get_file_name(file_path, .FALSE.)
        write(*,*)"#Nodes totals: ", N
        write(*,*)"#Ritme d'infecció: ", lambda
        write(*,*)"#Ritme de susceptibilitat: ", beta

    ! NODES INFECTATS
        NI = int(N*IRatio)
        allocate(I(1:N))
        I = 0
        do iter1 = 1, NI
            infected = int(genrand_real2() * N) + 1
            do while (any(I.eq.infected))
                infected = int(genrand_real2() * N) + 1
            enddo
            I(iter1) = infected
        enddo
        write(*,*)"#ºn Nodes infectats inicials: ", NI
        ! write(*,*)"#Nodes infectats: ", I

    ! VECTOR LINKS EN CONTACTE AMB UN INFECTAT
        Nlinks = 0
        allocate(Ilinks(1:2*E))
        Ilinks = 0
        do iter1 = 1, NI
            infected = I(iter1)
            do iter2 = Pini(infected), Pfin(infected)
                if (all(I.ne.links(iter2))) then
                    Nlinks = Nlinks + 1
                    Ilinks(Nlinks*2 - 1) = infected
                    Ilinks(Nlinks*2) = links(iter2)
                endif
            enddo
        enddo
        write(*,*)"#Links inicials en contacte amb un infectat: ", Nlinks
        !write(*,*)"#Links infectats", Ilinks

    ! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    !                           ALGORITME DE GUILLESPIE
    ! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    ! S'ESCRIU EL NOM DE L'ARXIU ON ES GUARDARAN LES DADES DE LA SIMULACIÓ
        write(sim_path, "(A,A,A,F6.4)")trim(save_path),"SIM_Confinament_SIRS_", "_Rest_", restriction
        sim_path = trim(sim_path)//"__"//trim(get_file_name(file_path, .FALSE.))
    ! S'OBRE L'ARXIU PER GUARDAR LES DADES
        open(20, file = trim(sim_path)//"__D.txt")
        time = 0d0
        day = 1
        NR = 0
        allocate(R(1:N))
        a = 1d0
        condition = 30
        mesures_time = 120
        wave = 1
        allocate(NInew(1:2))
        NInew(1) = NI
        NItot_anterior = NI/real(N)
        NInew(2) = 0
        write(20,*)day, real(NI)/real(N), 0, NInew(1)/real(N)
        do while ((NI.ne.0).and.(day.lt.daymax))
    ! ES CALCULA LA PROBABILITAT DE QUE HI HA HAGUI UNA INFECCIÓ O DE QUE HI HAGUI
    ! UNA RECUPERACIÓ O MORT
            tau = (NI*1 + Nlinks*lambda*a + NR*beta)
            Prec = (NI*1)/tau
            Pinf = (Nlinks*lambda*a)/tau
            Psus = (NR*beta)/tau
            rand_number = genrand_real2()

    ! SI HI HA UNA RECUPERACIÓ
            if (rand_number.le.Prec) then
                ! write(*,*)repeat("-", 70)
                ! write(*,*)"Recuperació"
                ! write(*,*)repeat("-", 70)
                recovered = int(genrand_real2()*NI + 1)
                ! write(*,*)"Node recuperat: ", I(recovered)
    ! ES TREUEN ELS LINKS DEL NODE RECUPERAT 
    10          do iter2 = 1, 2*Nlinks, 2
                    if (Ilinks(iter2).eq.I(recovered)) then
    ! ES PASA L'ÚLTIM ELEMENT A LA POSICIÓ ON ERA EL NODE INFECTAT
                        Ilinks(iter2) = Ilinks(Nlinks*2 - 1)
                        Ilinks(iter2 + 1) = Ilinks(Nlinks*2)
                        ! Ilinks(Nlinks*2 - 1) = 0
                        ! Ilinks(Nlinks*2) = 0
                        Nlinks = Nlinks - 1  
                        go to 10     
                    endif
                enddo
    ! S'AJUNTA EL NODE RECOVERED A LA LLISTA
                NR = NR + 1
                R(NR) = I(recovered)
    ! ES TREU EL NODE INFECTAT DE LA LLISTA D'INFECCIONS
                I(recovered) = I(NI)
                ! I(NI) = 0
                NI = NI - 1 
    ! SI HI HA UNA INFECCIÓ
            elseif ((rand_number.le.(Prec + Pinf)).and.(rand_number.gt.Prec)) then
                ! write(*,*)repeat("-", 70)
                ! write(*,*)"Infecció"
                ! write(*,*)repeat("-", 70)
                NInew(day + 1) = NInew(day + 1) + 1
                infected = Ilinks(2)
                NI = NI + 1
                I(NI) = infected
                ! write(*,*)"Node infectat: ", I(NI)
    ! ES CREEN LINKS INFECTABLES SI ALGUN DEL VEÏNS ESTÀ SUSCEPTIBLE
                do iter2 = Pini(infected), Pfin(infected)
                    if (all(I.ne.links(iter2)).and.all(R.ne.links(iter2))) then
    ! ES GENERA UN NOU LINK AL FINAL DE LA LLISTA DE LINKS INFECTABLES
                        Nlinks = Nlinks + 1
                        Ilinks(Nlinks*2 - 1) = infected
                        Ilinks(Nlinks*2) = links(iter2)
                    endif
                enddo
    ! ES TREUEN ELS LINKS AMB VEÏNS INFECTATS
    20          do iter2 = 2, Nlinks*2, 2
                    if (Ilinks(iter2).eq.infected) then
                        Ilinks(iter2) = Ilinks(Nlinks*2)
                        Ilinks(iter2 - 1) = Ilinks(Nlinks*2 - 1)
                        ! Ilinks(Nlinks*2) = 0
                        ! Ilinks(Nlinks*2 - 1) = 0
                        Nlinks = Nlinks - 1
                        go to 20
                    endif
                enddo                
                ! write(*,*)"Node infectat: ", I(NI)
    ! UN NODE RECUPERAT ES TORNA SUSCEPTIBLE
            else
                susceptible = int(genrand_real2()) + 1
                R(susceptible) = R(NR)
                NR = NR - 1
    ! ES CREEN NOUS LINKS ACTIUS AMB EL NODES INFECTAT VEÏNS
                do iter2 = Pini(R(susceptible)), Pfin(R(susceptible))
                    if (any(I.eq.links(iter2))) then
                        Nlinks = Nlinks + 1
                        Ilinks(Nlinks*2 - 1) = links(iter2)
                        Ilinks(Nlinks*2) = R(susceptible)
                    endif
                enddo                

            endif
            ! write(*,*)"#Infectats: ", I
            ! write(*,*)"#Links infectats", Ilinks
            ! write(*,*)"#Nodes recuperats: ", R
    ! S'ESCRIU EN UN ARCIU EL # DE NODES INFECTATS EN CADA ITERACIÓ
            time = time + (-log(genrand_real2()))/tau
            if (time.gt.(day*daylength)) then
                NInew(day + 1) = NInew(day + 1)*0.9
                day = day + 1
                NItot_actual = 0d0
                do iter3 = 1, day
                    NItot_actual = NItot_actual + NInew(iter3)*exp(-daylength*(day - iter3))
                enddo
                ! Restrictions are taken
                if (mod(day,condition).eq.0) then
                    if (R0.gt.1d0) then
                        wave = wave + 1
                        ! Frequency to take mesures
                        if (wave.gt.1) then
                            condition = mesures_time
                        endif
                        a = restriction
                    else
                        a = 1d0
                    endif
                endif 
                write(20,*)day, real(NI)/real(N), R0, NItot_actual/real(N)
                call append_int(NInew, 0)
                NItot_anterior = NItot_actual
            endif
        enddo
    30  close(20)
        if (day.eq.daymax) then
            write(*,*)repeat("-", 66)
            write(*,*)"ESTAT ESTACIONARI!!!"
            write(*,*)repeat("-", 66)
        else
            write(*,*)repeat("-", 66)
            write(*,*)"EPIDEMIA EXTINCTA!!!"
            write(*,*)repeat("-", 66)
        endif

        ! ES GUARDEN LES DADES A UN FITXER
        open(30, file = trim(sim_path)//"__I.txt")
        write(30,"(A,F6.4)")"daylength=", daylength
        write(30,"(A,F4.2)")"infected_ini=", IRatio
        write(30,"(A,F4.2)")"survivors=", (N-NI-NR)/real(N)
        write(30,"(A,F4.2)")"recovered=", NR/real(N)
        write(30,"(A,F4.2)")"infected=", NI/real(N)
        write(30,"(A,I0)")"days=", day
        close(30)
        deallocate(I, R, Ilinks, NInew)
        return
    end
! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
! /////////////////////////////////////SIM_COMFINAMENT/////////////////////////////
! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    subroutine SIM_Confinament(network_path, save_path, IRatio, lambda_ini, phi, daylength)
        implicit none
    ! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    !                             DEFINICIÓ DE VARIABLES
    ! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    ! VARIABLES PER BUCLES I SEED
        integer iter1, iter2, iter3, s, dailycases
    ! NOMS DEL ARXIUS
        character*200 network_path, save_path, file_path, sim_path, network_name
    ! INPUTS
        real*8 lambda, phi, IRatio
    ! PROBABILITATS
        real*8 Pinf, Prec, tau 
    ! INNER PARAMATERS
        real*8 time, R0, a, NItot_actual, NItot_anterior
    ! DAY VARIABLES
        integer day, daylength, day_asc, day_des
        integer relaxation_mesure, first_mesure, week, weekmax
    ! EVOLUTION VECTORS
        integer, allocatable :: I(:), R(:), Ilinks(:), NInew(:), mesures_vector(:)

        integer NI, NR, Nlinks, infected, susceptible, recovered, n_mesures

        real*8 lambda_ini
        integer take_mesure, following_mesure
        integer mask_reduction, ascending_steps, descending_steps, counter
        logical ascending, descending, automatic_asc, automatic_des, condition, restrictions

    ! DADES XARXA
        integer, allocatable :: links(:), degree(:), Pini(:), Pfin(:)
        integer N, E, sim
        Namelist/parameters/ N, E 
        Namelist/network/ links, degree, Pini, Pfin
    ! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    !                               PROGRAMA PRINCIPAL
    ! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    ! S'INICIALITZA LA SEED
        s = 5345834
        call init_genrand(s)
        allocate(mesures_vector(1:200))
        n_mesures = 0

    ! ES GUARDEN ELS PARÀMETRES DE LA XARXA 
        open(10,file = network_path)
        read(10, nml = parameters)
        allocate(links(1:2*E), degree(1:N), Pini(1:N), Pfin(1:N))
        read(10, nml = network)
        close(10)

    ! PARÀMETRES SIMULACIÓ
        lambda = lambda_ini
        write(*,*)repeat("%&", 38)
        write(*,*)"#Network: ", trim(get_file_name(network_path, .FALSE.))
        write(*,*)"#Total nodes: ", N
        write(*,*)"#lambda: ", lambda
        write(*,*)"#phi: ", phi
        write(*,*)"#daylength: ", daylength
        write(*,*)repeat("--", 38)

        allocate(Ilinks(1:2*E), I(1:N))
    ! NODES INFECTATS
        NI = int(N*IRatio)
        do iter1 = 1, NI
            infected = int(genrand_real2() * N) + 1
            do while (any(I.eq.infected))
                infected = int(genrand_real2() * N) + 1
            enddo
            I(iter1) = infected
        enddo
        write(*,*)NI
        write(*,*)"#ºn Nodes infectats inicials: ", NI

    ! VECTOR LINKS EN CONTACTE AMB UN INFECTAT
        Nlinks = 0
        do iter1 = 1, NI
             infected = I(iter1)
             do iter2 = Pini(infected), Pfin(infected)
                 if (all(I.ne.links(iter2))) then
                     Nlinks = Nlinks + 1
                     Ilinks(Nlinks*2 - 1) = infected
                     Ilinks(Nlinks*2) = links(iter2)
                endif
            enddo
        enddo
        write(*,*)"#Links inicials en contacte amb un infectat: ", Nlinks
        write(*,*)repeat("%&", 38)

    ! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    !                           ALGORITME DE GUILLESPIE
    ! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    ! S'ESCRIU EL NOM DE L'ARXIU ON ES GUARDARAN LES DADES DE LA SIMULACIÓ
        sim_path = save_path 
        write(sim_path, "(A,A,A,F5.3,A,F4.2,A,I0)")trim(sim_path), "SIM_Confinament_", &
        "_lambda_", lambda, "_phi_", phi, "_gamma_", daylength
        sim_path = trim(sim_path)//"__"//trim(get_file_name(network_path, .FALSE.))
    
    ! RESTRICTION PARAMETER
        ! LAS RESTRICCIONES SE TOMAN AUTOMATICAMENTE
        automatic_asc = .False.
        ! LAS RESTRICCIONES SE QUITAN AUTOMATICAMENTE
        automatic_des = .False.
        ! ASCENSO
        ascending = .False.
        ascending_steps = 3 ! in steps
        ! DESCENSO
        descending = .False.
        descending_steps = 4 ! in steps
        ! LA SIMULACION EMPIEZA SIN RESTRICCIONES
        restrictions = .False. 
        ! mask_on = .False.
        ! mask_reduction = 0.05
    ! TIME VARIABLES
        time = 0d0
        day = 1
        allocate(NInew(1:2), R(1:N))
        NR = 0 
        NInew(1) = int(N*IRatio)
        NItot_anterior = NI/real(N)
        NInew(2) = 0
    ! RESTRICTION VARIABLE
        a = 1d0
        counter = 0
    ! MESURES PARAMATERS
        take_mesure = 45

    ! S'OBRE L'ARXIU PER GUARDAR LES DADES
        open(20, file = trim(sim_path)//"__D.txt")
        write(20,*)day, real(NI)/real(N), NInew(day), IRatio, &
        real(N-NR-NI)/real(N), real(NR)/real(N), 0
        do while (NI.ne.0) 
     ! ES CALCULA LA PROBABILITAT DE QUE HI HA HAGUI UNA INFECCIÓ O DE QUE HI HAGUI
            tau = (NI*1 + Nlinks*a*lambda)
            Prec = (NI*1)/tau
            Pinf = (Nlinks*a*lambda)/tau

    ! SI HI HA UNA RECUPERACIÓ
            if (genrand_real2().le.Prec) then
                recovered = int(genrand_real2()*NI + 1)
    ! ES TREUEN ELS LINKS DEL NODE RECUPERAT 
    10          do iter2 = 1, 2*Nlinks, 2
                    if (Ilinks(iter2).eq.I(recovered)) then
    ! ES PASA L'ÚLTIM ELEMENT A LA POSICIÓ ON ERA EL NODE INFECTAT
                        Ilinks(iter2) = Ilinks(Nlinks*2 - 1)
                        Ilinks(iter2 + 1) = Ilinks(Nlinks*2)
                        Nlinks = Nlinks - 1  
                        go to 10     
                    endif
                enddo
    ! S'AJUNTA EL NODE RECOVERED A LA LLISTA
                NR = NR + 1
                R(NR) = I(recovered)
    ! ES TREU EL NODE INFECTAT DE LA LLISTA D'INFECCIONS
                I(recovered) = I(NI)
                NI = NI - 1 

    ! SI HI HA UNA INFECCIÓ
            else
                NInew(day + 1) = NInew(day + 1) + 1
                infected = Ilinks(2)
                NI = NI + 1
                I(NI) = infected
    ! ES CREEN LINKS INFECTABLES SI ALGUN DEL VEÏNS ESTÀ SUSCEPTIBLE
                do iter2 = Pini(infected), Pfin(infected)
                    if (all(I.ne.links(iter2)).and.all(R.ne.links(iter2))) then
    ! ES GENERA UN NOU LINK AL FINAL DE LA LLISTA DE LINKS INFECTABLES
                        Nlinks = Nlinks + 1
                        Ilinks(Nlinks*2 - 1) = infected
                        Ilinks(Nlinks*2) = links(iter2)
                    endif
                enddo
    ! ES TREUEN ELS LINKS AMB VEÏNS INFECTATS
    20          do iter2 = 2, Nlinks*2, 2
                    if (Ilinks(iter2).eq.infected) then
                        Ilinks(iter2) = Ilinks(Nlinks*2)
                        Ilinks(iter2 - 1) = Ilinks(Nlinks*2 - 1)
                        Nlinks = Nlinks - 1
                        go to 20
                    endif
                enddo  
            endif

        ! CALCULATE TIME
            time = time + (-log(genrand_real2()))/tau
            if (time.gt.(day*(1/real(daylength)))) then
                ! NInew(day + 1) = int(NInew(day + 1)*(1 - 0.5*genrand_real2()))
                NInew(day + 1) = int(NInew(day + 1)*0.1)
                day = day + 1
                NItot_actual = 0d0
                do iter3 = 1, day
                    NItot_actual = NItot_actual + NInew(iter3)*exp(-(1/real(daylength))*(day - iter3))
                enddo
                if (day.ge.2) then
                    R0 = (1 + (log(NItot_actual) - log(NItot_anterior))*daylength)*0.1d0
                    ! R0 = 1 + (log(NItot_actual) - log(NItot_anterior))*daylength
                endif
                call append_int(NInew, 0)
                NItot_anterior = NItot_actual
                write(*,*)a, day


                ! SE COMPRUEBA SI ESTA EN EL ASCENSO
                if (ascending.eqv..True.) then
                    if (day.eq.take_mesure) then
                        ! SI EL ASCENSO EN RESTRICCIONES HA ACABADO
                        if (counter.eq.ascending_steps) then
                            ascending = .False.
                            restrictions = .True.
                            day_asc = day
                            counter = 0
                            n_mesures = n_mesures + 1
                            mesures_vector(n_mesures) = day 
                        else
                            counter = counter + 1 
                            take_mesure = day + int(14/real(ascending_steps))  
                            a = a - (1 - phi)/real(ascending_steps)
                        endif
                    endif

                ! SE COMPRUEBA SI ESTA EN EL DESCENSO
                elseif (descending.eqv..True.) then
                    if (day.eq.take_mesure) then                        
                        ! SI EL DESCENSO EN RESTRICCIONES HA ACABADO
                        if (counter.eq.descending_steps) then
                            descending = .False.
                            day_des = day
                            restrictions = .False.
                            counter = 0
                            n_mesures = n_mesures + 1
                            mesures_vector(n_mesures) = day 
                        else
                            counter = counter + 1 
                            take_mesure = day + int(30/real(descending_steps))  
                            a = a + (1 - phi)/real(descending_steps)
                        endif
                    endif

                ! SE COMPRUEBA SI NO ESTA EN NINGUNO DE LES CASOS ANTERIORES
                else

                    ! SI LA SIMULACION ESTA EN LA FASE SIN RESTRICCIONES
                    if (restrictions.eqv..False.) then
                        if (automatic_asc.eqv..True.) then
                            condition = (R0.gt.1).and.(day.ge.30)
                        else 
                            condition = day.eq.23000
                        endif
                        
                        if (condition) then
                            ascending = .True.
                            take_mesure = day + int(14/real(ascending_steps))
                            counter = counter + 1
                            a = a - (1 - phi)/real(ascending_steps)
                            n_mesures = n_mesures + 1
                            mesures_vector(n_mesures) = day
                        endif

                    ! SI LA SIMULACION ESTA EN LA FASE CON RESTRICCIONES
                    else
                        if (automatic_des.eqv..True.) then
                            condition = (R0.lt.1).and.(day.ge.(day_asc + 14))
                            ! condition = (R0.lt.1)
                        else 
                            condition = day.eq.65000
                        endif
                        
                        if (condition) then
                            descending = .True.
                            take_mesure = day + int(30/real(descending_steps))
                            counter = counter + 1
                            a = a + (1 - phi)/real(descending_steps)
                            n_mesures = n_mesures + 1
                            mesures_vector(n_mesures) = day 
                        endif
                    
                ! ! MASK MESURE
                !     elseif (mask_on.eqv..True.) then
                !         lambda = lambda_ini*mask_reduction
                !         condition = following_mesure
                        
                    endif
                endif

                ! WRITES THE DATA IN A FILE
                ! if (day.le.7) then
                !     dailycases = 0
                ! else
                !     dailycases = NInew(day - 7)
                ! endif
                write(20,*)day, real(NI)/real(N), NInew(day), NItot_actual/real(N),&
                real(N-NR-NI)/real(N), real(NR)/real(N), R0
            endif

        enddo
        close(20)

        ! Pandemic end
        write(*,*)"# EPIDEMIC EXTICTED!!!"

        ! ES GUARDEN LES DADES A UN FITXER
        open(30, file = trim(sim_path)//"__I.txt")
        write(30,"(A,I0)")"infected_ini=", int(IRatio*N)
        write(30,"(A,F4.2)")"survivors=", (N-NR)/real(N)
        write(30,"(A,I0)")"days=", day
        ! if (automatic_asc.eqv..True.) then
        ! write(30,"(A,I0)")"first_mesure=", first_mesure
        ! write(30,"(A,I0)")"following_mesure=",  following_mesure
        ! write(30,"(A,I0)")"ascending_steps=", ascending_steps
        close(30)

        ! Deallocate vectors 
        write(*,*)"MESURES:"
        write(*,*)mesures_vector(:n_mesures)
        deallocate(I, R, Ilinks, NInew, mesures_vector)
        write(*,*)

        return
    end
! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
! /////////////////////////////////////SIRS_MODEL///////////////////////////////////
! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    subroutine SIRS_model(network_path, save_path, IRatio, lambda, beta, daymax, daylength)
        implicit none
    ! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    !                             DEFINICIÓ DE VARIABLES
    ! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    ! VARIABLES PER BUCLES I SEED
        integer iter1, iter2, iter3, s
    ! NOMS DEL ARXIUS
        character*200 network_path, save_path, sim_path, file_path
    ! PARÀMETRES
        real*8 lambda, beta, Pinf, Prec, Psus, IRatio,tau, temps, daylength, rand_number
        real*8 NItot_actual, NItot_anterior
        integer, allocatable :: I(:), R(:), Ilinks(:), NInew(:)
        integer NI, NR, Nlinks, infected, susceptible, recovered, day, daymax
    ! DADES XARXA
        integer, allocatable :: links(:), degree(:), Pini(:), Pfin(:)
        integer N, E
        Namelist/parameters/ file_path, N, E 
        Namelist/network/ links, degree, Pini, Pfin 
    ! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    !                               PROGRAMA PRINCIPAL
    ! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    ! S'INICIALITZA LA SEED
        s = 20255
        call init_genrand(s)

    ! ES GUARDEN ELS PARÀMETRES DE LA XARXA 
        open(10,file = network_path)
        read(10, nml = parameters)
        allocate(links(1:2*E), degree(1:N), Pini(1:N), Pfin(1:N))
        read(10, nml = network)
        close(10)

    ! PARÀMETRES SIMULACIÓ
        write(*,*)repeat("%&", 32)
        write(*,*)"#Xarxa: ", get_file_name(file_path, .FALSE.)
        write(*,*)"#Nodes totals: ", N
        write(*,*)"#Ritme d'infecció: ", lambda
        write(*,*)"#Ritme de susceptibilitat: ", beta

    ! NODES INFECTATS
        NI = int(N*IRatio)
        allocate(I(1:N))
        I = 0
        do iter1 = 1, NI
            infected = int(genrand_real2() * N) + 1
            do while (any(I.eq.infected))
                infected = int(genrand_real2() * N) + 1
            enddo
            I(iter1) = infected
        enddo
        write(*,*)"#ºn Nodes infectats inicials: ", NI
        ! write(*,*)"#Nodes infectats: ", I

    ! VECTOR LINKS EN CONTACTE AMB UN INFECTAT
        Nlinks = 0
        allocate(Ilinks(1:2*E))
        Ilinks = 0
        do iter1 = 1, NI
            infected = I(iter1)
            do iter2 = Pini(infected), Pfin(infected)
                if (all(I.ne.links(iter2))) then
                    Nlinks = Nlinks + 1
                    Ilinks(Nlinks*2 - 1) = infected
                    Ilinks(Nlinks*2) = links(iter2)
                endif
            enddo
        enddo
        write(*,*)"#Links inicials en contacte amb un infectat: ", Nlinks
        !write(*,*)"#Links infectats", Ilinks

    ! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    !                           ALGORITME DE GUILLESPIE
    ! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    ! S'ESCRIU EL NOM DE L'ARXIU ON ES GUARDARAN LES DADES DE LA SIMULACIÓ
        write(sim_path, "(A,A,A,F6.4,A,F6.4)")trim(save_path),"SIM_SIRS_", "_lambda_", lambda, "_beta_", beta
        sim_path = trim(sim_path)//"__"//trim(get_file_name(file_path, .FALSE.))
    ! S'OBRE L'ARXIU PER GUARDAR LES DADES
        open(20, file = trim(sim_path)//"__D.txt")
        temps = 0d0
        day = 1
        NR = 0
        NItot_anterior = NI/real(N)
        allocate(NInew(1:2))
        NInew(1) = int(N*IRatio)
        NInew(2) = 0
        allocate(R(1:N))
        write(20,*)day, real(NI)/real(N), NInew(1), IRatio, real(N - NI - NR)/real(N), real(NR)/real(N)
        do while ((NI.ne.0).and.(day.lt.daymax))
    ! ES CALCULA LA PROBABILITAT DE QUE HI HA HAGUI UNA INFECCIÓ O DE QUE HI HAGUI
    ! UNA RECUPERACIÓ O MORT
            tau = (NI*1 + Nlinks*lambda + NR*beta)
            Prec = (NI*1)/tau
            Pinf = (Nlinks*lambda)/tau
            Psus = (NR*beta)/tau
            rand_number = genrand_real2()

    ! SI HI HA UNA RECUPERACIÓ
            if (rand_number.le.Prec) then
                ! write(*,*)repeat("-", 70)
                ! write(*,*)"Recuperació"
                ! write(*,*)repeat("-", 70)
                recovered = int(genrand_real2()*NI + 1)
                ! write(*,*)"Node recuperat: ", I(recovered)
    ! ES TREUEN ELS LINKS DEL NODE RECUPERAT 
    10          do iter2 = 1, 2*Nlinks, 2
                    if (Ilinks(iter2).eq.I(recovered)) then
    ! ES PASA L'ÚLTIM ELEMENT A LA POSICIÓ ON ERA EL NODE INFECTAT
                        Ilinks(iter2) = Ilinks(Nlinks*2 - 1)
                        Ilinks(iter2 + 1) = Ilinks(Nlinks*2)
                        ! Ilinks(Nlinks*2 - 1) = 0
                        ! Ilinks(Nlinks*2) = 0
                        Nlinks = Nlinks - 1  
                        go to 10     
                    endif
                enddo
    ! S'AJUNTA EL NODE RECOVERED A LA LLISTA
                NR = NR + 1
                R(NR) = I(recovered)
    ! ES TREU EL NODE INFECTAT DE LA LLISTA D'INFECCIONS
                I(recovered) = I(NI)
                ! I(NI) = 0
                NI = NI - 1 
    ! SI HI HA UNA INFECCIÓ
            elseif ((rand_number.le.(Prec + Pinf)).and.(rand_number.gt.Prec)) then
                ! write(*,*)repeat("-", 70)
                ! write(*,*)"Infecció"
                ! write(*,*)repeat("-", 70)
                NInew(day + 1) = NInew(day + 1) + 1
                infected = Ilinks(2)
                NI = NI + 1
                I(NI) = infected
                ! write(*,*)"Node infectat: ", I(NI)
    ! ES CREEN LINKS INFECTABLES SI ALGUN DEL VEÏNS ESTÀ SUSCEPTIBLE
                do iter2 = Pini(infected), Pfin(infected)
                    if (all(I.ne.links(iter2)).and.all(R.ne.links(iter2))) then
    ! ES GENERA UN NOU LINK AL FINAL DE LA LLISTA DE LINKS INFECTABLES
                        Nlinks = Nlinks + 1
                        Ilinks(Nlinks*2 - 1) = infected
                        Ilinks(Nlinks*2) = links(iter2)
                    endif
                enddo
    ! ES TREUEN ELS LINKS AMB VEÏNS INFECTATS
    20          do iter2 = 2, Nlinks*2, 2
                    if (Ilinks(iter2).eq.infected) then
                        Ilinks(iter2) = Ilinks(Nlinks*2)
                        Ilinks(iter2 - 1) = Ilinks(Nlinks*2 - 1)
                        ! Ilinks(Nlinks*2) = 0
                        ! Ilinks(Nlinks*2 - 1) = 0
                        Nlinks = Nlinks - 1
                        go to 20
                    endif
                enddo                
                ! write(*,*)"Node infectat: ", I(NI)
    ! UN NODE RECUPERAT ES TORNA SUSCEPTIBLE
            else
                susceptible = int(genrand_real2()) + 1
                R(susceptible) = R(NR)
                NR = NR - 1
    ! ES CREEN NOUS LINKS ACTIUS AMB EL NODES INFECTAT VEÏNS
                do iter2 = Pini(R(susceptible)), Pfin(R(susceptible))
                    if (any(I.eq.links(iter2))) then
                        Nlinks = Nlinks + 1
                        Ilinks(Nlinks*2 - 1) = links(iter2)
                        Ilinks(Nlinks*2) = R(susceptible)
                    endif
                enddo                

            endif
            ! write(*,*)"#Infectats: ", I
            ! write(*,*)"#Links infectats", Ilinks
            ! write(*,*)"#Nodes recuperats: ", R
    ! S'ESCRIU EN UN ARCIU EL # DE NODES INFECTATS EN CADA ITERACIÓ
            temps = temps + (-log(genrand_real2()))/tau
            if (temps.gt.(day*daylength)) then
                NInew(day + 1) = NInew(day + 1)*0.9
                day = day + 1
                NItot_actual = 0d0
                do iter3 = 1, day
                    NItot_actual = NItot_actual + NInew(iter3)*exp(-daylength*(day - iter3))
                enddo
                write(20,*)day, real(NI)/real(N), NInew(day), NItot_actual/real(N), &
                real(N - NI - NR)/real(N), real(NR)/real(N)
                call append_int(NInew, 0)
                NItot_anterior = NItot_actual
            endif
        enddo
    30  close(20)
        if (day.eq.daymax) then
            write(*,*)repeat("-", 66)
            write(*,*)"ESTAT ESTACIONARI!!!"
            write(*,*)repeat("-", 66)
        else
            write(*,*)repeat("-", 66)
            write(*,*)"EPIDEMIA EXTINCTA!!!"
            write(*,*)repeat("-", 66)
        endif
        open(30, file = trim(sim_path)//"__I.txt")
        write(30,"(A,F6.4)")"daylength=", daylength
        write(30,"(A,F4.2)")"infected_ini=", IRatio
        write(30,"(A,F4.2)")"survivors=", (N-NI-NR)/real(N)
        write(30,"(A,F4.2)")"recovered=", NR/real(N)
        write(30,"(A,F4.2)")"infected=", NI/real(N)
        write(30,"(A,I0)")"days=", day
        close(30)
        deallocate(I, R, Ilinks)
        return
    end
! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
! /////////////////////////////////////SEIR_MODEL///////////////////////////////////
! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    subroutine SEIR_model(network_path, save_path, IRatio, beta, gamma, mu)
        implicit none
    ! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    !                             DEFINICIÓ DE VARIABLES
    ! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    ! VARIABLES PER BUCLES I SEED
        integer iter1, iter2, s, iter3
    ! NOMS DEL ARXIUS
        character*200 network_path, save_path, sim_path, file_path
    ! PARÀMETRES
        real*8 beta, gamma, mu, Pinf, Prec, Pexp, rand_number
        real*8 IRatio, tau, time, NItot_actual, NItot_anterior, R0
        integer, allocatable :: I(:), R(:), EX(:), Ilinks(:), NInew(:)
        integer NI, NR, NE, Nlinks, infected, susceptible, recovered, exposed, day, daylength
    ! DADES XARXA
        integer, allocatable :: links(:), degree(:), Pini(:), Pfin(:)
        integer N, E
        Namelist/parameters/ file_path, N, E 
        Namelist/network/ links, degree, Pini, Pfin 
    ! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    !                               PROGRAMA PRINCIPAL
    ! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    ! S'INICIALITZA LA SEED
        s = 20255
        call init_genrand(s)

    ! ES GUARDEN ELS PARÀMETRES DE LA XARXA 
        open(10,file = network_path)
        read(10, nml = parameters)
        allocate(links(1:2*E), degree(1:N), Pini(1:N), Pfin(1:N))
        read(10, nml = network)
        close(10)

    ! PARÀMETRES SIMULACIÓ
        write(*,*)repeat("%&", 32)
        write(*,*)"#Xarxa: ", get_file_name(file_path, .FALSE.)
        write(*,*)"#Nodes totals: ", N
        write(*,*)"#Ritme infecció: ", beta
        write(*,*)"#Ritme d'incubació: ", gamma
        write(*,*)"#Ritme de recuperació: ", mu

    ! NODES INFECTATS
        NI = int(N*IRatio)
        allocate(I(1:N))
        I = 0
        do iter1 = 1, NI
            infected = int(genrand_real2() * N) + 1
            do while (any(I.eq.infected))
                infected = int(genrand_real2() * N) + 1
            enddo
            I(iter1) = infected
        enddo
        write(*,*)"#ºn Nodes infectats inicials: ", NI
        ! write(*,*)"#Nodes infectats: ", I

    ! VECTOR LINKS EN CONTACTE AMB UN INFECTAT
        Nlinks = 0
        allocate(Ilinks(1:2*E))
        Ilinks = 0
        do iter1 = 1, NI
            infected = I(iter1)
            do iter2 = Pini(infected), Pfin(infected)
                if (all(I.ne.links(iter2))) then
                    Nlinks = Nlinks + 1
                    Ilinks(Nlinks*2 - 1) = infected
                    Ilinks(Nlinks*2) = links(iter2)
                endif
            enddo
        enddo
        write(*,*)"#Links inicials en contacte amb un infectat: ", Nlinks
        !write(*,*)"#Links infectats", Ilinks

    ! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    !                           ALGORITME DE GUILLESPIE
    ! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    ! S'ESCRIU EL NOM DE L'ARXIU ON ES GUARDARAN LES DADES DE LA SIMULACIÓ
        write(sim_path, "(A,A,A,F5.3,A,F5.3)")trim(save_path),"SIM_SEIR_", "_beta_", beta, "_gamma_", gamma
        sim_path = trim(sim_path)//"__"//trim(get_file_name(network_path, .FALSE.))
    ! S'OBRE L'ARXIU PER GUARDAR LES DADES
        open(20, file = trim(sim_path)//"__D.txt")
        time = 0d0
        day = 1
        daylength = 125
        NE = 0
        allocate(EX(1:N))
        NR = 0
        allocate(R(1:N))
        NItot_anterior = NI/real(N)
        allocate(NInew(1:2))
        NInew(1) = int(N*IRatio)
        NInew(2) = 0
        write(20,*)day, real(NI)/real(N), NInew(day), IRatio, &
        real(N-NR-NI-NE)/real(N), real(NR)/real(N), 0, real(NE)/real(N)        
        do while ((NI.ne.0).or.(NE.ne.0))
    ! ES CALCULA LA PROBABILITAT DE QUE HI HA HAGUI UNA INFECCIÓ O DE QUE HI HAGUI
    ! UNA RECUPERACIÓ O MORT
            tau = (NE*gamma + Nlinks*beta + NI*mu)
            Pexp = (Nlinks*beta)/tau
            Pinf = (NE*gamma)/tau
            Prec = (NI*mu)/tau
            rand_number = genrand_real2()
    ! SI HI HA UNA EXPOSICIÓ
            if (rand_number.le.Pexp) then
                exposed = Ilinks(2)
                NE = NE + 1
                EX(NE) = exposed
    ! ES TREUEN ELS LINKS AMB VEÏNS INFECTATS
    20          do iter2 = 2, Nlinks*2, 2
                    if (Ilinks(iter2).eq.exposed) then
                        Ilinks(iter2) = Ilinks(Nlinks*2)
                        Ilinks(iter2 - 1) = Ilinks(Nlinks*2 - 1)
                        Nlinks = Nlinks - 1
                        go to 20
                    endif
                enddo
    ! SI HI HA UNA INFECCIÓ
            elseif ((rand_number.le.(Pinf + Pexp))) then
                ! write(*,*)repeat("-", 70)
                ! write(*,*)"Infecció"
                ! write(*,*)repeat("-", 70)
                infected = int(genrand_real2()*NE) + 1
                NI = NI + 1
                I(NI) = EX(infected)
                EX(infected) = EX(NE)
                NE = NE - 1
                NInew(day + 1) = NInew(day + 1) + 1
                ! write(*,*)"Node infectat: ", I(NI)
    ! ES CREEN LINKS INFECTABLES SI ALGUN DEL VEÏNS ESTÀ SUSCEPTIBLE
                do iter2 = Pini(I(NI)), Pfin(I(NI))
                    if (all(I.ne.links(iter2)).and.all(R.ne.links(iter2)).and.all(EX.ne.links(iter2))) then
    ! ES GENERA UN NOU LINK AL FINAL DE LA LLISTA DE LINKS INFECTABLES
                        Nlinks = Nlinks + 1
                        Ilinks(Nlinks*2 - 1) = I(NI)
                        Ilinks(Nlinks*2) = links(iter2)
                    endif
                enddo
    ! SI HI HA UNA RECUPERACIÓ
            elseif (rand_number.gt.(Pinf + Pexp)) then
                ! write(*,*)repeat("-", 70)
                ! write(*,*)"Recuperació"
                ! write(*,*)repeat("-", 70)
                recovered = int(rand_number*NI) + 1
                ! write(*,*)"Node recuperat: ", I(recovered)
    ! ES TREUEN ELS LINKS DEL NODE RECUPERAT 
    10          do iter2 = 1, 2*Nlinks, 2
                    if (Ilinks(iter2).eq.I(recovered)) then
    ! ES PASA L'ÚLTIM ELEMENT A LA POSICIÓ ON ERA EL NODE INFECTAT
                        Ilinks(iter2) = Ilinks(Nlinks*2 - 1)
                        Ilinks(iter2 + 1) = Ilinks(Nlinks*2)
                        ! Ilinks(Nlinks*2 - 1) = 0
                        ! Ilinks(Nlinks*2) = 0
                        Nlinks = Nlinks - 1  
                        go to 10     
                    endif
                enddo
    ! S'AJUNTA EL NODE RECOVERED A LA LLISTA
                NR = NR + 1
                R(NR) = I(recovered)
    ! ES TREU EL NODE INFECTAT DE LA LLISTA D'INFECCIONS
                I(recovered) = I(NI)
                ! I(NI) = 0
                NI = NI - 1
    
            endif
            ! write(*,*)"#Infectats: ", I
            ! write(*,*)"#Links infectats", Ilinks
            ! write(*,*)"#Nodes recuperats: ", R
    ! S'ESCRIU EN UN ARCIU EL # DE NODES INFECTATS EN CADA ITERACIÓ
            time = time + (-log(genrand_real2()))/tau
            if (time.gt.(day*(1/real(daylength)))) then
                NInew(day + 1) = int(NInew(day + 1)*0.1)
                day = day + 1
                NItot_actual = 0d0
                do iter3 = 1, day
                    NItot_actual = NItot_actual + NInew(iter3)*exp(-(1/real(daylength))*(day - iter3))
                enddo
                if (day.ge.2) then
                    R0 = 1 + (log(NItot_actual) - log(NItot_anterior))*daylength
                    write(*,*)R0, NItot_actual, NItot_anterior
                endif
                call append_int(NInew, 0)
                NItot_anterior = NItot_actual
                write(20,*)day, real(NI)/real(N), NInew(day), NItot_actual/real(N),&
                real(N-NR-NI-NE)/real(N), real(NR)/real(N), R0, real(NE)/real(N)  
            endif
        enddo
    30  close(20)
    write(*,*)repeat("-", 76)
        write(*,*)"S'ha extingit la pandemia!!!"
        write(*,*)repeat("-", 76)

        open(30, file = trim(sim_path)//"__I.txt")
        write(30,"(A,I0)")"daylength=", daylength
        write(30,"(A,F4.2)")"infected_ini=", IRatio
        write(30,"(A,F4.2)")"survivors=", (N-NR)/real(N)
        write(30,"(A,I0)")"days=", day
        close(30)
        deallocate(I, R, EX, Ilinks)
        return
    end
! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
! /////////////////////////////////////SIR_MODEL///////////////////////////////////
! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    subroutine SIR_model(network_path, save_path, IRatio, lambda, daylength)
        implicit none
    ! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    !                             DEFINICIÓ DE VARIABLES
    ! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    ! VARIABLES PER BUCLES I SEED
        integer iter1, iter2, iter3, s
    ! NOMS DEL ARXIUS
        character*200 network_path, save_path, sim_path, file_path
    ! PARÀMETRES
        real*8 lambda, Pinf, Prec, IRatio, tau, temps, NItot_actual, NItot_anterior, R0
        integer, allocatable :: I(:), R(:), Ilinks(:), NInew(:)
        integer NI, NR, Nlinks, infected, susceptible, recovered, day, daylength
    ! DADES XARXA
        integer, allocatable :: links(:), degree(:), Pini(:), Pfin(:)
        integer N, E
        Namelist/parameters/ N, E 
        Namelist/network/ links, degree, Pini, Pfin 
    ! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    !                               PROGRAMA PRINCIPAL
    ! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    ! S'INICIALITZA LA SEED
        s = 20255
        call init_genrand(s)

    ! ES GUARDEN ELS PARÀMETRES DE LA XARXA 
        open(10,file = network_path)
        read(10, nml = parameters)
        allocate(links(1:2*E), degree(1:N), Pini(1:N), Pfin(1:N))
        read(10, nml = network)
        close(10)

    ! PARÀMETRES SIMULACIÓ
        write(*,*)repeat("%&", 38)
        write(*,*)"#Network: ", trim(get_file_name(network_path, .FALSE.))
        write(*,*)"#Total nodes: ", N
        write(*,*)"#lambda: ", lambda
        write(*,*)"#daylength: ", daylength
        write(*,*)repeat("--", 38)

    ! NODES INFECTATS
        NI = int(N*IRatio)
        allocate(I(1:N))
        I = 0
        do iter1 = 1, NI
            infected = int(genrand_real2() * N) + 1
            do while (any(I.eq.infected))
                infected = int(genrand_real2() * N) + 1
            enddo
            I(iter1) = infected
        enddo
        write(*,*)"#ºn Nodes infectats inicials: ", NI

    ! VECTOR LINKS EN CONTACTE AMB UN INFECTAT
        Nlinks = 0
        allocate(Ilinks(1:2*E))
        Ilinks = 0
        do iter1 = 1, NI
            infected = I(iter1)
            do iter2 = Pini(infected), Pfin(infected)
                if (all(I.ne.links(iter2))) then
                    Nlinks = Nlinks + 1
                    Ilinks(Nlinks*2 - 1) = infected
                    Ilinks(Nlinks*2) = links(iter2)
                endif
            enddo
        enddo
        write(*,*)"#Links inicials en contacte amb un infectat: ", Nlinks

    ! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    !                           ALGORITME DE GUILLESPIE
    ! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    ! S'ESCRIU EL NOM DE L'ARXIU ON ES GUARDARAN LES DADES DE LA SIMULACIÓ
        write(sim_path, "(A,A,A,F6.4,A,I0)")trim(save_path),"SIM_SIR_", "_lambda_", lambda, "_gamma_", daylength
        sim_path = trim(sim_path)//"__"//trim(get_file_name(network_path, .FALSE.))
    ! S'OBRE L'ARXIU PER GUARDAR LES DADES
        open(20, file = trim(sim_path)//"__D.txt")
        temps = 0d0
        day = 1
        NR = 0
        NItot_anterior = NI/real(N)
        allocate(NInew(1:2), R(1:N))
        NInew(1) = int(N*IRatio)
        NInew(2) = 0
        write(20,*)day, (real(NI)*100)/real(N), NInew(day), IRatio*100, &
        real(N-NR-NI)/real(N), real(NR)/real(N), 0
        do while (NI.ne.0) 
    ! ES CALCULA LA PROBABILITAT DE QUE HI HA HAGUI UNA INFECCIÓ O DE QUE HI HAGUI
    ! UNA RECUPERACIÓ O MORT
            tau = (NI*1 + Nlinks*lambda)
            Prec = (NI*1)/tau
            Pinf = (Nlinks*lambda)/tau
    ! SI HI HA UNA RECUPERACIÓ
            if (genrand_real2().le.Prec) then
                recovered = int(genrand_real2()*NI + 1)
    ! ES TREUEN ELS LINKS DEL NODE RECUPERAT 
    10          do iter2 = 1, 2*Nlinks, 2
                    if (Ilinks(iter2).eq.I(recovered)) then
    ! ES PASA L'ÚLTIM ELEMENT A LA POSICIÓ ON ERA EL NODE INFECTAT
                        Ilinks(iter2) = Ilinks(Nlinks*2 - 1)
                        Ilinks(iter2 + 1) = Ilinks(Nlinks*2)
                        Nlinks = Nlinks - 1  
                        go to 10     
                    endif
                enddo
    ! S'AJUNTA EL NODE RECOVERED A LA LLISTA
                NR = NR + 1
                R(NR) = I(recovered)
    ! ES TREU EL NODE INFECTAT DE LA LLISTA D'INFECCIONS
                I(recovered) = I(NI)
                NI = NI - 1 
    ! SI HI HA UNA INFECCIÓ
            else
                NInew(day + 1) = NInew(day + 1) + 1
                infected = Ilinks(2)
                NI = NI + 1
                I(NI) = infected
    ! ES CREEN LINKS INFECTABLES SI ALGUN DEL VEÏNS ESTÀ SUSCEPTIBLE
                do iter2 = Pini(infected), Pfin(infected)
                    if (all(I.ne.links(iter2)).and.all(R.ne.links(iter2))) then
    ! ES GENERA UN NOU LINK AL FINAL DE LA LLISTA DE LINKS INFECTABLES
                        Nlinks = Nlinks + 1
                        Ilinks(Nlinks*2 - 1) = infected
                        Ilinks(Nlinks*2) = links(iter2)
                    endif
                enddo
    ! ES TREUEN ELS LINKS AMB VEÏNS INFECTATS
    20          do iter2 = 2, Nlinks*2, 2
                    if (Ilinks(iter2).eq.infected) then
                        Ilinks(iter2) = Ilinks(Nlinks*2)
                        Ilinks(iter2 - 1) = Ilinks(Nlinks*2 - 1)
                        Nlinks = Nlinks - 1
                        go to 20
                    endif
                enddo                
            endif
            temps = temps + (-log(genrand_real2()))/tau
            if (temps.gt.(day*(1/real(daylength)))) then
                ! NInew(day + 1) = int(NInew(day + 1)*0.1)
                day = day + 1
                NItot_actual = 0d0
                do iter3 = 1, day
                    NItot_actual = NItot_actual + NInew(iter3)*exp(-(1/real(daylength))*(day - iter3))
                enddo
                if (day.ge.2) then
                    R0 = 1 + (log(NItot_actual) - log(NItot_anterior))*daylength
                    ! write(*,*)R0, NItot_actual, NItot_anterior
                endif
                call append_int(NInew, 0)
                NItot_anterior = NItot_actual
                ! WRITES THE DATA IN A FILE
                write(20,*)day, (real(NI)*100)/real(N), NInew(day)/real(N), (NItot_actual*100)/real(N),&
                real(N-NR-NI)/real(N), real(NR)/real(N), R0
            endif
        enddo
    30  close(20)
        write(*,*)repeat("-", 66)
        write(*,*)"S'ha extingit la pandemia!!!"
        write(*,*)repeat("-", 66)

        ! ES GUARDEN LES DADES A UN FITXER
        open(30, file = trim(sim_path)//"__I.txt")
        write(30,"(A,I0)")"infected_ini=", int(IRatio*N)
        write(30,"(A,F4.2)")"survivors=", (N-NR)/real(N)
        write(30,"(A,I0)")"days=", day
        close(30)

        ! Deallocate vectors 
        deallocate(I, R, Ilinks, NInew)
        write(*,*)
        return
    
    end
! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
! /////////////////////////////////////SIS_MODEL///////////////////////////////////
! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    subroutine SIS_model(network_path, save_path, IRatio, rate, totalsteps)
        implicit none
    ! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    !                             DEFINICIÓ DE VARIABLES
    ! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    ! VARIABLES PER BUCLES I SEED
        integer iter1, iter2, s
    ! NOMS DEL ARXIUS
        character*200 network_path, save_path, sim_path, file_path
    ! PARÀMETRES
        real*8 rate, Psus, Pinf, IRatio, tau, temps, daylength
        integer, allocatable :: I(:), Ilinks(:)
        integer NI, Nlinks, infected, susceptible, totalsteps, day
    ! DADES XARXA
        integer, allocatable :: links(:), degree(:), Pini(:), Pfin(:)
        integer N, E
        Namelist/parameters/ file_path, N, E 
        Namelist/network/ links, degree, Pini, Pfin 
    ! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    !                               PROGRAMA PRINCIPAL
    ! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    ! S'INICIALITZA LA SEED
        s = 20255
        call init_genrand(s)

    ! ES GUARDEN ELS PARÀMETRES DE LA XARXA 
        open(10,file = network_path)
        read(10, nml = parameters)
        allocate(links(1:2*E), degree(1:N), Pini(1:N), Pfin(1:N))
        read(10, nml = network)
        close(10)

    ! PARÀMETRES SIMULACIÓ
        write(*,*)repeat("-", 66)
        write(*,*)"#Infectivitat: ", rate
        write(*,*)"#Nodes totals: ", N

    ! NODES INFECTATS
        NI = int(N*IRatio) 
        allocate(I(1:N))
        do iter1 = 1, NI
            infected = int(genrand_real2() * N) + 1
            do while (any(I.eq.infected))
                infected = int(genrand_real2() * N) + 1
            enddo
            I(iter1) = infected
        enddo
        write(*,*)"#Nodes infectats: ", NI

    ! VECTOR LINKS EN CONTACTE AMB UN INFECTAT
        Nlinks = 0
        allocate(Ilinks(1:2*E))
        do iter1 = 1, NI
            infected = I(iter1)
            do iter2 = Pini(infected), Pfin(infected)
                if (all(I.ne.links(iter2))) then
                    Nlinks = Nlinks + 1
                    Ilinks(Nlinks*2 - 1) = infected
                    Ilinks(Nlinks*2) = links(iter2)
                endif
            enddo
        enddo
        write(*,*)"#Links inicials en contacte amb un infectat: ", Nlinks
        ! write(*,*)"#Links infectats", Ilinks

    ! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    !                           ALGORITME DE GUILLESPIE
    ! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    ! S'ESCRIU EL NOM DE L'ARXIU ON ES GUARDARAN LES DADES DE LA SIMULACIÓ
        write(sim_path, "(A,A,A,F6.4)")trim(save_path),"SIM_SIS_", "_lambda_", rate
        sim_path = trim(sim_path)//"__"//trim(get_file_name(file_path, .FALSE.))
    ! S'OBRE L'ARXIU PER GUARDAR LES DADES
        temps = 0d0
        day = 1
        daylength = 0.065d0
        open(20, file = trim(sim_path)//"__D.txt")
        write(20,*)day, real(NI)/real(N), real(N - NI)/real(N)
        do iter1 = 1, totalsteps
    ! ES CALCULA LA PROBABILITAT DE QUE HI HA HAGUI UNA INFECCIÓ O DE QUE HI HAGUI
    ! UNA RECUPERACIÓ A SUSCEPTIBLE
            tau = (NI*1 + Nlinks*rate)
            Psus = (NI*1)/tau
            Pinf = (Nlinks*rate)/tau
    ! SI HI HA UNA RECUPERACIÓ
            if (genrand_real2().le.Psus) then
                ! write(*,*)repeat("-", 70)
                ! write(*,*)"Recuperació"
                ! write(*,*)repeat("-", 70)
                susceptible = int(genrand_real2()*NI + 1)
                ! write(*,*)"Node recuperat: ", I(susceptible)
    ! ES TREUEN ELS LINKS DEL NODE RECUPERAT QUE ESTAN SUSCETIBLES
    10          do iter2 = 1, 2*Nlinks, 2
                    if (Ilinks(iter2).eq.I(susceptible)) then
    ! ES PASA L'ÚLTIM ELEMENT A LA POSICIÓ ON ERA EL NODE INFECTAT
                        Ilinks(iter2) = Ilinks(Nlinks*2 - 1)
                        Ilinks(iter2 + 1) = Ilinks(Nlinks*2)
                        Nlinks = Nlinks - 1  
                        go to 10     
                    endif
                enddo
    ! ES CREEN LINKS INFECTABLES SI ALGUN DEL VEÏNS TAMBÉ ESTABA INFECTAT
                do iter2 = Pini(I(susceptible)), Pfin(I(susceptible)) 
                    if (any(I.eq.links(iter2))) then
    ! ES GENERA UN NOU LINK AL FINAL DE LA LLISTA DE LINKS INFECTABLES
                        Nlinks = Nlinks + 1
                        Ilinks(Nlinks*2 - 1) = links(iter2)
                        Ilinks(Nlinks*2) = I(susceptible)
                    endif
                enddo
    ! ES TREU EL NODE INFECTAT DE LA LLISTA D'INFECCIONS
                I(susceptible) = I(NI)
                NI = NI - 1 
    ! SI HI HA UNA INFECCIÓ
            else
                ! write(*,*)repeat("-", 70)
                ! write(*,*)"Infecció"
                ! write(*,*)repeat("-", 70)
                infected = Ilinks(2)
                NI = NI + 1
                I(NI) = infected
    ! ES CREEN LINKS INFECTABLES SI ALGUN DEL VEÏNS ESTÀ SUSCEPTIBLE
                do iter2 = Pini(infected), Pfin(infected)
                    if (all(I.ne.links(iter2))) then
    ! ES GENERA UN NOU LINK AL FINAL DE LA LLISTA DE LINKS INFECTABLES
                        Nlinks = Nlinks + 1
                        Ilinks(Nlinks*2 - 1) = infected
                        Ilinks(Nlinks*2) = links(iter2)
                    endif
                enddo
    ! ES TREUEN ELS LINKS AMB VEÏNS INFECTATS
    20          do iter2 = 2, Nlinks*2, 2
                    if (Ilinks(iter2).eq.infected) then
                        Ilinks(iter2) = Ilinks(Nlinks*2)
                        Ilinks(iter2 - 1) = Ilinks(Nlinks*2 - 1)
                        Nlinks = Nlinks - 1
                        go to 20
                    endif
                enddo                
                ! write(*,*)"Node infectat: ", I(NI)
            endif
            ! write(*,*)"#Infectats: ", I
            ! write(*,*)"#Links infectats", Ilinks
    ! S'ATURA L'ALGORITME SI HI S'HA EXTINGUIT L'INFECCIÓ
            if (NI.eq.0) then
                write(*,*)"NO HI HA CAP NODE INFECTAT"
                write(*,*)"Iteració: ", iter1
                go to 30
    ! S'ATURA L'ALGORITME SI NO QUEDEN NODE PER INFECTAR
            elseif (NI.eq.N) then
                write(*,*)"NO HI HA CAP NODE PER INFECTAT"
                write(*,*)"Iteració: ", iter1
                go to 30
            endif
    ! S'ESCRIU EN UN ARCIU EL # DE NODES INFECTATS EN CADA ITERACIÓ
            temps = temps + (-log(genrand_real2()))/tau
            if (temps.gt.(day*daylength)) then
                day = day + 1
                write(20,*)day, real(NI)/real(N), real(N - NI)/real(N)
            endif
        enddo
    30  close(20)

        open(30, file = trim(sim_path)//"__I.txt")
        write(30,"(A,F6.4)")"daylength=", daylength
        write(30,"(A,F4.2)")"infected_ini=", IRatio
        write(30,"(A,F4.2)")"survivors=", (N-NI)/real(N)
        write(30,"(A,I0)")"days=", day
        close(30)
        deallocate(I, Ilinks)
        return
    end
! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
! ///////////////////////////////////READ_NETWORK//////////////////////////////////
! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    subroutine read_network(file_path, data_path)
        implicit none
        ! VARIABLES LECTURA INICAL
        character*200 file_path, data_path
        integer N, E, Nlinks_unicos, link
        integer, allocatable :: links(:), degree(:), Pini(:), Pfin(:), links_unicos(:)
        Namelist/parameters/ N, E 
        Namelist/network/ links, degree, Pini, Pfin

        ! VARIABLES NODES CONSECUTIUS
        character*200 copy_file_path, original_path 
        integer, allocatable :: labels(:)
        integer i, j, first_replace
        logical zero, repe, c1, c2, c3, c4

        !VARIABLES LINKS REPETITS
        integer k, candidate

    ! --------------------------------------------------------------------------------------------
        ! LECTURA INICIAL DE L'ARXIU ABANS D'ANALITZAR SI FA FALTA ALGUN CANVI
        data_path = "Xarxes/"//get_file_name(file_path, .FALSE.)
        data_path = trim(data_path)//".dat"
        call read_file(file_path, data_path)
        original_path = file_path

        ! LLECTURA DE LES DADES 
        open(50, file = data_path)
        read(unit = 50, nml = parameters) 
        allocate(links(1:2*E), degree(1:N), Pini(1:N), Pfin(1:N))
        read(unit = 50, nml = network)
        close(50)

        write(*,*)repeat("%&", 38)
        write(*,*)"#Mirando si los nodos són consecutivos"
        ! MIRAR SI ELS NODES SON CONSECUTIUS
        allocate(labels(1:N))
        N = 0
        do i = 1, size(degree)
            if (degree(i).ne.0) then
                N = N + 1
                labels(i) = N
            endif
        enddo 
        write(*,*)repeat("%&", 38)
        write(*,*)"#Nodos consecutivos DONE"
        
        allocate(links_unicos(1:2*E))
        Nlinks_unicos = 0
        ! ES FA UNA CÒPIA DE L'ARXIU ORIGINAL REETIQUETANT ELS NODES QUE NO ESTAN EN ORDRE CONSECUTIU
        copy_file_path = "Data/Copy_data.txt"
        write(*,*)repeat("%&", 38)
        write(*,*)"#Reetiquetando"
        open(70, file = file_path)
        open(80, file = copy_file_path)
        do i = 1, E
            read(70,*)j, k
            if ((i.ne.0).and.(j.ne.0)) then
                j = labels(j)
                k = labels(k)
                write(80,*)j, k
            endif
        enddo
        close(80)
        close(70)
        write(*,*)repeat("%&", 38)
        write(*,*)"#Reetiquetado DONE"
        
        ! SEGONA LECTURA DE L'ARXIU HAVENT RESOLT EL PROBLEMA DE LES ETIQUETES
        call read_file(copy_file_path, data_path)

        ! LLECTURA DE LES DADES DE LA COPIA CORREGIDA
        open(90, file = data_path)
        read(unit = 90, nml = parameters) 
        deallocate(links, degree, Pini, Pfin)
        allocate(links(1:2*E), degree(1:N), Pini(1:N), Pfin(1:N))
        read(unit = 90, nml = network)
        close(90)

        write(*,*)repeat("%&", 38)
        write(*,*)"#Mirando si los links se repiten"
        ! ES MIRA SI ES REPETEIXEN LINKS I ES CORREGEIX
        do i = 1, N
    40      do j = Pini(i), Pfin(i)
                candidate = links(j)
                do k = 0, degree(i) - 1
                    if ((links(Pini(i) + k).eq.candidate).and.((Pini(i) + k)).ne.j) then
                        call remove_int(links, Pini(i) + k)
                        degree(i) = degree(i) - 1
                        Pini(i + 1:) = Pini(i + 1:) - 1
                        Pfin(i:) = Pfin(i:) - 1
                        go to 40
                    endif
                enddo
            enddo
            write(*,*)"Revisados ", i, "nodos de ", N
        enddo
        write(*,*)repeat("%&", 38)
        write(*,*)"#Links repetidos DONE"
        write(*,*)repeat("%&", 38)
        E = size(links)/2
    
        ! UN COP S'HAN CORREGUIT ELS POSIBLES ERRORS DE LA XARXA, ES GUARDEN LES DADES A UN ARXIU
        call system("rm "//copy_file_path)
        file_path = original_path
        open(100, file = data_path) 
        write(100, nml = parameters)
        write(100, nml = network)
        close(100)

        return
    end 
! %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
!                                         READ_FILE
! %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    subroutine read_file(file_path, data_path)
        implicit none
        character*200 file_path, data_path 
        integer, allocatable :: links(:), degree(:), Pini(:), Pfin(:), replace(:,:)
        integer N, E
        integer i, j
        Namelist/parameters/ N, E 
        Namelist/network/ links, degree, Pini, Pfin

        ! PRIMERA LECURA DEL FITXER
        open(10, file = file_path)
        E = 0
        N = 0
        do 
            read(10, *, END = 10)i, j
            if ((i.ne.0).and.(j.ne.0)) then
                E = E + 1
                if (i.gt.N) then
                    N = i
                elseif (j.gt.N) then
                    N = j
                endif
            endif
        enddo    
    10  close(10)
        allocate(links(1:2*E), degree(1:N), Pini(1:N), Pfin(1:N))

        ! SEGONA LECTURA DEL FITXER
        open(20, file = file_path)
        degree = 0
        do 
            read(20, *, END = 20)i, j
            if ((i.ne.0).and.(j.ne.0)) then
                degree(i) = degree(i) + 1
                degree(j) = degree(j) + 1
            endif
        enddo
    20  close(20)

        ! S'OMPLE EL VECTOR Pini
        Pini(1) = 1
        do i = 2, N
            Pini(i) = Pini(i-1) + degree(i-1)
        enddo     

        ! TERCERA LECTURA DEL FITXER
        Pfin = Pini - 1
        open(30, file = file_path)
        do 
            read(30, *, END = 30)i, j
            if ((i.ne.0).and.(j.ne.0)) then
                Pfin(i) = Pfin(i) + 1
                Pfin(j) = Pfin(j) + 1
                links(Pfin(i)) = j
                links(Pfin(j)) = i
            endif
        enddo
    30  close(30)

    ! ES GUARDEN LES DADES A UN FITXER
        open(40, file = data_path) 
        write(40, nml = parameters)
        write(40, nml = network)
        close(40)

        return
    end
! %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
!                                         GET_FILE_PATH
! %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    function get_file_path(directory)
        implicit none 

        character* 200 get_file_path, directory
        character* 200, allocatable :: files(:)
        integer n_files, i

        ! ARCHIUS EN EL DIRECTORI ACTUAL
    30  call system("ls "//trim(directory)//" > files.txt")

        ! ES GUARDEN ELS NOMS DELS ARXIUS EN UN VECTOR
        open(10, file = "files.txt")
        n_files = 0
            do 
                read(10, *, END = 10)
                n_files = n_files + 1
            enddo
    10  close(10)
        allocate(files(1:n_files))
        open(20, file = "files.txt")
        do i = 1, n_files
            read(20, "(A)", END = 20)files(i)
        enddo
    20  close(20)

        ! ES COMUNICA PER PANTALLA ELS ARXIUS/CARPETES ACCESIBLES
        write(*,*)repeat("-", 76)
        write(*,*)"Els arxius del directori '"//trim(directory)//"' són:"
        write(*,*)repeat("-", 76)
        do i = 1, n_files
            write(*,*)i, trim(files(i))
        enddo
        read(*,*)i
        ! ES MIRA SI LA DIRECCIÓ SELECCIONADA ES UN ARCHIU
        if ((scan(files(i), ".")).ne.0) then
            get_file_path = trim(directory)//trim(files(i))
        ! SI ES SELECCIONA UN DIECTORI ES TORNA REPETIR EL MATEIX PROCES FINS TROBAR UN ARXIU
        else
            directory = trim(directory)//trim(files(i))//"/"
            deallocate(files)
            go to 30
        endif
        call system("rm files.txt")
        return
    end
! %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
!                                         GET_FILE_NAME
! %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    function get_file_name(file_path, file_format)
        implicit none 

        character* 200 get_file_name, file_path
        logical file_format
        integer i

        i = len(trim(file_path))
        do while(file_path(i:i).ne."/") 
            i = i - 1
        enddo
        get_file_name = file_path(i + 1:len(trim(file_path)))

        if (file_format.eqv..FALSE.) then
            i = len(trim(get_file_name))
            do while(get_file_name(i:i).ne.".") 
                i = i - 1
            enddo
            get_file_name = get_file_name(1:i - 1)
        endif
        return
    end
! %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
!                                         GET_PC
! %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    subroutine get_Pc(data_path)
        implicit none
        
        character*200 data_path, file_path 
        integer, allocatable :: links(:), degree(:), Pini(:), Pfin(:)
        integer N, E, N_k
        integer i, j
        integer, allocatable :: k(:), count_k(:)
        real*8, allocatable :: Prob_k(:), Pc(:)
        Namelist/parameters/ N, E 
        Namelist/network/ links, degree, Pini, Pfin 

    ! LLECTURA DE LES DADES 
        open(10, file = data_path)
        read(unit = 10, nml = parameters) 
        allocate(links(1:2*E), degree(1:N), Pini(1:N), Pfin(1:N))
        read(unit = 10, nml = network)
        close(10)

    ! ES CALCULA LA PROBABILITAT DE CADA DEGREE
        call value_count(degree, count_k, k) 
        N_k = size(k)
        allocate(Prob_k(1:N_k))
        Prob_k = real(count_k)/N
        
    ! ES CALCULA LA PROBABILITAT ACUMULADA DE CADA DEGREE
        allocate(Pc(1:N_k))
        do i = 1, N_k
            Pc(i) = Prob_k(i)
            do j = 1, N_k 
                if (k(j).gt.k(i)) then
                    Pc(i) = Pc(i) + Prob_k(j)
                endif
            enddo 
        enddo

    
        file_path = "Propietats/"//get_file_name(data_path, .FALSE.)
        write(*,*)file_path
        file_path = trim(file_path)//"__Pc.txt"
        open(20, file = file_path)
        do i = 1, N_k
            write(20,"(I0,X,F20.18)")k(i), Prob_k(i)
        enddo
        
        close(20)

        return
    end
! %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
!                                        GET_KNN
! %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    subroutine get_Knn(data_path)
        implicit none
        
        character*200 data_path, file_path 
        integer, allocatable :: links(:), degree(:), Pini(:), Pfin(:)
        
        integer N, E, N_k
        integer i, j, sumint
        real*8 sumreal
        integer, allocatable :: k(:), count_k(:)
        real*8, allocatable :: mean_degree(:), Knn(:)
        Namelist/parameters/ N, E 
        Namelist/network/ links, degree, Pini, Pfin 

        ! LLECTURA DE LES DADES 
        open(10, file = data_path)
        read(unit = 10, nml = parameters) 
        allocate(links(1:2*E), degree(1:N), Pini(1:N), Pfin(1:N))
        read(unit = 10, nml = network)
        close(10)

        ! CÀLCUL DE MEAN_DEGREE
        allocate(mean_degree(1:N))
        do i = 1, N
            sumint = degree(i)
            do j = Pini(i), Pfin(i)
                sumint = sumint + degree(links(j))
            enddo
            mean_degree(i) = real(sumint)/degree(i)
        enddo

        ! CÀLCUL DE ACUMULATE_DEGREE
        call value_count(degree, count_k, k) 
        N_k = size(k)
        allocate(Knn(1:N_k))
        do i = 1, N_k
            Knn(i) = 0.d0
            do j = 1, N
                if (k(i).eq.degree(j)) then
                Knn(i) = Knn(i) + mean_degree(j)
                endif
            enddo
            Knn(i) = Knn(i)/count_k(i)
        enddo

        file_path = "Propietats/"//get_file_name(data_path, .FALSE.)
        file_path = trim(file_path)//"__Knn.txt"
        open(20, file = file_path )
        do i = 1, N_k
        write(20, "(I0, X, F8.4)")k(i), Knn(i)
        enddo
        close(20)
        return
    end   

! %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
!                                          VALUE_COUNT
! %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    subroutine value_count(vector, counter, values)
        implicit none
        integer dim, i
        integer, allocatable :: counter(:), values(:), vector(:)

        dim = size(vector)
        allocate(counter(1:1), values(1:1))
        do i = 1, dim
            if (i.eq.1) then
                counter(1) = 1
                values(1) = vector(i)
            elseif (all(values.ne.vector(i))) then
                call append_int(counter, 1)
                call append_int(values, vector(i))
            else
                counter(findloc(values, vector(i))) = counter(findloc(values, vector(i))) + 1
            endif
        enddo
        return
    end

! %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
!                                         APPEND_INT
! %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    subroutine append_int(vector, new_number)
        implicit none

        integer new_number, dim
        integer, allocatable :: vector(:), support_vector(:)
    
        dim = size(vector)
        allocate(support_vector(1:dim))
        support_vector = vector
        deallocate(vector)
        allocate(vector(1:dim + 1))
        vector(1:dim) = support_vector
        vector(dim + 1) = new_number

        return
    end
! %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
!                                         APPEND_REAL
! %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    subroutine append_real(vector, new_number)
        implicit none

        real*8 new_number
        integer  dim
        real*8, allocatable :: vector(:), support_vector(:)

        dim = size(vector)
        allocate(support_vector(1:dim))
        support_vector = vector
        deallocate(vector)
        allocate(vector(1:dim + 1))
        vector(1:dim) = support_vector
        vector(dim + 1) = new_number

        return
    end
! %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
!                                         APPEND_ROW
! %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    subroutine append_row(array, rows_array, cols_array, row)
        implicit none
        integer, allocatable :: array(:,:)
        integer cols_array, rows_array
        integer support_array(1:rows_array, 1:cols_array), row(1:cols_array)
        integer i, j

        support_array = array
        deallocate(array)
        allocate(array(1:rows_array + 1, 1:cols_array))
        do i = 1, rows_array + 1
            do j = 1, cols_array
                if (i.eq.(rows_array + 1)) then
                    array(i,j) = row(j)
                else
                    array(i,j) = support_array(i,j)
                endif
            enddo
        enddo

        return
    end
! %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
!                                         REMOVE_INT
! %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    subroutine remove_int(vector, position)
        implicit none

        integer dim, position
        integer, allocatable :: vector(:), support_vector(:)

        dim = size(vector)
        allocate(support_vector(1:dim))
        support_vector = vector
        deallocate(vector)
        allocate(vector(1:dim - 1))
        vector(1:position - 1) = support_vector(1:position - 1)
        vector(position:) = support_vector(position + 1:)
        return
    end
! %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
!                                         DELETE_INT
! %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    subroutine delete_int(vector, int)
        implicit none

        integer int, i
        integer, allocatable :: vector(:), support_vector(:)

        call remove_int(vector, findloc(vector, int, dim = 1))
        return
    end
! %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
!                                         RM_REPETITION
! %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    subroutine rm_repetition_int(vector)
        implicit none

        integer, allocatable :: vector(:), counter(:), values(:)
        integer i, j, actual

        call value_count(vector, counter, values)
        do i = 1, size(values)
            if (counter(i).ne.1) then
                actual = values(i)
                do j = 1, counter(i) - 1
                    call delete_int(vector, actual)
                enddo
            endif
        enddo 

        return
    end

! %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
!                       GENERADOR NUMEROS ALEATORIS      
! %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

!  A C-program for MT19937, with initialization improved 2002/1/26.
!  Coded by Takuji Nishimura and Makoto Matsumoto.

!  Before using, initialize the state by using init_genrand(seed)  
!  or init_by_array(init_key, key_length).

!  Copyright (C) 1997 - 2002, Makoto Matsumoto and Takuji Nishimura,
!  All rights reserved.                          
!  Copyright (C) 2005, Mutsuo Saito,
!  All rights reserved.                          

!  Redistribution and use in source and binary forms, with or without
!  modification, are permitted provided that the following conditions
!  are met:

!    1. Redistributions of source code must retain the above copyright
!       notice, this list of conditions and the following disclaimer.

!    2. Redistributions in binary form must reproduce the above copyright
!       notice, this list of conditions and the following disclaimer in the
!       documentation and/or other materials provided with the distribution.

!    3. The names of its contributors may not be used to endorse or promote 
!       products derived from this software without specific prior written 
!       permission.

!  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
!  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
!  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
!  A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
!  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
!  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
!  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
!  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
!  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
!  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
!  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


!  Any feedback is very welcome.
!  http://www.math.sci.hiroshima-u.ac.jp/~m-mat/MT/emt.html
!  email: m-mat @ math.sci.hiroshima-u.ac.jp (remove space)

!-----------------------------------------------------------------------
!  FORTRAN77 translation by Tsuyoshi TADA. (2005/12/19)

!     ---------- initialize routines ----------
!  subroutine init_genrand(seed): initialize with a seed
!  subroutine init_by_array(init_key,key_length): initialize by an array

!     ---------- generate functions ----------
!  integer function genrand_int32(): signed 32-bit integer
!  integer function genrand_int31(): unsigned 31-bit integer
!  double precision function genrand_real1(): [0,1] with 32-bit resolution
!  double precision function genrand_real2(): [0,1) with 32-bit resolution
!  double precision function genrand_real3(): (0,1) with 32-bit resolution
!  double precision function genrand_res53(): (0,1) with 53-bit resolution

!  This program uses the following non-standard intrinsics.
!    ishft(i,n): If n>0, shifts bits in i by n positions to left.
!                If n<0, shifts bits in i by n positions to right.
!    iand (i,j): Performs logical AND on corresponding bits of i and j.
!    ior  (i,j): Performs inclusive OR on corresponding bits of i and j.
!    ieor (i,j): Performs exclusive OR on corresponding bits of i and j.

!-----------------------------------------------------------------------
!     initialize mt(0:N-1) with a seed
!-----------------------------------------------------------------------
    subroutine init_genrand(s)
      integer s
      integer N
      integer DONE
      integer ALLBIT_MASK
      parameter (N=624)
      parameter (DONE=123456789)
      integer mti,initialized
      integer mt(0:N-1)
      common /mt_state1/ mti,initialized
      common /mt_state2/ mt
      common /mt_mask1/ ALLBIT_MASK

      call mt_initln
      mt(0)=iand(s,ALLBIT_MASK)
      do 100 mti=1,N-1
        mt(mti)=1812433253*ieor(mt(mti-1),ishft(mt(mti-1),-30))+mti
        mt(mti)=iand(mt(mti),ALLBIT_MASK)
  100 continue
      initialized=DONE

      return
      end
!-----------------------------------------------------------------------
!     initialize by an array with array-length
!     init_key is the array for initializing keys
!     key_length is its length
!-----------------------------------------------------------------------
      subroutine init_by_array(init_key,key_length)
      integer init_key(0:*)
      integer key_length
      integer N
      integer ALLBIT_MASK
      integer TOPBIT_MASK
      parameter (N=624)
      integer i,j,k
      integer mt(0:N-1)
      common /mt_state2/ mt
      common /mt_mask1/ ALLBIT_MASK
      common /mt_mask2/ TOPBIT_MASK

      call init_genrand(19650218)
      i=1
      j=0
      do 100 k=max(N,key_length),1,-1
        mt(i)=ieor(mt(i),ieor(mt(i-1),ishft(mt(i-1),-30))*1664525)+init_key(j)+j
        mt(i)=iand(mt(i),ALLBIT_MASK)
        i=i+1
        j=j+1
        if(i.ge.N)then
          mt(0)=mt(N-1)
          i=1
        endif
        if(j.ge.key_length)then
          j=0
        endif
  100 continue
      do 200 k=N-1,1,-1
        mt(i)=ieor(mt(i),ieor(mt(i-1),ishft(mt(i-1),-30))*1566083941)-i
        mt(i)=iand(mt(i),ALLBIT_MASK)
        i=i+1
        if(i.ge.N)then
          mt(0)=mt(N-1)
          i=1
        endif
  200 continue
      mt(0)=TOPBIT_MASK

      return
      end
!-----------------------------------------------------------------------
!     generates a random number on [0,0xffffffff]-interval
!-----------------------------------------------------------------------
      function genrand_int32()
      integer genrand_int32
      integer N,M
      integer DONE
      integer UPPER_MASK,LOWER_MASK,MATRIX_A
      integer T1_MASK,T2_MASK
      parameter (N=624)
      parameter (M=397)
      parameter (DONE=123456789)
      integer mti,initialized
      integer mt(0:N-1)
      integer y,kk
      integer mag01(0:1)
      common /mt_state1/ mti,initialized
      common /mt_state2/ mt
      common /mt_mask3/ UPPER_MASK,LOWER_MASK,MATRIX_A,T1_MASK,T2_MASK
      common /mt_mag01/ mag01

      if(initialized.ne.DONE)then
        call init_genrand(21641)
      endif

      if(mti.ge.N)then
        do 100 kk=0,N-M-1
          y=ior(iand(mt(kk),UPPER_MASK),iand(mt(kk+1),LOWER_MASK))
          mt(kk)=ieor(ieor(mt(kk+M),ishft(y,-1)),mag01(iand(y,1)))
  100   continue
        do 200 kk=N-M,N-1-1
          y=ior(iand(mt(kk),UPPER_MASK),iand(mt(kk+1),LOWER_MASK))
          mt(kk)=ieor(ieor(mt(kk+(M-N)),ishft(y,-1)),mag01(iand(y,1)))
  200   continue
        y=ior(iand(mt(N-1),UPPER_MASK),iand(mt(0),LOWER_MASK))
        mt(kk)=ieor(ieor(mt(M-1),ishft(y,-1)),mag01(iand(y,1)))
        mti=0
      endif

      y=mt(mti)
      mti=mti+1

      y=ieor(y,ishft(y,-11))
      y=ieor(y,iand(ishft(y,7),T1_MASK))
      y=ieor(y,iand(ishft(y,15),T2_MASK))
      y=ieor(y,ishft(y,-18))

      genrand_int32=y
      return
      end
!-----------------------------------------------------------------------
!     generates a random number on [0,0x7fffffff]-interval
!-----------------------------------------------------------------------
      function genrand_int31()
      integer genrand_int31
      !integer genrand_int32
      genrand_int31=int(ishft(genrand_int32(),-1))
      return
      end
!-----------------------------------------------------------------------
!     generates a random number on [0,1]-real-interval
!-----------------------------------------------------------------------
      function genrand_real1()
      double precision genrand_real1,r
      !integer genrand_int32
      r=dble(genrand_int32())
      if(r.lt.0.d0)r=r+2.d0**32
      genrand_real1=r/4294967295.d0
      return
      end
!-----------------------------------------------------------------------
!     generates a random number on [0,1)-real-interval
!-----------------------------------------------------------------------
      function genrand_real2()
      double precision genrand_real2,r
      !integer genrand_int32
      r=dble(genrand_int32())
      if(r.lt.0.d0)r=r+2.d0**32
      genrand_real2=r/4294967296.d0
      return
      end
!-----------------------------------------------------------------------
!     generates a random number on (0,1)-real-interval
!-----------------------------------------------------------------------
      function genrand_real3()
      double precision genrand_real3,r
      !integer genrand_int32
      r=dble(genrand_int32())
      if(r.lt.0.d0)r=r+2.d0**32
      genrand_real3=(r+0.5d0)/4294967296.d0
      return
      end
!-----------------------------------------------------------------------
!     generates a random number on [0,1) with 53-bit resolution
!-----------------------------------------------------------------------
      function genrand_res53()
      double precision genrand_res53
      !integer genrand_int32
      double precision a,b
      a=dble(ishft(genrand_int32(),-5))
      b=dble(ishft(genrand_int32(),-6))
      if(a.lt.0.d0)a=a+2.d0**32
      if(b.lt.0.d0)b=b+2.d0**32
      genrand_res53=(a*67108864.d0+b)/9007199254740992.d0
      return
      end
!-----------------------------------------------------------------------
!     initialize large number (over 32-bit constant number)
!-----------------------------------------------------------------------
      subroutine mt_initln()
      integer ALLBIT_MASK
      integer TOPBIT_MASK
      integer UPPER_MASK,LOWER_MASK,MATRIX_A,T1_MASK,T2_MASK
      integer mag01(0:1)
      common /mt_mask1/ ALLBIT_MASK
      common /mt_mask2/ TOPBIT_MASK
      common /mt_mask3/ UPPER_MASK,LOWER_MASK,MATRIX_A,T1_MASK,T2_MASK
      common /mt_mag01/ mag01
!!    TOPBIT_MASK = Z'80000000'
!!    ALLBIT_MASK = Z'ffffffff'
!!    UPPER_MASK  = Z'80000000'
!!    LOWER_MASK  = Z'7fffffff'
!!    MATRIX_A    = Z'9908b0df'
!!    T1_MASK     = Z'9d2c5680'
!!    T2_MASK     = Z'efc60000'
      TOPBIT_MASK=1073741824
      TOPBIT_MASK=ishft(TOPBIT_MASK,1)
      ALLBIT_MASK=2147483647
      ALLBIT_MASK=ior(ALLBIT_MASK,TOPBIT_MASK)
      UPPER_MASK=TOPBIT_MASK
      LOWER_MASK=2147483647
      MATRIX_A=419999967
      MATRIX_A=ior(MATRIX_A,TOPBIT_MASK)
      T1_MASK=489444992
      T1_MASK=ior(T1_MASK,TOPBIT_MASK)
      T2_MASK=1875247104
      T2_MASK=ior(T2_MASK,TOPBIT_MASK)
      mag01(0)=0
      mag01(1)=MATRIX_A
      return
      end

end module NetworkEncoder