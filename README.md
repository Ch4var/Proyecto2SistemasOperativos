# Autores, Curso y Sede
**Instituto Tecnológico de Costa Rica**
*Principios de Sistemas Operativos. Grupo 40*
Integrantes:
*    Sergio Chavarría Avilés- 2021077879 - Centro Académico de Alajuela
*    José Ignacio Sánchez Morales- 2022081784 - Centro Académico Local San José
*    Adrián Josué Vega Barrantes- 2022104007 - Centro académico Local San José

Profesor:
*    Rodolfo Mora Zamora 

## Tabla de contenidos
- [Descripción](#Descripción)
- [Compilación](#Compilación)

# Descripción:

Este proyecto consiste en la programación del algoritmo de Huffman en el lenguaje de programación C. Esto con el objetivo de comprimir 100 libros en formato de texto plano obtenidos del Gutenberg y luego descomprimirlos volviendo a generar los 100 libros originales. Para esto se programaron 3 versiones de compresión y 3 versiones de descompresión. Para la compresión y descompresión se programó una versión serial, una versión paralela utilizando fork y una versión concurrente utilizando pthreads. Esto con el objetivo de poder ver la mejora en el tiempo de ejecución entre las versiones.

# Compilación:
Para poder ejecutar el código en el ambiente Fedora Worktstation 40 es necesario instalar la versión más reciente de Python a través del siguiente comando:  
    
$ sudo dnf install python3

Una vez instalado la última versión de Python, es necesario instalar la biblioteca de interfaz gráfica Tkinter, esencial para el proyecto, con el siguiente comando:
    
$ sudo dnf install python3-tkinter

Una vez realizadas ejecutados ambos comandos, se ejecuta el siguiente comando para otorgarle permisos al programa que contiene el código de ejecución del programa:

$ chmod +x main.py

Finalmente, para ejecutar el programa, se ejecuta el siguiente comando:

 $ python main.py
