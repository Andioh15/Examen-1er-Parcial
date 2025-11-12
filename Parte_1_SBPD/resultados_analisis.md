Análisis de Resultados - Parte 1: Procesos vs. Hilos

1. Tareas Procesadas

Se generaron y procesaron 20 tareas con dificultades asignadas aleatoriamente (1 a 5).

Contexto de la Tarea: La tarea process_task es de tipo I/O Bound (limitada por I/O), ya que utiliza time.sleep(difficulty * 0.3) para simular la carga de trabajo, lo que significa que pasa la mayor parte del tiempo esperando.

2. Tiempos de Ejecución

Los tiempos de ejecución obtenidos en la segunda corrida exitosa fueron los siguientes:

Mecanismo                    Tiempo Total

Hilos (Threading)           1.5035 segundos

Procesos (Multiprocessing)  1.9840 segundos

3. Conclusiones y Recomendaciones

A. Rendimiento (Hilos vs. Procesos)

La ejecución con Hilos fue significativamente más rápida (aproximadamente un 24% más rápido) que la ejecución con Procesos.

Razón del Rendimiento de Hilos: En Python (CPython), cuando un hilo encuentra una operación de bloqueo de I/O (como time.sleep), el Global Interpreter Lock (GIL) se libera temporalmente. Esto permite que el sistema operativo programe y ejecute otro hilo de Python, incluso si este último también está haciendo I/O. Esto maximiza la concurrencia en tareas que pasan mucho tiempo esperando.

Razón del Rendimiento de Procesos: Aunque los Procesos superan al GIL y son ideales para tareas intensivas en CPU (CPU-Bound), tienen un mayor overhead de inicio. Crear un nuevo proceso requiere que el sistema operativo asigne un nuevo espacio de memoria y recursos, un costo que no vale la pena para tareas cortas y limitadas por I/O.

B. Mecanismos de Sincronización

La sincronización fue crucial para asegurar que el contador de tareas completadas (tasks_completed_...) fuera preciso, evitando condiciones de carrera.

Mecanismo                       Objeto de Sincronización

Hilos (Threading)                    threading.Lock()

Procesos (Multiprocessing) multiprocessing.Value().get_lock()

Explicación de Hilos: Se utilizó threading.Lock() para garantizar la exclusión mutua en la sección crítica donde se incrementa la variable. Solo el hilo que adquiere el lock puede modificar el contador, asegurando la consistencia de los datos en la memoria compartida.

Explicación de Procesos: Se utilizó multiprocessing.Value('i', 0) para crear un contador en memoria compartida. El método .get_lock() asociado a esta variable asegura que, aunque los procesos operan en espacios de memoria separados, la actualización de ese valor compartido se realiza de forma atómica y segura.

Recomendación

Se recomienda utilizar Hilos para tareas de procesamiento distribuido que impliquen latencia de red, lecturas de archivos o, en este caso, pausas por tiempo (I/O-Bound). Los Procesos solo serían la mejor opción si la tarea fuera CPU-Bound (ej. cálculo matricial complejo o criptografía).