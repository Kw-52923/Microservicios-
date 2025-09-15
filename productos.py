# Importamos las librerías necesarias
from flask import Flask, jsonify, request  # Flask para crear el servidor web
import sqlite3  # Para trabajar con bases de datos SQLite
import jwt  # Para crear y verificar tokens JWT
import datetime  # Para manejar fechas y tiempos
import os  # Nuevo: Para acceder a variables del sistema
from dotenv import load_dotenv  # Nuevo: Para cargar el archivo .env

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Creamos una aplicación Flask
app = Flask(__name__)

# Obtener valores desde variables de entorno con valores por defecto
SECRET_KEY = os.getenv('SECRET_KEY', 'productos123')  # Valor por defecto por si no existe en .env
DATABASE_NAME = os.getenv('DATABASE_URL', 'sqlite:///productos.db').replace('sqlite:///', '')
PORT = int(os.getenv('PORT', 5001))  # Convertir a entero
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'  # Convertir a booleano

# # Mostrar configuración cargada (opcional, para debugging)
# print(f"🔧 Configuración cargada:")
# print(f"   SECRET_KEY: {SECRET_KEY}")
# print(f"   DATABASE_NAME: {DATABASE_NAME}")
# print(f"   PORT: {PORT}")
# print(f"   DEBUG: {DEBUG}")

# Función para verificar el token JWT
def verificar_token(token):
    try:
        # Decodificamos el token usando nuestra clave secreta
        # Es como verificar una identificación con una lupa especial
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.InvalidTokenError:
        # Si el token no es válido, devolvemos None
        return None

# Función para conectar a la base de datos
def conectar_db():
    # Conectamos a la base de datos SQLite (si no existe, se crea automáticamente)
    # Usamos el nombre de la base de datos desde las variables de entorno
    conn = sqlite3.connect(DATABASE_NAME)
    return conn

# Función para inicializar la base de datos (crear tablas si no existen)
def inicializar_db():
    conn = conectar_db()
    cursor = conn.cursor()
    
    # Creamos la tabla de productos si no existe
    # SQL es el lenguaje para hablar con las bases de datos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            descripcion TEXT
        )
    ''')
    
    # Guardamos los cambios y cerramos la conexión
    conn.commit()
    conn.close()
    print(f"✅ Base de datos '{DATABASE_NAME}' inicializada correctamente")



# Ruta para obtener todos los productos
@app.route('/productos', methods=['GET'])
def obtener_productos():
    # Verificamos el token de autenticación
    token = request.headers.get('Authorization')
    if not token or not verificar_token(token.replace("Bearer ", "")):
        return jsonify({"error": "Token inválido"}), 401
    
    conn = conectar_db()
    cursor = conn.cursor()
    
    # Obtenemos todos los productos de la base de datos
    cursor.execute('SELECT * FROM productos')
    productos = cursor.fetchall()
    
    conn.close()
    
    # Convertimos los resultados a un formato más amigable
    resultado = []
    for producto in productos:
        resultado.append({
            "id": producto[0],
            "nombre": producto[1],
            "precio": producto[2],
            "descripcion": producto[3]
        })
    
    return jsonify(resultado)

# Ruta para agregar un nuevo producto
@app.route('/productos', methods=['POST'])
def agregar_producto():
    # Verificamos el token
    token = request.headers.get('Authorization')
    if not token or not verificar_token(token.replace("Bearer ", "")):
        return jsonify({"error": "Token inválido"}), 401
    
    # Obtenemos los datos del producto del cuerpo de la solicitud
    datos = request.get_json()
    nombre = datos.get('nombre')
    precio = datos.get('precio')
    descripcion = datos.get('descripcion', '')
    
    conn = conectar_db()
    cursor = conn.cursor()
    
    # Insertamos el nuevo producto en la base de datos
    cursor.execute('INSERT INTO productos (nombre, precio, descripcion) VALUES (?, ?, ?)', 
                   (nombre, precio, descripcion))
    
    conn.commit()
    conn.close()
    
    return jsonify({"mensaje": "Producto agregado correctamente"}), 201

# Ruta de salud para verificar que el servicio está funcionando
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "product_service",
        "database": DATABASE_NAME
    })

# Inicializamos la base de datos cuando arranca el servicio
inicializar_db()

# Ejecutamos la aplicación Flask
if __name__ == '__main__':
    print(f"🚀 Iniciando Servicio de Productos en puerto {PORT}...")
    # Iniciamos el servidor con configuración desde variables de entorno
    app.run(debug=DEBUG, port=PORT)