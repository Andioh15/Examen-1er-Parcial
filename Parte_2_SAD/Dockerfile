# Usa una imagen base de Python oficial
FROM python:3.12.10

# Define el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala las dependencias. 
RUN pip install pymongo

# Copia los archivos de la aplicación al contenedor
# Copia sistema_almacenamiento.py y el archivo principal si existe
COPY sistema_almacenamiento.py .

# Comando que se ejecuta al iniciar el contenedor. 
# Esto iniciará tu sistema de almacenamiento distribuido.
CMD ["python", "sistema_almacenamiento.py"]