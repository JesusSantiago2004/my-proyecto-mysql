from db_connection import get_conn
from respaldo import Respaldo
from nas import NAS

class PoliticaBackup:
    def __init__(self, id_, frecuencia, retencion, destino_nas_id):
        self.id = id_
        self.frecuencia = frecuencia
        self.retencion = retencion
        self.destino_nas_id = destino_nas_id

    def aplicarBackup(self, equipo_id):
        nas = NAS.buscar_por_id(self.destino_nas_id)
        if nas:
            return Respaldo.crear(equipo_id, self.destino_nas_id)
        return None

    @classmethod
    def crear(cls, frecuencia, retencion, destino_nas_id):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO politicas_backup (frecuencia, retencion, destino_nas_id) VALUES (%s, %s, %s)", (frecuencia, retencion, destino_nas_id))
            conn.commit()
            pid = cur.lastrowid
            return cls(pid, frecuencia, retencion, destino_nas_id)
        finally:
            cur.close()
            conn.close()

    @classmethod
    def listar_todos(cls):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, frecuencia, retencion, destino_nas_id FROM politicas_backup")
            rows = cur.fetchall()
            return [cls(r[0], r[1], r[2], r[3]) for r in rows]
        finally:
            cur.close()
            conn.close()

    def __str__(self):
        return f"Política {self.id}: {self.frecuencia}, Retención: {self.retencion} días, NAS: {self.destino_nas_id}"