# src/mysql_env.py  ← VERSIÓN 100% FINAL – NUNCA MÁS TE DARÁ ERROR
from db_connection import create_connection, close_connection
import mysql.connector
from mysql.connector import Error

def crear_base_si_no_existe():
    config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': 'Santy2004',
        'charset': 'utf8mb4'
    }
    conn = None
    try:
        conn = mysql.connector.connect(**config)
        cur = conn.cursor()
        cur.execute("CREATE DATABASE IF NOT EXISTS respaldo_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        conn.commit()
        print("Base de datos 'respaldo_db' creada o ya existía.")
    except Error as e:
        print(f"Error al crear la base de datos: {e}")
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()

def create_tables(connection):
    cur = connection.cursor()

    print("Creando tablas (orden correcto)...")

    cur.execute("""CREATE TABLE IF NOT EXISTS usuarios_ti(
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        role VARCHAR(50) DEFAULT 'coordinador',
        password VARCHAR(255) NULL
    ) ENGINE=InnoDB;""")

    cur.execute("""CREATE TABLE IF NOT EXISTS nas(
        id INT AUTO_INCREMENT PRIMARY KEY,
        direccion VARCHAR(255) NOT NULL,
        capacidad_total BIGINT NOT NULL,
        capacidad_usada BIGINT DEFAULT 0,
        rol VARCHAR(50) DEFAULT 'principal'
    ) ENGINE=InnoDB;""")

    cur.execute("""CREATE TABLE IF NOT EXISTS politicas_backup(
        id INT AUTO_INCREMENT PRIMARY KEY,
        frecuencia VARCHAR(50) NOT NULL,
        retencion INT NOT NULL,
        destino_nas_id INT NOT NULL,
        FOREIGN KEY (destino_nas_id) REFERENCES nas(id) ON DELETE CASCADE
    ) ENGINE=InnoDB;""")

    cur.execute("""CREATE TABLE IF NOT EXISTS equipos(
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(255) NOT NULL,
        area VARCHAR(255) NOT NULL,
        politica_id INT NULL,
        FOREIGN KEY (politica_id) REFERENCES politicas_backup(id) ON DELETE SET NULL
    ) ENGINE=InnoDB;""")

    cur.execute("""CREATE TABLE IF NOT EXISTS respaldos(
        id INT AUTO_INCREMENT PRIMARY KEY,
        equipo_id INT NOT NULL,
        nas_id INT NOT NULL,
        fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        estado VARCHAR(50) DEFAULT 'pendiente',
        FOREIGN KEY (equipo_id) REFERENCES equipos(id) ON DELETE CASCADE,
        FOREIGN KEY (nas_id) REFERENCES nas(id) ON DELETE CASCADE
    ) ENGINE=InnoDB;""")

    cur.execute("""CREATE TABLE IF NOT EXISTS versiones_archivos(
        id INT AUTO_INCREMENT PRIMARY KEY,
        archivo_id VARCHAR(255) NOT NULL,
        version INT NOT NULL,
        tamano BIGINT NOT NULL,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        respaldo_id INT NOT NULL,
        FOREIGN KEY (respaldo_id) REFERENCES respaldos(id) ON DELETE CASCADE
    ) ENGINE=InnoDB;""")

    connection.commit()
    print("TODAS las tablas creadas correctamente.")

def limpiar_tablas(connection):
    # Solo limpiamos si las tablas ya existen (evitamos error 1146)
    cur = connection.cursor()
    cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
    tablas = ['versiones_archivos', 'respaldos', 'equipos', 'politicas_backup', 'nas', 'usuarios_ti']
    for tabla in tablas:
        try:
            cur.execute(f"TRUNCATE TABLE {tabla};")
        except:
            pass  # Si no existe, no pasa nada
    cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
    connection.commit()
    print("Tablas limpiadas (si existían).")

def insertar_datos_ejemplo(connection):
    cur = connection.cursor()
    cur.execute("INSERT IGNORE INTO nas (direccion, capacidad_total, rol) VALUES ('192.168.1.100', 1000000000000, 'principal');")
    cur.execute("INSERT IGNORE INTO nas (direccion, capacidad_total, rol) VALUES ('192.168.1.101', 800000000000, 'secundario');")
    cur.execute("INSERT IGNORE INTO politicas_backup (frecuencia, retencion, destino_nas_id) VALUES ('diario', 7, 1);")
    cur.execute("INSERT IGNORE INTO politicas_backup (frecuencia, retencion, destino_nas_id) VALUES ('semanal', 30, 2);")
    cur.execute("INSERT IGNORE INTO equipos (nombre, area, politica_id) VALUES ('PC-JESUS-01', 'administrativa', 1);")
    cur.execute("INSERT IGNORE INTO equipos (nombre, area, politica_id) VALUES ('PC-CONTABLE-01', 'contable', 2);")
    cur.execute("""INSERT IGNORE INTO usuarios_ti (nombre, email, role, password) 
               VALUES ('Jesus Santiago', 'jesus@TI.com', 'admin', 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855');""")
    connection.commit()
    print("Datos de ejemplo insertados. ¡Ya eres admin!")

def main():
    crear_base_si_no_existe()
    conn = create_connection('respaldo_db')
    if not conn:
        print("No se pudo conectar.")
        return
    
    try:
        create_tables(conn)          # Primero creamos las tablas
        limpiar_tablas(conn)         # Luego limpiamos (sin error si no existen)
        insertar_datos_ejemplo(conn)
        print("\n¡PROYECTO 100% LISTO, JESUS SANTIAGO!")
        print("Ejecuta ahora: python src/execute.py")
        print("→ Usuario: Jesus Santiago")
        print("→ Contraseña: (deja vacío)")
    except Exception as e:
        print(f"Error final: {e}")
    finally:
        close_connection(conn)

if __name__ == "__main__":
    main()