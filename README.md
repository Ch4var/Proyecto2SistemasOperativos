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

Este proyecto consiste en la programación 5 algoritmos de paginación y el impacto que pueden tener en el rendimiento de un sistema operativo doméstico. La simulación consiste en la ejecución de dos algoritmos en simultáneo, el algoritmo óptimo y el algoritmo seleccionado por el usuario, sobre líneas de código que pueden ser cargadas en un archivo, o ser generadas por el mismo programa. Además, el usuario debe agregar la semilla para la ejecución del programa, tiene la opción de cargar un archivo para la lectura de las operaciones, y si no fuera a cargar un archivo, debe seleccionar la cantidad de operaciones y la cantidad de líneas de operaciones que quiere que ambos algoritmos ejecuten. También, tiene la posibilidad de descargar un archivo con la cantidad de operaciones y la cantidad de líneas de operaciones seleccionadas. Luego de esta selección, se va a visualizar la ejecución de ambos algoritmos sobre las operaciones, donde va a tener la opción de pausar la simulación. 

# Compilación:
Para poder ejecutar el código en el ambiente Fedora Worktstation 40 es necesario instalar la versión más reciente de Python a través del siguiente comando:  
    
$ sudo dnf install python3

Una vez instalado la última versión de Python, es necesario instalar la biblioteca de interfaz gráfica Tkinter, esencial para el proyecto, con el siguiente comando:
    
$ sudo dnf install python3-tkinter

Una vez realizadas ejecutados ambos comandos, se ejecuta el siguiente comando para otorgarle permisos al programa que contiene el código de ejecución del programa:

$ chmod +x main.py

Finalmente, para ejecutar el programa, se ejecuta el siguiente comando:

 $ python main.py
