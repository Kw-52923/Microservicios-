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
SECRET_KEY = os.getenv('SECRET_KEY', 'pedido123')  # Valor por defecto por si no existe en .env
DATABASE_NAME = os.getenv('DATABASE_URL', 'sqlite:///pedido.db').replace('sqlite:///', '')
PORT = int(os.getenv('PORT', 5002))  # Convertir a entero
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'  # Convertir a booleano

def verificar_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"]) # Algoritmo de firma para JWT, asegura que el token no haya sido modificado
        return payload
    except jwt.InvalidTokenError:
        return None

def conectar_db():
    conn = sqlite3.connect(DATABASE_NAME)
    return conn

def inicializar_db():
    conn = conectar_db()
    cursor = conn.cursor()
    
    # Creamos la tabla de pedidos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            estado TEXT DEFAULT 'pendiente'
        )
    ''')
    
    conn.commit()
    conn.close()

# Ruta para crear un nuevo pedido
@app.route('/pedidos', methods=['POST'])
def crear_pedido():
    # Verificamos el token
    token = request.headers.get('Authorization')
    if not token or not verificar_token(token.replace("Bearer ", "")):
        return jsonify({"error": "Token inválido"}), 401
    
    # Obtenemos los datos del pedido
    datos = request.get_json()
    usuario_id = datos.get('usuario_id')
    producto_id = datos.get('producto_id')
    cantidad = datos.get('cantidad')
    
    # En un sistema real, aquí verificaríamos con el servicio de productos
    # si el producto existe y tiene stock disponible
    
    conn = conectar_db()
    cursor = conn.cursor()
    
    # Insertamos el nuevo pedido
    cursor.execute('INSERT INTO pedidos (usuario_id, producto_id, cantidad) VALUES (?, ?, ?)', 
                   (usuario_id, producto_id, cantidad))
    
    conn.commit()
    conn.close()
    
    return jsonify({"mensaje": "Pedido creado correctamente"}), 201


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy", 
        "service": "pedido_service",
        "database": DATABASE_NAME
    })

# Ruta para obtener los pedidos de un usuario
@app.route('/pedidos/usuario/<int:usuario_id>', methods=['GET'])
def obtener_pedidos_usuario(usuario_id):
    # Verificamos el token
    token = request.headers.get('Authorization')
    if not token or not verificar_token(token.replace("Bearer ", "")):
        return jsonify({"error": "Token inválido"}), 401
    
    conn = conectar_db()
    cursor = conn.cursor()
    
    # Obtenemos los pedidos del usuario
    cursor.execute('SELECT * FROM pedidos WHERE usuario_id = ?', (usuario_id,))
    pedidos = cursor.fetchall()
    
    conn.close()
    
    # Convertimos los resultados
    resultado = []
    for pedido in pedidos:
        resultado.append({
            "id": pedido[0],
            "usuario_id": pedido[1],
            "producto_id": pedido[2],
            "cantidad": pedido[3],
            "estado": pedido[4]
        })
    
    return jsonify(resultado)

inicializar_db()

# Ejecutamos la aplicación Flask
if __name__ == '__main__':
    print(f"🚀 Iniciando Servicio de Productos en puerto {PORT}...")
    # Iniciamos el servidor con configuración desde variables de entorno
    app.run(debug=DEBUG, port=PORT)