import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor  # Devuelve filas como diccionarios
import logging
import time

logger = logging.getLogger("autodoc")  # Logger para mensajes de depuración

class PsqlConnectionPool:
    """
    Clase para manejar un pool de conexiones a PostgreSQL.
    Esto evita abrir/cerrar conexiones constantemente, mejora eficiencia y rendimiento.
    """
    _pool = None  # Variable de clase para guardar el pool de conexiones

    def __init__(self, config):
        """
        Inicializa la configuración de la conexión desde un diccionario.
        """
        self.user = config["DB_USER"]
        self.password = config["DB_PASS"]
        self.host = config["DB_HOST"]
        self.port = config.get("DB_PORT", 5432)
        self.database = config["DB_NAME"]
        self.pool_min = config.get("DB_POOL_MIN", 1)  # conexiones mínimas en el pool
        self.pool_max = config.get("DB_POOL_MAX", 5)  # conexiones máximas en el pool
        self.retries = config.get("DB_CONN_RETRIES", 3)  # reintentos si falla la conexión
        self.timeout = config.get("DB_CONN_TIMEOUT", 10)  # timeout en segundos

    def connect(self):
        """
        Crea el pool de conexiones si no existe.
        """
        if self._pool is not None:
            # Ya existe el pool, no hacemos nada
            return

        # Creamos un ThreadedConnectionPool
        self._pool = psycopg2.pool.ThreadedConnectionPool(
            self.pool_min,
            self.pool_max,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database,
            connect_timeout=self.timeout,
            cursor_factory=RealDictCursor  # Para que devuelva filas como diccionarios
        )
        logger.info("[DB] Connection pool created.")

    def get_connection(self):
        """
        Obtiene una conexión del pool.
        Reintenta varias veces si hay errores temporales.
        """
        if self._pool is None:
            self.connect()  # Crear pool si no existe

        for attempt in range(self.retries):
            try:
                conn = self._pool.getconn()  # Obtener conexión del pool
                return conn
            except Exception as e:
                logger.warning(f"[DB] Connection attempt {attempt + 1} failed: {e}")
                time.sleep(1)  # Espera 1 segundo antes de reintentar

        raise Exception("Could not get DB connection after retries.")

    def release_connection(self, conn):
        """
        Devuelve la conexión al pool.
        """
        if self._pool and conn:
            self._pool.putconn(conn)
            logger.debug("[DB] Connection released back to pool.")

    def close_all(self):
        """
        Cierra todas las conexiones del pool.
        """
        if self._pool:
            self._pool.closeall()
            self._pool = None
            logger.info("[DB] All connections closed.")

    # ------------------ Helpers para consultas ------------------ #
    @staticmethod
    def fetch_all(cursor):
        """
        Devuelve todas las filas de una consulta como lista de diccionarios.
        """
        return cursor.fetchall() if cursor.rowcount else []

    @staticmethod
    def fetch_one(cursor):
        """
        Devuelve la primera fila de una consulta como diccionario.
        """
        result = cursor.fetchone()
        return result if result else None


# ------------------ Context manager para usar con "with" ------------------ #
from contextlib import contextmanager

@contextmanager
def db_cursor(pool: PsqlConnectionPool):
    """
    Context manager para manejar conexión y cursor de forma automática.
    - Hace commit si todo va bien
    - Hace rollback si hay error
    - Devuelve el cursor listo para ejecutar consultas
    """
    conn = pool.get_connection()   # Obtener conexión del pool
    cursor = conn.cursor()         # Crear cursor
    try:
        yield cursor               # Se usa en bloque with
        conn.commit()              # Commit automático al finalizar el bloque
    except Exception as e:
        conn.rollback()            # Rollback si hay error
        raise e
    finally:
        cursor.close()             # Cierra el cursor
        pool.release_connection(conn)  # Devuelve la conexión al pool