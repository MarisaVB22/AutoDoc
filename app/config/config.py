APP_PORT = 5000
CORS_ORIGINS = ["http://localhost:5173"]  # frontend en desarrollo

# Configuración de la base de datos
DB_CONFIG = {
    "DB_HOST": "127.0.0.1",
    "DB_NAME": "autodoc_db",
    "DB_USER": "autodoc_user",
    "DB_PASS": "autodoc",
    "DB_PORT": 5432,
    "MINCONN": 1,
    "MAXCONN": 5,
}