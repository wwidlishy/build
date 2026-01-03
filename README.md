# build
simple build system for any language

# modules
A module is a folder in the `modules` which doesnt have any subfolders

# creating a new project
1. cd into a directory
2. create directories 'modules' and 'build'
3. create 'buildfile'
```asm
?cc gcc ; compiler path
?ld gcc $I -o $O ; link command ($I is input and $O is output)
  
?in .c ; extenstion of files
?out a.out ; output of build system
  
main -c $I -o $O ; compile command for 'main' module
```

# macros
```
?cc gcc ; compiler path
?ld gcc $I -o $O ; link command ($I is input and $O is output)
  
?in .c ; extenstion of files
?out a.out ; output of build system

?macro args -c $I -o $O ; macro named args

some_module $args
another_module $args
main $args -Imodules/some_module -Imodules/another_module ; compile command for 'main' module
```

# building
1. runing `build` without any arguments links all the files in build together
```
D:\test>build
[LINK]
gcc "build/m_main main main.o" "build/m_include include my_math.o" -o "a.exe"
```
2. argument `*` builds all files from all modules
```
D:\test>build *
[BUILD] *
building: main/main.c
gcc -c "modules/main/main.c" -o "build/m_main main main.o" -Imodules/include/
building: include/my_math.c
gcc -c "modules/include/my_math.c" -o "build/m_include include my_math.o"
[LINK]
gcc "build/m_main main main.o" "build/m_include include my_math.o" -o "a.exe"
```
3. or you can build a single module by typing its name
```
D:\test>build include
[BUILD] include
building: include/my_math.c
gcc -c "modules/include/my_math.c" -o "build/m_include include my_math.o"
[LINK]
gcc "build/m_main main main.o" "build/m_include include my_math.o" -o "a.exe"
```
4. or a single file in a module
```
D:\test>build include/my_math.c
[BUILD] include/my_math.c
building: include/my_math.c
gcc -c "modules/include/my_math.c" -o "build/m_include include my_math.o"
[LINK]
gcc "build/m_main main main.o" "build/m_include include my_math.o" -o "a.exe"
```
5. you can chain arguments
```
D:\test>build include/my_math.c some_module main
[BUILD] include/my_math.c
building: include/my_math.c
gcc -c "modules/include/my_math.c" -o "build/m_include include my_math.o"
[BUILD] some_module
building: some_module/a.c
gcc -c "modules/some_module/a.c" -o "build/m_some_module some_module a.o"
[BUILD] main
building: main/main.c
gcc -c "modules/main/main.c" -o "build/m_main main main.o" -Imodules/include/
[LINK]
gcc "build/m_main main main.o" "build/m_some_module some_module a.o" "build/m_include include my_math.o" -o "a.exe"
```
