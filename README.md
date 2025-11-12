Examen Práctico - Sistemas Distribuidos

Este repositorio contiene la solución para las dos partes del examen práctico:

Parte 1: Sistema Básico de Procesamiento Distribuido (Hilos vs. Procesos).

Parte 2: Sistema de Almacenamiento Distribuido (Docker y MongoDB Sharding).

💾 Parte 1: Análisis de Resultados (Hilos vs. Procesos)

Se procesaron 20 tareas con dificultades variadas (1 a 5) en un entorno de I/O Bound (simulado con time.sleep).

📊 Tiempos de Ejecución Obtenidos

Enfoque                  Tiempo Total
Hilos (Threading)          1.5035s

Procesos (Multiprocessing) 1.9840s

Conclusiones sobre Rendimiento

Los Hilos (Threading) resultaron ser el mecanismo más rápido con un tiempo de 1.5035s, superando a los Procesos (1.9840s).

Razón: La tarea es de tipo I/O Bound (limitada por entrada/salida, en este caso, por espera time.sleep). En Python, cuando un Hilo entra en estado de espera (I/O), el Global Interpreter Lock (GIL) se libera, permitiendo que otro hilo de Python se ejecute. Los Procesos, en cambio, tienen un alto overhead al iniciar (crear un nuevo espacio de memoria completo) y al comunicarse, lo que penaliza el rendimiento en tareas que no son intensivas en CPU.

Explicación de Mecanismos de Sincronización

Para evitar las condiciones de carrera al actualizar el contador de tareas completadas:

En Hilos: Se utilizó threading.Lock() para garantizar la exclusión mutua. El hilo debe adquirir el lock antes de modificar la variable compartida (tasks_completed_threads) y liberarlo al terminar.

En Procesos: Se utilizó multiprocessing.Value('i', 0) con su mecanismo de bloqueo integrado (.get_lock()). Dado que los procesos no comparten memoria, multiprocessing.Value proporciona un segmento de memoria compartida seguro, y su lock es esencial para sincronizar el acceso entre los diferentes espacios de memoria de los procesos.

🐳 Parte 2: Almacenamiento Distribuido (Docker y MongoDB)

El sistema utiliza Docker Compose para levantar tres servicios: dos nodos de MongoDB y un contenedor para la aplicación Python que implementa la lógica de sharding.

Arquitectura

Nodos MongoDB: mongo1 (Puerto 27017) y mongo2 (Puerto 27018).

Aplicación: storage_app (Contenedor Python con sistema_almacenamiento.py).

Sharding: Se utiliza una función de hash (hashlib.md5) basada en el ID del documento para decidir consistentemente si debe ir al nodo 1 o al nodo 2. Esto garantiza una distribución cercana al 50/50.

Instrucciones de Ejecución Paso a Paso

Requisitos: Tener Docker y Docker Compose instalados y en ejecución.

Archivos: Asegurarse de que docker-compose.yml, sistema_almacenamiento.py, y Dockerfile estén en sus ubicaciones correctas.

Compilación: Desde la raíz del proyecto (Examen 1er Parcial), ejecutar el comando para construir la imagen de la aplicación y levantar todos los servicios:

docker-compose up --build -d


Ver Resultados: Para ver la salida de la aplicación (conexión, inserciones distribuidas y estadísticas):

docker logs distributed_app


Detener: Para detener y eliminar los contenedores y liberar los puertos:

docker-compose down