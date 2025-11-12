import multiprocessing
import threading
import time
import random
from typing import List, Tuple, Any

# Define la estructura de las tareas: (task_id, difficulty)
Task = Tuple[int, int]

class TaskProcessor:
    """
    Clase que gestiona la ejecución de tareas usando hilos y procesos para comparar su rendimiento.
    """
    def __init__(self):
        # Contador compartido para PROCESOS (usa multiprocessing.Value)
        self.tasks_completed_processes: multiprocessing.Value = multiprocessing.Value('i', 0)
        
        # Contador y Lock para HILOS (usa threading.Lock y variable normal)
        self.tasks_completed_threads: int = 0
        self.thread_lock: threading.Lock = threading.Lock()
        
    def process_task(self, task_id: int, difficulty: int) -> int:
        """
        Simula el procesamiento de una tarea con diferente dificultad.
        
        Dificultad 1 (Fácil): 0.3 segundos
        Dificultad 5 (Difícil): 1.5 segundos
        """
        print(f"Iniciando Tarea {task_id} (Dificultad: {difficulty}) [cite: 99]")
        
        # La dificultad determina el tiempo de procesamiento [cite: 100, 102]
        processing_time: float = difficulty * 0.3
        time.sleep(processing_time) # Simula trabajo (I/O Bound) [cite: 103]
        
        # Resultado basado en dificultad [cite: 105]
        result: int = task_id * difficulty
        print(f"Tarea {task_id} completada. Resultado: {result} [cite: 106]")
        return result

    # --- Funciones Worker para Hilos y Procesos ---

    def _worker_thread(self, task_id: int, difficulty: int):
        """Función worker que se ejecuta en cada HILO."""
        self.process_task(task_id, difficulty)
        
        # Usar Lock para evitar condiciones de carrera en el contador compartido (Requisito 2) [cite: 112]
        with self.thread_lock:
            self.tasks_completed_threads += 1

    @staticmethod
    def _worker_process(task_id: int, difficulty: int, tasks_completed_counter: multiprocessing.Value):
        """Función worker que se ejecuta en cada PROCESO."""
        # Simular procesamiento de tarea
        print(f"Iniciando Tarea {task_id} (Dificultad: {difficulty}) [cite: 99]")
        processing_time: float = difficulty * 0.3
        time.sleep(processing_time)
        result: int = task_id * difficulty
        print(f"Tarea {task_id} completada. Resultado: {result} [cite: 106]")
        
        # Usar Lock de multiprocessing.Value para evitar condiciones de carrera (Requisito 3) [cite: 116]
        with tasks_completed_counter.get_lock():
            tasks_completed_counter.value += 1


    # --- Implementaciones de Ejecución ---

    def run_with_threads(self, tasks: List[Task]) -> float:
        """Ejecutar tareas usando HILOS (comparte memoria) [cite: 25]"""
        print("\n--- Ejecución con HILOS (Threading) ---")
        
        start_time = time.time()
        threads: List[threading.Thread] = []
        
        for task_id, difficulty in tasks:
            # Crear hilo para cada tarea [cite: 120]
            thread = threading.Thread(
                target=self._worker_thread,
                args=(task_id, difficulty)
            )
            threads.append(thread)
            thread.start() # Iniciar hilo [cite: 125]

        # Esperar a que todos los hilos terminen [cite: 127]
        for thread in threads:
            thread.join()
            
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"\n[RESUMEN THREADS] Tareas completadas: {self.tasks_completed_threads}")
        print(f"[RESUMEN THREADS] Tiempo total de ejecución: {execution_time:.4f} segundos")
        return execution_time


    def run_with_processes(self, tasks: List[Task]) -> float:
        """Ejecutar tareas usando PROCESOS (memoria separada, usa multiprocessing.Value) [cite: 27]"""
        print("\n--- Ejecución con PROCESOS (Multiprocessing) ---")
        
        start_time = time.time()
        processes: List[multiprocessing.Process] = []
        
        # Reiniciar el contador de procesos para esta corrida
        self.tasks_completed_processes.value = 0
        
        for task_id, difficulty in tasks:
            # Crear proceso para cada tarea
            process = multiprocessing.Process(
                target=TaskProcessor._worker_process,
                # Pasamos el multiprocessing.Value como argumento para compartir el contador
                args=(task_id, difficulty, self.tasks_completed_processes)
            )
            processes.append(process)
            process.start()

        # Esperar a que todos los procesos terminen
        for process in processes:
            process.join()
            
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"\n[RESUMEN PROCESSES] Tareas completadas: {self.tasks_completed_processes.value}")
        print(f"[RESUMEN PROCESSES] Tiempo total de ejecución: {execution_time:.4f} segundos")
        return execution_time


def generate_tasks(num_tasks: int = 20) -> List[Task]:
    """Genera 20 tareas con dificultad aleatoria (1-5) [cite: 34]"""
    return [(i + 1, random.randint(1, 5)) for i in range(num_tasks)]

# --- Ejecución Principal para Comparación ---

if __name__ == "__main__":
    
    # 1. Generar tareas [cite: 34]
    TASKS = generate_tasks(num_tasks=20)
    print(f"Tareas generadas ({len(TASKS)}): {TASKS}")
    
    processor = TaskProcessor()
    
    # 2. Ejecutar con Hilos y medir tiempo [cite: 35]
    time_threads = processor.run_with_threads(TASKS)
    
    # 3. Ejecutar con Procesos y medir tiempo [cite: 35]
    time_processes = processor.run_with_processes(TASKS)
    
    # 4. Análisis de resultados (para incluir en results_analysis.md y README.md) [cite: 36]
    print("\n\n--- ANÁLISIS DE RENDIMIENTO ---")
    print(f"Tiempo total con HILOS: {time_threads:.4f}s")
    print(f"Tiempo total con PROCESOS: {time_processes:.4f}s")
    
    if time_threads < time_processes:
        print("\nCONCLUSIÓN: Los **HILOS** fueron más rápidos.")
        print("Esto se debe a que la tarea es 'I/O Bound' (pasa mucho tiempo esperando en 'time.sleep'), y Python maneja el bloqueo de I/O de los hilos de manera eficiente[cite: 272].")
    else:
        print("\nCONCLUSIÓN: Los **PROCESOS** fueron más rápidos.")
        print("Esto indicaría que la tarea, aunque simula I/O, pudo tener un cuello de botella en CPU que los procesos superaron al evitar el GIL de Python[cite: 273].")