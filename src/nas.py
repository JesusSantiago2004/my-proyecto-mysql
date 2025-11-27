from db_connection import get_conn

class NAS:
    def __init__(self, id_, direccion, capacidad_total, capacidad_usada=0, rol='principal'):
        self.id = id_
        self.direccion = direccion
        self.capacidad_total = capacidad_total
        self.capacidad_usada = capacidad_usada
        self.rol = rol

    def almacenarRespaldo(self, tamano):
        if self.capacidad_usada + tamano > self.capacidad_total:
            return False
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("UPDATE nas SET capacidad_usada = capacidad_usada + %s WHERE id = %s", (tamano, self.id))
            conn.commit()
            self.capacidad_usada += tamano
            return True
        except Exception as e:
            conn.rollback()
            raise
        finally:
            cur.close()
            conn.close()

    def sincronizarConOtroNAS(self, otro_nas_id):
        # Simulación de sincronización
        return True

    @classmethod
    def crear(cls, direccion, capacidad_total, rol='principal'):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO nas (direccion, capacidad_total, rol) VALUES (%s, %s, %s)", (direccion, capacidad_total, rol))
            conn.commit()
            nid = cur.lastrowid
            return cls(nid, direccion, capacidad_total, 0, rol)
        finally:
            cur.close()
            conn.close()

    @classmethod
    def listar_todos(cls):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, direccion, capacidad_total, capacidad_usada, rol FROM nas")
            rows = cur.fetchall()
            return [cls(r[0], r[1], r[2], r[3], r[4]) for r in rows]
        finally:
            cur.close()
            conn.close()

    @classmethod
    def buscar_por_id(cls, id_):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, direccion, capacidad_total, capacidad_usada, rol FROM nas WHERE id = %s", (id_,))
            r = cur.fetchone()
            return cls(r[0], r[1], r[2], r[3], r[4]) if r else None
        finally:
            cur.close()
            conn.close()

    def __str__(self):
        return f"NAS {self.direccion} ({self.rol}, Usado: {self.capacidad_usada}/{self.capacidad_total})"