! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
! ///////////////////////////////////READ_NETWORK//////////////////////////////////
! %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
subroutine read_network(network_path, N, E, links_out, degree_out, Pini_out, Pfin_out, Emax)
    implicit none
    ! VARIABLES LECTURA INICAL
    character*300, intent(in) :: network_path
    integer, intent(in) :: Emax
    integer, intent(out) :: N, E
    integer, intent(out) :: links_out(1:2*Emax), degree_out(1:2*Emax), Pini_out(1:2*Emax), Pfin_out(1:2*Emax)
    integer, allocatable :: links(:), degree(:), Pini(:), Pfin(:)
    Namelist/parameters/ N, E 
    Namelist/network/ links, degree, Pini, Pfin

    ! VARIABLES NODES CONSECUTIUS
    character*200 aux_path, aux_copy_path
    integer, allocatable :: labels(:)
    integer i, j

    !VARIABLES LINKS REPETITS
    integer k, candidate

! --------------------------------------------------------------------------------------------
    ! LECTURA INICIAL DE L'ARXIU ABANS D'ANALITZAR SI FA FALTA ALGUN CANVI
    aux_path = "aux.dat"
    call read_file(network_path, aux_path)

    ! LLECTURA DE LES DADES 
    open(50, file = aux_path)
    read(unit = 50, nml = parameters) 
    allocate(links(1:2*E), degree(1:N), Pini(1:N), Pfin(1:N))
    read(unit = 50, nml = network)
    close(50)

    ! write(*,*)repeat("%&", 38)
    ! write(*,*)"#Mirando si los nodos són consecutivos"
    ! MIRAR SI ELS NODES SON CONSECUTIUS
    allocate(labels(1:N))
    N = 0
    do i = 1, size(degree)
        if (degree(i).ne.0) then
            N = N + 1
            labels(i) = N
        endif
    enddo 
    ! write(*,*)repeat("%&", 38)
    ! write(*,*)"#Nodos consecutivos DONE"
        
    ! ES FA UNA CÒPIA DE L'ARXIU ORIGINAL REETIQUETANT ELS NODES QUE NO ESTAN EN ORDRE CONSECUTIU
    aux_copy_path = "aux_copy.txt"
    ! write(*,*)repeat("%&", 38)
    ! write(*,*)"#Reetiquetando"
    open(70, file = network_path)
    open(80, file = aux_copy_path)
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
    ! write(*,*)repeat("%&", 38)
    ! write(*,*)"#Reetiquetado DONE"
        
    ! SEGONA LECTURA DE L'ARXIU HAVENT RESOLT EL PROBLEMA DE LES ETIQUETES
    call read_file(aux_copy_path, aux_path)

    ! LLECTURA DE LES DADES DE LA COPIA CORREGIDA
    open(90, file = aux_path)
    read(unit = 90, nml = parameters) 
    deallocate(links, degree, Pini, Pfin)
    allocate(links(1:2*E), degree(1:N), Pini(1:N), Pfin(1:N))
    read(unit = 90, nml = network)
    close(90)

    ! write(*,*)repeat("%&", 38)
    ! write(*,*)"#Mirando si los links se repiten"
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
        ! write(*,*)"Revisados ", i, "nodos de ", N
    enddo
    ! write(*,*)repeat("%&", 38)
    ! write(*,*)"#Links repetidos DONE"
    ! write(*,*)repeat("%&", 38)
    E = size(links)/2
    
    ! UN COP S'HAN CORREGUIT ELS POSIBLES ERRORS DE LA XARXA, ES GUARDEN LES DADES A UN ARXIU
    call system("rm "//aux_path)
    call system("rm "//aux_copy_path)
    links_out(:2*E) = links
    degree_out(:N) = degree
    Pini_out(:N) = Pini
    Pfin_out(:N) = Pfin
    contains
! %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
!                                         READ_FILE
! %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    subroutine read_file(file_path, data_path)
        implicit none
        character*200 file_path, data_path 
        integer, allocatable :: links(:), degree(:), Pini(:), Pfin(:)
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

    end subroutine read_file

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

    end subroutine remove_int

end subroutine read_network
