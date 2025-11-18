import pymongo
from pymongo import MongoClient
import hashlib
from datetime import datetime
from typing import Dict, Tuple, List, Any
import random

# Definición de la clase principal
class DistributedStorage:
    def __init__(self):
        # Conectar a múltiples instancias MongoDB (Requisito)
        self.nodes = [
            {'client': None, 'db': None, 'name': 'node1', 'port': 27017},
            {'client': None, 'db': None, 'name': 'node2', 'port': 27018}
        ]
        self._connect_nodes()

    def _connect_nodes(self):
        """Intenta conectar a las instancias de MongoDB."""
        print("Intentando conectar a nodos distribuidos...")
        try:
            # Conexión al PRIMER MongoDB (puerto 27017) 
            self.nodes[0]['client'] = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=5000)
            # Seleccionar base de datos                              
            self.nodes[0]['db'] = self.nodes[0]['client']['distributed_db']
            self.nodes[0]['client'].admin.command('ping')
            print(f"✔️ Conectado a {self.nodes[0]['name']} (Puerto 27017)")
            
            # Conexión al SEGUNDO MongoDB (puerto 27018) 
            self.nodes[1]['client'] = MongoClient('mongodb://localhost:27018', serverSelectionTimeoutMS=5000)
            # Seleccionar base de datos                             
            self.nodes[1]['db'] = self.nodes[1]['client']['distributed_db']
            self.nodes[1]['client'].admin.command('ping')
            print(f"✔️ Conectado a {self.nodes[1]['name']} (Puerto 27018)")

        except pymongo.errors.ServerSelectionTimeoutError as e:
            print(f"❌ Error de conexión a MongoDB. Asegúrate de que Docker esté corriendo y los puertos 27017/27018 estén libres.")
            # Es vital salir o manejar si la conexión falla.
            raise e

    def _select_node_for_document(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Decide en qué nodo guardar el documento usando sharding por hash."""
        # Obtener o generar ID del documento
        document_id = str(document_data.get('id'))
        
        # Crear hash del ID para distribución consistente  
        hash_value = hashlib.md5(document_id.encode()).hexdigest()  
        
        # Usar módulo para elegir nodo (0 o 1)  
        node_index = int(hash_value, 16) % len(self.nodes)
        
        return self.nodes[node_index]

    def insert_document(self, data: Dict[str, Any]):
        """Inserta documento distribuyéndolo entre nodos (Requisito)."""
        # 1. Seleccionar nodo automáticamente  
        target_node = self._select_node_for_document(data)
        target_db = target_node['db']
        node_name = target_node['name']

        if target_db is None:
            print(f"  [X] Nodo destino {node_name} no disponible. Saltando inserción para ID {data.get('id')}.")
            return

        # 2. Preparar documento con metadatos  
        document = {
            '_id': data.get('id'), # Usar el ID como _id  
            'data': data,
            'node': node_name, # Guardamos en qué nodo quedó  
            'created_at': datetime.now()
        }
        
        # 3. Insertar en el nodo seleccionado 
        try:
            result = target_db.documents.insert_one(document)  
            # print(f"  [+] Documento {data.get('id')} guardado en {node_name}")  
        except pymongo.errors.DuplicateKeyError:
             print(f"  [!] Documento {data.get('id')} ya existe. Saltando inserción.")
        except Exception as e:
            print(f"  [X] Error al insertar en {node_name}: {e}")

    def find_document(self, document_id: int) -> List[Dict[str, Any]]:
        """Busca documento en todos los nodos (Requisito)."""
        print(f"\n🔍 Buscando documento ID: {document_id}")
        results = []
        
        for node in self.nodes:
            db = node['db']
            node_name = node['name']
            
            if db is None:
                print(f"  ❌ Nodo {node_name} no disponible. Omitiendo búsqueda en este nodo.")
                continue
            
            # Buscar en el nodo actual
            doc = db.documents.find_one({'_id': document_id})  
            
            if doc:
                doc['source_node'] = node_name # Marcar de dónde vino  
                results.append(doc)
                print(f"  ✔️ Encontrado en {node_name}")
            else:
                print(f"  ❌ No encontrado en {node_name}")
        
        return results

    def get_stats(self):
        """Obtiene y muestra estadísticas de distribución (Requisito)."""
        print("\n📊 Estadísticas de Distribución:")
        total_docs = 0
        node_counts = {}

        for node in self.nodes:
            db = node['db']
            node_name = node['name']
            
            if db is None:
                print(f"  ⚠️ Nodo {node_name} no disponible. Contador 0.")
                node_counts[node_name] = 0
                continue
            
            # Contar documentos en la colección 'documents'
            count = db.documents.count_documents({})
            node_counts[node_name] = count
            total_docs += count
        
        if total_docs == 0:
            print("No hay documentos para analizar.")
            return

        print(f"Total de Documentos Insertados: {total_docs}")
        print("---------------------------------")
        for name, count in node_counts.items():
            percentage = (count / total_docs) * 100
            print(f"- {name}: {count} documentos ({percentage:.2f}%)")
        print("---------------------------------")
        print("Se espera una distribución cercana al 50/50 gracias al sharding por hash.")
        
        return node_counts

# --- Funciones Auxiliares ---
def generate_sample_data(num_documents: int = 100) -> List[Dict[str, Any]]:
    """Genera 100 documentos de ejemplo (Requisito)."""
    sample_data = []
    for i in range(num_documents):
        sample_data.append({
            'id': i, # ID único para cada documento  
            'name': f'Documento_{i}',
            'value': i * 10,
            'category': f'categoria_{i % 5}', # 5 categorías diferentes  
            'timestamp': datetime.now()
        })
    return sample_data

# --- Ejecución Principal ---
if __name__ == "__main__":
    
    # 1. Inicializar y conectar al almacenamiento distribuido
    storage = DistributedStorage()
    
    # Limpiar colecciones para una ejecución limpia
    for node in storage.nodes:
        if node['db'] is not None:
            node['db'].documents.drop() 
            print(f"Limpiando colección 'documents' en {node['name']}")
    
    # 2. Generar 100 documentos de ejemplo
    SAMPLE_DOCUMENTS = generate_sample_data(num_documents=100)
    print(f"\nGenerados {len(SAMPLE_DOCUMENTS)} documentos de ejemplo.")

    # 3. Insertar documentos con distribución automática
    print("Iniciando inserción distribuida...")
    for doc in SAMPLE_DOCUMENTS:
        storage.insert_document(doc)
    print("Inserción completada.")
    
    # 4. Mostrar estadísticas de distribución
    storage.get_stats()
    
    # 5. Realizar búsquedas distribuidas
    # Documento que debería existir
    storage.find_document(document_id=50) 
    # Documento que no debería existir
    storage.find_document(document_id=999) 
    
    # Comando para apagar Docker al terminar (Recomendación)
    print("\nPara detener los nodos de MongoDB: docker-compose down")