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

Este proyecto consiste en la programación 5 algoritmos de paginación y el impacto que pueden tener en el rendimiento de un sistema operativo doméstico. La simulación consiste en la ejecución de dos algoritmos en simultáneo, el algoritmo óptimo y el algoritmo seleccionado por el usuario (FIFO, Second Chance, MRU, y Random), sobre líneas de código que pueden ser cargadas en un archivo, o ser generadas por el mismo programa. Además, el usuario debe agregar la semilla para la ejecución del programa, tiene la opción de cargar un archivo para la lectura de las operaciones, y si no fuera a cargar un archivo, debe seleccionar la cantidad de operaciones y la cantidad de líneas de operaciones que quiere que ambos algoritmos ejecuten. También, tiene la posibilidad de descargar un archivo con la cantidad de operaciones y la cantidad de líneas de operaciones seleccionadas. Luego de esta selección, se va a visualizar la ejecución de ambos algoritmos sobre las operaciones, donde va a tener la opción de pausar la simulación. 

# Compilación:
Para poder ejecutar el código en el ambiente Fedora Worktstation 40 es necesario darle permisos al archivo llamado setup.sh, el cual es un script que se encarga de instalar la biblioteca de interfaz gráfica Tkinter, esencial para este proyecto, y de otorgarle permisos al programa necesario para la ejecución del programa. Esto se logra abriendo una terminal donde se encuentra el proyecto y ejecutando el siguiente comando: 

$ chmod +x setup.sh

Una vez se le dieron los permisos al archivo se ejecuta el mismo de la siguiente manera:

$ ./setup.sh

Deberá ingresar su contraseña y presionar la tecla enter para que comience la instalación de la biblioteca. Finalmente, para ejecutar el programa, se ejecuta el siguiente comando:

$ python main.py
