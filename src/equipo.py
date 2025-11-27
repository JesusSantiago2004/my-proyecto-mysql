from db_connection import get_conn
from respaldo import Respaldo
from nas import NAS

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

    def obtener_nas_respaldos(self):
        """Obtiene la lista de NAS donde tiene respaldos este equipo"""
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT DISTINCT n.id, n.direccion, n.rol 
                FROM nas n 
                INNER JOIN respaldos r ON n.id = r.nas_id 
                WHERE r.equipo_id = %s
            """, (self.id,))
            nas_list = cur.fetchall()
            return [f"NAS {nas[0]} ({nas[1]})" for nas in nas_list]
        finally:
            cur.close()
            conn.close()

    def obtener_info_respaldos(self):
        """Obtiene información formateada sobre los respaldos del equipo"""
        conn = get_conn()
        try:
            cur = conn.cursor()
            # Obtener el último respaldo
            cur.execute("""
                SELECT n.id, n.direccion, r.fecha_inicio 
                FROM nas n 
                INNER JOIN respaldos r ON n.id = r.nas_id 
                WHERE r.equipo_id = %s 
                ORDER BY r.fecha_inicio DESC 
                LIMIT 1
            """, (self.id,))
            ultimo_respaldo = cur.fetchone()
            
            # Contar total de respaldos
            cur.execute("SELECT COUNT(*) FROM respaldos WHERE equipo_id = %s", (self.id,))
            total_respaldos = cur.fetchone()[0]
            
            if ultimo_respaldo:
                nas_id, direccion, fecha = ultimo_respaldo
                return {
                    'tiene_respaldos': True,
                    'ultimo_nas': f"NAS {nas_id} ({direccion})",
                    'total_respaldos': total_respaldos,
                    'fecha_ultimo': fecha
                }
            else:
                return {
                    'tiene_respaldos': False,
                    'ultimo_nas': "Sin respaldos",
                    'total_respaldos': 0,
                    'fecha_ultimo': None
                }
        finally:
            cur.close()
            conn.close()

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
            equipos = []
            for r in rows:
                equipo = cls(r[0], r[1], r[2], r[3])
                equipos.append(equipo)
            return equipos
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