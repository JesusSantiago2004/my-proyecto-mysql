from db_connection import get_conn

class Respaldo:
    def __init__(self, id_, equipo_id, nas_id, fecha_inicio, estado='pendiente'):
        self.id = id_
        self.equipo_id = equipo_id
        self.nas_id = nas_id
        self.fecha_inicio = fecha_inicio
        self.estado = estado

    @classmethod
    def crear(cls, equipo_id, nas_id):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO respaldos (equipo_id, nas_id) VALUES (%s, %s)",
                (equipo_id, nas_id)
            )
            conn.commit()
            rid = cur.lastrowid
            # Simular versión de archivo
            cur.execute(
                "INSERT INTO versiones_archivos (archivo_id, version, tamano, respaldo_id) VALUES (%s, %s, %s, %s)",
                (f"arch_{rid}", 1, 1000000, rid)
            )
            conn.commit()
            return cls(rid, equipo_id, nas_id, 'NOW()', 'completado')
        except Exception as e:
            conn.rollback()
            raise
        finally:
            cur.close()
            conn.close()

    def monitorear(self):
        # Simular monitoreo
        return self.estado

    @classmethod
    def listar_por_equipo(cls, equipo_id):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, equipo_id, nas_id, fecha_inicio, estado FROM respaldos WHERE equipo_id = %s", (equipo_id,))
            rows = cur.fetchall()
            return [cls(r[0], r[1], r[2], r[3], r[4]) for r in rows]
        finally:
            cur.close()
            conn.close()

    def __str__(self):
        return f"Respaldo {self.id} para Equipo {self.equipo_id} en NAS {self.nas_id} ({self.estado})"