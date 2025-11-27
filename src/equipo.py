from db_connection import get_conn
from respaldo import Respaldo

class Equipo:
    def __init__(self, id_, nombre, area, politica_id=None):
        self.id = id_
        self.nombre = nombre
        self.area = area
        self.politica_id = politica_id

    def respaldar(self, nas_id):
        conn = get_conn()
        try:
            cur = conn.cursor()
            respaldo = Respaldo.crear(self.id, nas_id)
            if respaldo:
                # Simular almacenamiento (actualizar NAS)
                nas = NAS.buscar_por_id(nas_id)
                if nas:
                    nas.almacenarRespaldo(1000000)  # Simular tamaño 1MB
                return True
            return False
        except Exception as e:
            conn.rollback()
            raise
        finally:
            cur.close()
            conn.close()

    def restaurar(self):
        # Simular restauración
        return True

    @classmethod
    def crear(cls, nombre, area, politica_id=None):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO equipos (nombre, area, politica_id) VALUES (%s, %s, %s)", (nombre, area, politica_id))
            conn.commit()
            eid = cur.lastrowid
            return cls(eid, nombre, area, politica_id)
        finally:
            cur.close()
            conn.close()

    @classmethod
    def listar_todos(cls):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, nombre, area, politica_id FROM equipos ORDER BY nombre")
            rows = cur.fetchall()
            return [cls(r[0], r[1], r[2], r[3]) for r in rows]
        finally:
            cur.close()
            conn.close()

    @classmethod
    def buscar_por_nombre(cls, nombre):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, nombre, area, politica_id FROM equipos WHERE nombre = %s", (nombre,))
            r = cur.fetchone()
            return cls(r[0], r[1], r[2], r[3]) if r else None
        finally:
            cur.close()
            conn.close()

    def __str__(self):
        return f"Equipo {self.nombre} (Área: {self.area}, Política: {self.politica_id or 'Ninguna'})"