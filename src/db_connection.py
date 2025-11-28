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

pool = None 

def init_pool():
    """Crea el pool solo cuando la base de datos ya existe"""
    global pool
    if pool is None:
        try:
            pool = pooling.MySQLConnectionPool(
                pool_name="respaldo_pool",
                pool_size=5,
                **DB_CONFIG
            )
            print("Pool de conexiones creado exitosamente")
        except Error as e:
            print(f"Error al crear el pool: {e}")
            pool = None

def get_conn():
    """Obtiene conexión del pool o crea una directa si no existe"""
    global pool
    if pool is None:
        init_pool()
    if pool:
        try:
            return pool.get_connection()
        except:
            init_pool()
            if pool:
                return pool.get_connection()
    # Si falla el pool, conexión directa
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error de conexión directa: {e}")
        raise

def create_connection(database_name=None):
    config = DB_CONFIG.copy()
    if database_name:
        config['database'] = database_name
    try:
        connection = mysql.connector.connect(**config)
        return connection
    except Error as e:
        print(f"Error al conectar: {e}")
        return None

def close_connection(connection):
    if connection and connection.is_connected():
        connection.close()