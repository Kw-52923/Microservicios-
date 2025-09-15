# Sistema de Microservicios 🐧

Arquitectura de microservicios para una tienda online con servicios independientes y comunicación via JWT tokens.

## 🏗️ Arquitectura

El sistema está dividido en **3 microserviios independientes**:

- **👤 Servicio de Usuarios** (Puerto 5003) - Registro y autenticación
- **📦 Servicio de Productos** (Puerto 5001) - Gestión de catálogo  
- **🛒 Servicio de Pedidos** (Puerto 5002) - Procesamiento de órdenes

Cada servicio tiene su propia base de datos SQLite y expone APIs REST independientes.

## 🚀 Inicio Rápido

### Instalación
```bash
pip install flask pyjwt python-dotenv
```

### Configuración
Crea un archivo `.env` en la raíz del proyecto:
```env
SECRET_KEY=tu_clave_super_secreta
DATABASE_URL=sqlite:///database.db
PORT=5000
DEBUG=True
JWT_EXPIRATION_HOURS=24
```

### Ejecutar los servicios
```bash
# Terminal 1 - Servicio de Usuarios
python usuario.py

# Terminal 2 - Servicio de Productos  
python productos.py

# Terminal 3 - Servicio de Pedidos
python pedidos.py
```

## 📡 APIs Disponibles

### 👤 Servicio de Usuarios (`localhost:5003`)

#### Registrar Usuario
```http
POST /registro
Content-Type: application/json

{
  "nombre": "Juan Pérez",
  "email": "juan@email.com", 
  "password": "password123"
}
```

#### Login
```http
POST /login
Content-Type: application/json

{
  "email": "juan@email.com",
  "password": "password123"
}
```

**Respuesta:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 📦 Servicio de Productos (`localhost:5001`)

#### Listar Productos
```http
GET /productos
Authorization: Bearer <tu_token>
```

#### Agregar Producto
```http
POST /productos
Authorization: Bearer <tu_token>
Content-Type: application/json

{
  "nombre": "Laptop Gaming",
  "precio": 1299.99,
  "descripcion": "Laptop para gaming de alta gama"
}
```

### 🛒 Servicio de Pedidos (`localhost:5002`)

#### Crear Pedido
```http
POST /pedidos
Authorization: Bearer <tu_token>
Content-Type: application/json

{
  "usuario_id": 1,
  "producto_id": 1,
  "cantidad": 2
}
```

#### Obtener Pedidos de Usuario
```http
GET /pedidos/usuario/1
Authorization: Bearer <tu_token>
```

## 🛡️ Autenticación

El sistema usa **JWT tokens** para la comunicación entre servicios:

1. Regístrate o haz login en el servicio de usuarios
2. Usa el token recibido en el header `Authorization: Bearer <token>`
3. Los tokens expiran según `JWT_EXPIRATION_HOURS` (default: 1 hora)

## 🗄️ Bases de Datos

Cada servicio mantiene su propia base de datos SQLite:

- **usuarios.db** - Almacena usuarios registrados
- **productos.db** - Catálogo de productos
- **pedido.db** - Órdenes y estados

## 💡 Características

- ✅ **Arquitectura de microservicios** con responsabilidades separadas
- ✅ **APIs RESTful** con endpoints bien definidos  
- ✅ **Autenticación JWT** para comunicación segura
- ✅ **Bases de datos independientes** por servicio
- ✅ **Health checks** en cada servicio (`/health`)
- ✅ **Configuración via variables de entorno**
- ✅ **Manejo de errores** y validaciones

## 🔍 Health Checks

Verifica el estado de cada servicio:
```bash
curl http://localhost:5003/health  # Usuarios
curl http://localhost:5001/health  # Productos  
curl http://localhost:5002/health  # Pedidos
```

## 📝 Flujo de Trabajo Típico

1. **Registro:** `POST /registro` → Crear cuenta de usuario
2. **Login:** `POST /login` → Obtener JWT token
3. **Productos:** `GET /productos` → Ver catálogo disponible  
4. **Pedido:** `POST /pedidos` → Crear nueva orden
5. **Seguimiento:** `GET /pedidos/usuario/{id}` → Ver mis pedidos

## 🛠️ Tecnologías

- **Flask** - Framework web minimalista
- **SQLite** - Base de datos embebida  
- **JWT** - Autenticación stateless
- **python-dotenv** - Gestión de variables de entorno
