from db_connection import get_conn

class VersionArchivo:
    def __init__(self, id_, archivo_id, version, tamano, fecha, respaldo_id):
        self.id = id_
        self.archivo_id = archivo_id
        self.version = version
        self.tamano = tamano
        self.fecha = fecha
        self.respaldo_id = respaldo_id

    @classmethod
    def crear(cls, archivo_id, version, tamano, respaldo_id):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO versiones_archivos (archivo_id, version, tamano, respaldo_id) VALUES (%s, %s, %s, %s)",
                (archivo_id, version, tamano, respaldo_id)
            )
            conn.commit()
            vid = cur.lastrowid
            return cls(vid, archivo_id, version, tamano, 'NOW()', respaldo_id)
        finally:
            cur.close()
            conn.close()

    def restaurar(self):
        # Simular restauración
        return True

    def __str__(self):
        return f"Versión {self.version} de {self.archivo_id} (Tamaño: {self.tamano}, Respaldo: {self.respaldo_id})"