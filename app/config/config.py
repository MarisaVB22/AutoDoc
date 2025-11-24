APP_PORT = 5000
CORS_ORIGINS = ["http://localhost:5173"]  # frontend en desarrollo

# Configuración de la base de datos
# Configuración de la base de datos
DB_CONFIG = {
    "host": "127.0.0.1",
    "database": "autodoc_db",
    "user": "autodoc_user",
    "password": "autodoc",   # ← sin caracteres especiales 👍
    "port": 5432,
    "minconn": 1,
    "maxconn": 5,
}