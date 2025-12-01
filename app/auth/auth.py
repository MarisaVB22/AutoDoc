import os
import requests
from flask import request, g, Response
from jose import jwt
from functools import wraps
from dotenv import load_dotenv
import psycopg2

load_dotenv()

# -------------------- Keycloak --------------------
KEYCLOAK_SERVER = os.getenv("KEYCLOAK_SERVER")  # http://localhost:8081
REALM = os.getenv("KEYCLOAK_REALM")            # autodoc
CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID")    # autodoc-frontend

JWKS_URL = f"{KEYCLOAK_SERVER}/realms/{REALM}/protocol/openid-connect/certs"

# -------------------- DB connection --------------------
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "autodoc_db")
DB_USER = os.getenv("DB_USER", "autodoc_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "autodoc")

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )
    return conn

# -------------------- JWT / Keycloak --------------------
def get_jwks():
    resp = requests.get(JWKS_URL)
    resp.raise_for_status()
    return resp.json()

def verify_token(token):
    jwks = get_jwks()
    unverified_header = jwt.get_unverified_header(token)

    rsa_key = None
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = key
            break
    if rsa_key is None:
        raise Exception("Key not found in JWKS")

    # Decodificamos el token sin validar audience
    payload = jwt.decode(
        token,
        rsa_key,
        algorithms=["RS256"],
        issuer=f"{KEYCLOAK_SERVER}/realms/{REALM}",
        options={"verify_aud": False}  # <--- Ignora el claim 'aud'
    )

    # Validamos que el token sea para nuestro cliente mediante 'azp'
    if payload.get("azp") != CLIENT_ID:
        raise Exception(f"Token no emitido para este cliente: {payload.get('azp')}")

    return payload

# -------------------- Decorador --------------------
def requires_auth(f):
    """Valida JWT y que el usuario exista en DB"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return Response("No Bearer token", status=401)

        token = auth.split()[1]
        try:
            payload = verify_token(token)
        except Exception as e:
            return Response(f"Token inválido: {str(e)}", status=401)

        # Tomamos email o preferred_username
        email = payload.get("email") or payload.get("preferred_username")
        if not email:
            return Response("Email no encontrado en token", status=401)

        # Validamos que el usuario existe en la DB (esquema autodoc)
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, email FROM autodoc.users WHERE email=%s", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if not user:
            return Response("Usuario no encontrado en DB", status=401)

        # Guardamos usuario en contexto global
        g.user = {"id": user[0], "email": user[1]}
        return f(*args, **kwargs)
    return wrapper