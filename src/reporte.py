# reporte.py
from db_connection import get_conn

class Reporte:
    def __init__(self, id_, equipo_id, usuario_id, titulo, descripcion, tipo='problema', estado='abierto'):
        self.id = id_
        self.equipo_id = equipo_id
        self.usuario_id = usuario_id
        self.titulo = titulo
        self.descripcion = descripcion
        self.tipo = tipo
        self.estado = estado

    @classmethod
    def crear(cls, equipo_id, usuario_id, titulo, descripcion, tipo='problema'):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO reportes (equipo_id, usuario_id, titulo, descripcion, tipo) VALUES (%s, %s, %s, %s, %s)",
                (equipo_id, usuario_id, titulo, descripcion, tipo)
            )
            conn.commit()
            rid = cur.lastrowid
            return cls(rid, equipo_id, usuario_id, titulo, descripcion, tipo, 'abierto')
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
            conn.close()

    @classmethod
    def listar_todos(cls):
        """Lista todos los reportes del sistema con información del usuario"""
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT r.id, r.equipo_id, r.usuario_id, r.titulo, r.descripcion, 
                       r.tipo, r.estado, r.fecha_creacion,
                       e.nombre as equipo_nombre,
                       u.nombre as usuario_nombre, u.role as usuario_role
                FROM reportes r
                JOIN equipos e ON r.equipo_id = e.id
                JOIN usuarios_ti u ON r.usuario_id = u.id
                ORDER BY r.fecha_creacion DESC
            """)
            rows = cur.fetchall()
            reportes = []
            for r in rows:
                reporte = cls(r[0], r[1], r[2], r[3], r[4], r[5], r[6])
                reporte.fecha_creacion = r[7]
                reporte.nombre_equipo = r[8]
                reporte.nombre_usuario = r[9]
                reporte.role_usuario = r[10]
                reportes.append(reporte)
            return reportes
        finally:
            cur.close()
            conn.close()

    def __str__(self):
        return f"Reporte {self.id}: {self.titulo} ({self.estado})"