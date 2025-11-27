from db_connection import create_connection, close_connection

def limpiar_tablas(connection):
    cursor = connection.cursor()
    # Limpiar en orden para respetar claves foráneas
    cursor.execute("DELETE FROM versiones_archivos;")
    cursor.execute("DELETE FROM respaldos;")
    cursor.execute("DELETE FROM politicas_backup;")
    cursor.execute("DELETE FROM equipos;")
    cursor.execute("DELETE FROM nas;")
    cursor.execute("DELETE FROM usuarios_ti;")
    connection.commit()
    cursor.close()
    print("Tablas limpiadas.")

def create_tables(connection):
    cursor = connection.cursor()

    # Tabla de usuarios_ti con role y password
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios_ti(
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        role VARCHAR(50) DEFAULT 'coordinador',
        password VARCHAR(255) NULL
    ) ENGINE=InnoDB;
    """)

    # Tabla de nas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS nas(
        id INT AUTO_INCREMENT PRIMARY KEY,
        direccion VARCHAR(255) NOT NULL,
        capacidad_total BIGINT NOT NULL,
        capacidad_usada BIGINT DEFAULT 0,
        rol VARCHAR(50) DEFAULT 'principal'
    ) ENGINE=InnoDB;
    """)

    # Tabla de equipos (como 'libros')
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS equipos(
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(255) NOT NULL,
        area VARCHAR(255) NOT NULL,
        politica_id INT NULL,
        FOREIGN KEY (politica_id) REFERENCES politicas_backup(id)
    ) ENGINE=InnoDB;
    """)

    # Tabla de politicas_backup
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS politicas_backup(
        id INT AUTO_INCREMENT PRIMARY KEY,
        frecuencia VARCHAR(50) NOT NULL,  -- diario, semanal, mensual
        retencion INT NOT NULL,
        destino_nas_id INT NOT NULL,
        FOREIGN KEY (destino_nas_id) REFERENCES nas(id)
    ) ENGINE=InnoDB;
    """)

    # Tabla de respaldos (como 'prestamos')
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS respaldos(
        id INT AUTO_INCREMENT PRIMARY KEY,
        equipo_id INT NOT NULL,
        nas_id INT NOT NULL,
        fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        estado VARCHAR(50) DEFAULT 'pendiente',
        FOREIGN KEY (equipo_id) REFERENCES equipos(id),
        FOREIGN KEY (nas_id) REFERENCES nas(id)
    ) ENGINE=InnoDB;
    """)

    # Tabla de versiones_archivos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS versiones_archivos(
        id INT AUTO_INCREMENT PRIMARY KEY,
        archivo_id VARCHAR(255) NOT NULL,
        version INT NOT NULL,
        tamano BIGINT NOT NULL,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        respaldo_id INT NOT NULL,
        FOREIGN KEY (respaldo_id) REFERENCES respaldos(id)
    ) ENGINE=InnoDB;
    """)

    connection.commit()
    print("Tablas creadas correctamente.")
    cursor.close()

def insertar_datos_ejemplo(connection):
    # Insertar NAS
    cursor = connection.cursor()
    cursor.execute("INSERT INTO nas (direccion, capacidad_total, rol) VALUES ('nas1.local', 10000000000, 'principal');")
    cursor.execute("INSERT INTO nas (direccion, capacidad_total, rol) VALUES ('nas2.local', 8000000000, 'secundario');")

    # Insertar políticas
    cursor.execute("INSERT INTO politicas_backup (frecuencia, retencion, destino_nas_id) VALUES ('diario', 7, 1);")
    cursor.execute("INSERT INTO politicas_backup (frecuencia, retencion, destino_nas_id) VALUES ('semanal', 30, 2);")

    # Insertar equipos
    cursor.execute("INSERT INTO equipos (nombre, area, politica_id) VALUES ('PC_Admin1', 'administrativa', 1);")
    cursor.execute("INSERT INTO equipos (nombre, area, politica_id) VALUES ('PC_Contable1', 'contable', 2);")

    # Insertar usuarios
    cursor.execute("INSERT INTO usuarios_ti (nombre, email, role) VALUES ('Admin1', 'admin@ti.com', 'admin');")
    cursor.execute("INSERT INTO usuarios_ti (nombre, email, role) VALUES ('Coord1', 'coord@ti.com', 'coordinador');")

    connection.commit()
    cursor.close()
    print("Datos de ejemplo insertados.")

def main():
    connection = create_connection('respaldo_db')
    if connection:
        try:
            create_tables(connection)
            limpiar_tablas(connection)
            insertar_datos_ejemplo(connection)
        except Exception as e:
            print(f"Error durante la ejecución: {e}")
        finally:
            close_connection(connection)

if __name__ == "__main__":
    main()