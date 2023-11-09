# How to build Fortran modules for Python
Docker takes care of installing Fortran in the app container. To build a Python-readable file from a Fortran script, it's necessary to run the following command inside the app container ([How to Enter Into a Docker Container's Shell?](https://kodekloud.com/blog/docker-exec/#){:target="_blank"}).
<div class="annotate" markdown>
```
f2py -c <fortran-file-path> -m <module-path> (1)
```
</div>

1. ❗ `module-path` must be formated with "." instead of "/" 
   ✨ Example -> dir1.dir2.module_name

### Fortran script estructure
```fortran
subroutine subroutineName(input1, input2, output1)
    
    integer, intent(in) :: input1, input2
    integer, intent(out) :: output1
    
    output1 = input1 + input2
    
end subroutine subroutineName
```
Once a Fortran module is created, you can access its functions as you would with a regular Python module.