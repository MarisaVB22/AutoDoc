APP_PORT = 5000
CORS_ORIGINS = ["http://localhost:5173"]  # frontend en desarrollo

# Configuración de la base de datos
# Configuración de la base de datos
DB_CONFIG = {
    "DB_HOST": "127.0.0.1",  
    "DB_NAME": "autodoc_db",
    "DB_USER": "autodoc_user",
    "DB_PASS": "autodoc",
    "DB_PORT": 5432,
    "DB_POOL_MIN": 1,
    "DB_POOL_MAX": 5,
    "DB_CONN_RETRIES": 3,
    "DB_CONN_TIMEOUT": 10
}