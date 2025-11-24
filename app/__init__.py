from flask import Flask

# Para poder conectar front y backend
from flask_cors import CORS
from .config.config import CORS_ORIGINS

app = Flask(__name__)
CORS(app, resources={"/*": {"origins": CORS_ORIGINS}})  # habilita CORS

# Registrar rutas
from .routes import services