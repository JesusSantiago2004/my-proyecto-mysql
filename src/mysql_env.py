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
        print("Base de datos 'respaldo_db' lista.")
    except Error as e:
        print(f"Error al crear la base de datos: {e}")
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()

def eliminar_tablas_existentes(connection):
    """Elimina todas las tablas existentes"""
    cur = connection.cursor()
    cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
    
    tablas = ['reportes', 'versiones_archivos', 'respaldos', 'equipos', 'politicas_backup', 'nas', 'usuarios_ti']
    for tabla in tablas:
        try:
            cur.execute(f"DROP TABLE IF EXISTS {tabla};")
            print(f"Tabla {tabla} eliminada")
        except Exception as e:
            print(f"Error al eliminar {tabla}: {e}")
    
    cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
    connection.commit()

def crear_tablas(connection):
    cur = connection.cursor()

    print("Creando tablas...")

    # ------------------ usuarios_ti ------------------
    cur.execute("""CREATE TABLE usuarios_ti(
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(255) NOT NULL UNIQUE,
        email VARCHAR(255) NOT NULL UNIQUE,
        role VARCHAR(50) DEFAULT 'auxiliar',
        password VARCHAR(255) NULL
    ) ENGINE=InnoDB;""")

    # ------------------ nas ------------------
    cur.execute("""CREATE TABLE nas(
        id INT AUTO_INCREMENT PRIMARY KEY,
        direccion VARCHAR(255) NOT NULL,
        capacidad_total BIGINT NOT NULL,
        capacidad_usada BIGINT DEFAULT 0,
        rol VARCHAR(50) DEFAULT 'principal'
    ) ENGINE=InnoDB;""")

    # ------------------ politicas_backup ------------------
    cur.execute("""CREATE TABLE politicas_backup(
        id INT AUTO_INCREMENT PRIMARY KEY,
        frecuencia VARCHAR(50) NOT NULL,
        retencion INT NOT NULL,
        destino_nas_id INT NOT NULL,
        FOREIGN KEY (destino_nas_id) REFERENCES nas(id) ON DELETE CASCADE
    ) ENGINE=InnoDB;""")

    # ------------------ equipos ------------------
    cur.execute("""CREATE TABLE equipos(
        id INT AUTO_INCREMENT PRIMARY KEY,
        id_unico VARCHAR(50) NOT NULL UNIQUE,
        nombre VARCHAR(255) NOT NULL UNIQUE,
        tipo VARCHAR(50) NOT NULL,
        usuario VARCHAR(255) NOT NULL,
        area VARCHAR(255) NOT NULL,
        username VARCHAR(100) NOT NULL UNIQUE,
        password VARCHAR(255) NULL,
        politica_id INT NULL,
        FOREIGN KEY (politica_id) REFERENCES politicas_backup(id) ON DELETE SET NULL
    ) ENGINE=InnoDB;""")

    # ------------------ respaldos ------------------
    cur.execute("""CREATE TABLE respaldos(
        id INT AUTO_INCREMENT PRIMARY KEY,
        equipo_id INT NOT NULL,
        nas_id INT NOT NULL,
        fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        estado VARCHAR(50) DEFAULT 'pendiente',
        FOREIGN KEY (equipo_id) REFERENCES equipos(id) ON DELETE CASCADE,
        FOREIGN KEY (nas_id) REFERENCES nas(id) ON DELETE CASCADE
    ) ENGINE=InnoDB;""")

    # ------------------ versiones_archivos ------------------
    cur.execute("""CREATE TABLE versiones_archivos(
        id INT AUTO_INCREMENT PRIMARY KEY,
        archivo_id VARCHAR(255) NOT NULL,
        version INT NOT NULL,
        tamano BIGINT NOT NULL,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        respaldo_id INT NOT NULL,
        FOREIGN KEY (respaldo_id) REFERENCES respaldos(id) ON DELETE CASCADE
    ) ENGINE=InnoDB;""")

    # ------------------ reportes (NUEVA TABLA) ------------------
    cur.execute("""CREATE TABLE reportes(
        id INT AUTO_INCREMENT PRIMARY KEY,
        equipo_id INT NOT NULL,
        usuario_id INT NOT NULL,
        titulo VARCHAR(255) NOT NULL,
        descripcion TEXT NOT NULL,
        tipo VARCHAR(50) DEFAULT 'problema',
        estado VARCHAR(50) DEFAULT 'abierto',
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (equipo_id) REFERENCES equipos(id) ON DELETE CASCADE,
        FOREIGN KEY (usuario_id) REFERENCES usuarios_ti(id) ON DELETE CASCADE
    ) ENGINE=InnoDB;""")

    connection.commit()
    print("Tablas creadas correctamente.")

def insertar_nas_predefinidos(connection):
    """Inserta los NAS predefinidos del sistema"""
    cur = connection.cursor()
    
    nas_predefinidos = [
        (1, '192.168.1.100', 2 * 1024**4, 'principal'),
        (2, '192.168.1.101', 2 * 1024**4, 'secundario'),
        (3, '192.168.1.102', 2 * 1024**4, 'respaldo')
    ]
    
    for nas_id, direccion, capacidad, rol in nas_predefinidos:
        cur.execute("""INSERT IGNORE INTO nas (id, direccion, capacidad_total, rol) 
                   VALUES (%s, %s, %s, %s)""", 
                   (nas_id, direccion, capacidad, rol))
    
    connection.commit()
    print("NAS predefinidos creados:")
    for nas_id, direccion, capacidad, rol in nas_predefinidos:
        capacidad_gb = capacidad / (1024**3)
        print(f"  - NAS {nas_id}: {direccion} ({rol}) - {capacidad_gb:.0f} GB")

def insertar_admin_principal(connection):
    """Inserta solo el usuario admin principal"""
    cur = connection.cursor()
    
    cur.execute("""INSERT IGNORE INTO usuarios_ti (nombre, email, role, password) 
               VALUES ('Jesus Santiago', 'jesus@ti.com', 'admin', 
               'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855');""")
    
    connection.commit()
    print("Usuario admin creado: Jesus Santiago (jesus@ti.com)")
    print("Contraseña: dejar vacío")

def main():
    crear_base_si_no_existe()
    conn = create_connection('respaldo_db')
    if not conn:
        print("No se pudo conectar.")
        return
    
    try:
        print("=== INICIALIZANDO SISTEMA ===")
        eliminar_tablas_existentes(conn)
        crear_tablas(conn)
        insertar_nas_predefinidos(conn)
        insertar_admin_principal(conn)
        
        print("\n" + "="*50)
        print("¡SISTEMA LISTO!")
        print("="*50)
        print("NAS predefinidos disponibles:")
        print("  - NAS 1: 192.168.1.100 (principal)")
        print("  - NAS 2: 192.168.1.101 (secundario)") 
        print("  - NAS 3: 192.168.1.102 (respaldo)")
        print("Capacidad: 2 TB cada uno\n")
        print("Usuario admin: Jesus Santiago")
        print("Email: jesus@ti.com")
        print("Contraseña: (dejar vacío)\n")
        print("Roles disponibles:")
        print("- admin: Acceso completo")
        print("- analista: Ver información y restaurar")
        print("- auxiliar: Solo consultas")
        print("="*50)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        close_connection(conn)

if __name__ == "__main__":
    main()
