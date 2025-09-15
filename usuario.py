from flask import Flask, jsonify, request  #  Web framework para crear APIs
import sqlite3                            #  Base de datos SQLite
import jwt                                #  JSON Web Tokens (autenticación)
import datetime                           #  Manejo de fechas y tiempos
import os                                 #  Acceso a variables del sistema
from dotenv import load_dotenv            #  Carga variables de entorno

load_dotenv()

app = Flask(__name__)

# Obtener todas las configuraciones desde variables de entorno
SECRET_KEY = os.getenv('SECRET_KEY', 'fallback_secret')
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///usuarios.db')
PORT = int(os.getenv('PORT', 5003))
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 1))

def conectar_db():
   
    db_path = DATABASE_URL.replace('sqlite:///', '')
    conn = sqlite3.connect(db_path)
    return conn

def inicializar_db():
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

# Y esta llamada:
inicializar_db()

# Prueba de vida, si el micro esta corriendo y puede responder
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",  # El servicio esta vivo
        "service": "user_service", # Nombre del microservicio
        "database": DATABASE_URL # Muestra que bd se esta usando
    })


# Ruta para registrar un nuevo usuario
@app.route('/registro', methods=['POST'])
def registrar_usuario():
    datos = request.get_json()
    nombre = datos.get('nombre')
    email = datos.get('email')
    password = datos.get('password')
    
    conn = conectar_db()
    cursor = conn.cursor()
    
    try:
        # Insertamos el nuevo usuario
        cursor.execute('INSERT INTO usuarios (nombre, email, password) VALUES (?, ?, ?)', 
                       (nombre, email, password))
        
        conn.commit()
        conn.close()
        
        return jsonify({"mensaje": "Usuario registrado correctamente"}), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "El email ya está registrado"}), 400

# Ruta para iniciar sesión y obtener un token JWT
@app.route('/login', methods=['POST'])
def login():
    datos = request.get_json()
    email = datos.get('email')
    password = datos.get('password')
    
    conn = conectar_db()
    cursor = conn.cursor()
    
    # Verificamos las credenciales
    cursor.execute('SELECT id, nombre FROM usuarios WHERE email = ? AND password = ?', 
                   (email, password))
    usuario = cursor.fetchone()
    
    conn.close()
    
    if usuario:
        # Creamos un token JWT válido por 1 hora
        # El token es como un pase de identificación temporal
        payload = {
            'usuario_id': usuario[0],
            'nombre': usuario[1],
            'exp': datetime.datetime.now() + datetime.timedelta(hours=1)
        }
        
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        
        return jsonify({"token": token})
    else:
        return jsonify({"error": "Credenciales inválidas"}), 401

inicializar_db()
if __name__ == '__main__':
    app.run(debug=DEBUG, port=PORT)