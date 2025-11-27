import mysql.connector
from mysql.connector import Error
from mysql.connector import pooling
from dotenv import load_dotenv
import os

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    "port": int(os.getenv('DB_PORT', 3306)),
    'database': os.getenv('DB_NAME', 'respaldo_db'),
    "user": os.getenv('DB_USER', 'root'),
    "password": os.getenv('DB_PASSWORD', 'Santy2004'),
    "autocommit": False,
    "charset": "utf8mb4",
}

POOL_NAME = os.getenv('DB_POOL_NAME', 'respaldo_pool')
POOL_SIZE = int(os.getenv('DB_POOL_SIZE', 5))

try:
    pool = pooling.MySQLConnectionPool(
        pool_name=POOL_NAME,
        pool_size=POOL_SIZE,
        **DB_CONFIG
    )
    print("✅ Pool de conexiones creado exitosamente")
except Error as e:
    print(f"❌ Error al crear el pool de conexiones: {e}")
    pool = None

def get_conn():
    if pool:
        return pool.get_connection()
    else:
        raise Error("Pool de conexiones no disponible")

# Función para crear conexión directa (para mysql_env.py)
def create_connection(database_name=None):
    config = DB_CONFIG.copy()
    if database_name:
        config['database'] = database_name
    try:
        connection = mysql.connector.connect(**config)
        print("✅ Conexión directa establecida")
        return connection
    except Error as e:
        print(f"❌ Error al conectar a la base de datos: {e}")
        return None

def close_connection(connection):
    if connection:
        connection.close()