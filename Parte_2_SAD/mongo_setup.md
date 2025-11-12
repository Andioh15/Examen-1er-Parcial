Configuración de Nodos Distribuidos MongoDB con Docker Compose

El sistema de almacenamiento distribuido se basa en la orquestación de contenedores Docker para simular un cluster de MongoDB.

Archivo docker-compose.yml

Se utiliza un archivo docker-compose.yml simplificado que permite que Docker cree automáticamente la red interna necesaria para la comunicación entre los servicios.

mongo1 mongo:latest 27017 Primer nodo de almacenamiento

mongo2 mongo:latest 27018 Segundo nodo de almacenamiento

storage_app Construido sin_puerto Aplicación Python con lógica de sharding

Dockerfile para la Aplicación Python

El Dockerfile se encuentra en la carpeta ./Parte_2_SAD y tiene la siguiente estructura:

Usa la imagen base python:3.12.10.

Instala la dependencia pymongo.

Copia el archivo sistema_almacenamiento.py.

Define CMD ["python", "sistema_almacenamiento.py"] como comando de inicio.

Proceso de Configuración

Para garantizar el funcionamiento de la comunicación interna (e.g., storage_app conectándose a mongo1 y mongo2):

Conexión Interna: La aplicación Python utiliza los nombres de servicio definidos en Docker Compose (mongo1 y mongo2) como nombres de host en la cadena de conexión de PyMongo, ya que los tres servicios están automáticamente en la misma red por defecto de Docker Compose.

Puertos: Los puertos 27017 y 27018 solo se mapean para permitir el acceso desde el host si fuera necesario verificar los datos manualmente (e.g., con una herramienta como Mongo Compass).