from db_connection import get_conn

class NAS:
    # NAS predefinidos
    NAS_PREDEFINIDOS = {
        1: {"direccion": "192.168.1.100", "capacidad_total": 2 * 1024**4, "rol": "principal"},
        2: {"direccion": "192.168.1.101", "capacidad_total": 2 * 1024**4, "rol": "secundario"},
        3: {"direccion": "192.168.1.102", "capacidad_total": 2 * 1024**4, "rol": "respaldo"}
    }

    def __init__(self, id_, direccion, capacidad_total, capacidad_usada=0, rol='principal', predefinido=False):
        self.id = id_
        self.direccion = direccion
        self.capacidad_total = capacidad_total
        self.capacidad_usada = capacidad_usada
        self.rol = rol
        self.predefinido = predefinido

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

    def obtener_equipos_con_respaldo(self):
        """Obtiene la lista de equipos que tienen respaldos en este NAS"""
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT DISTINCT e.id_unico, e.nombre, e.tipo, e.usuario, e.area, e.username
                FROM equipos e 
                INNER JOIN respaldos r ON e.id = r.equipo_id 
                WHERE r.nas_id = %s
                ORDER BY e.nombre
            """, (self.id,))
            equipos = cur.fetchall()
            return equipos
        finally:
            cur.close()
            conn.close()

    def obtener_info_equipos(self):
        """Obtiene información detallada de los equipos en este NAS"""
        equipos = self.obtener_equipos_con_respaldo()
        if not equipos:
            return "No hay equipos con respaldos en este NAS"
        
        info = f"=== EQUIPOS EN NAS {self.direccion} ===\n\n"
        for equipo in equipos:
            id_unico, nombre, tipo, usuario, area, username = equipo
            info += f"• {nombre}\n"
            info += f"  ID Único: {id_unico}\n"
            info += f"  Tipo: {tipo}\n"
            info += f"  Usuario: {usuario}\n"
            info += f"  Área: {area}\n"
            info += f"  Username: {username}\n"
            info += "\n"
        
        return info

    @classmethod
    def crear(cls, direccion, capacidad_total, rol='principal'):
        # Verificar si ya existe un NAS con la misma dirección
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id FROM nas WHERE direccion = %s", (direccion,))
            if cur.fetchone():
                raise ValueError(f"Ya existe un NAS con la dirección {direccion}")
            
            cur.execute("INSERT INTO nas (direccion, capacidad_total, rol) VALUES (%s, %s, %s)", (direccion, capacidad_total, rol))
            conn.commit()
            nid = cur.lastrowid
            return cls(nid, direccion, capacidad_total, 0, rol, False)
        finally:
            cur.close()
            conn.close()

    @classmethod
    def listar_todos(cls):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, direccion, capacidad_total, capacidad_usada, rol FROM nas ORDER BY id")
            rows = cur.fetchall()
            nas_list = []
            for r in rows:
                # Verificar si es predefinido
                predefinido = r[0] in cls.NAS_PREDEFINIDOS
                nas_list.append(cls(r[0], r[1], r[2], r[3], r[4], predefinido))
            return nas_list
        finally:
            cur.close()
            conn.close()

    @classmethod
    def buscar_por_id(cls, id_):
        # Primero verificar si es un NAS predefinido
        if id_ in cls.NAS_PREDEFINIDOS:
            nas_data = cls.NAS_PREDEFINIDOS[id_]
            # Obtener capacidad_usada de la base de datos si existe
            conn = get_conn()
            try:
                cur = conn.cursor()
                cur.execute("SELECT capacidad_usada FROM nas WHERE id = %s", (id_,))
                result = cur.fetchone()
                capacidad_usada = result[0] if result else 0
                return cls(id_, nas_data["direccion"], nas_data["capacidad_total"], capacidad_usada, nas_data["rol"], True)
            finally:
                cur.close()
                conn.close()
        
        # Si no es predefinido, buscar en la base de datos
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, direccion, capacidad_total, capacidad_usada, rol FROM nas WHERE id = %s", (id_,))
            r = cur.fetchone()
            return cls(r[0], r[1], r[2], r[3], r[4], False) if r else None
        finally:
            cur.close()
            conn.close()

    def eliminar(self):
        """Solo permite eliminar NAS que no son predefinidos"""
        if self.predefinido:
            raise ValueError("No se pueden eliminar los NAS predefinidos del sistema")
        
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM nas WHERE id = %s", (self.id,))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise
        finally:
            cur.close()
            conn.close()

    def actualizar(self, direccion=None, capacidad_total=None, rol=None):
        """Solo permite actualizar NAS que no son predefinidos"""
        if self.predefinido:
            raise ValueError("No se pueden modificar los NAS predefinidos del sistema")
        
        conn = get_conn()
        try:
            cur = conn.cursor()
            updates = []
            params = []
            
            if direccion is not None:
                updates.append("direccion = %s")
                params.append(direccion)
            if capacidad_total is not None:
                updates.append("capacidad_total = %s")
                params.append(capacidad_total)
            if rol is not None:
                updates.append("rol = %s")
                params.append(rol)
            
            if updates:
                params.append(self.id)
                cur.execute(f"UPDATE nas SET {', '.join(updates)} WHERE id = %s", params)
                conn.commit()
                
                # Actualizar objeto
                if direccion: self.direccion = direccion
                if capacidad_total: self.capacidad_total = capacidad_total
                if rol: self.rol = rol
                
            return True
        except Exception as e:
            conn.rollback()
            raise
        finally:
            cur.close()
            conn.close()

    def __str__(self):
        # Obtener información de equipos
        equipos = self.obtener_equipos_con_respaldo()
        total_equipos = len(equipos) if equipos else 0
        
        tipo = "PREDEFINIDO" if self.predefinido else "personalizado"
        return f"NAS {self.direccion} ({self.rol}, {tipo}, Usado: {self.capacidad_usada}/{self.capacidad_total}, Equipos: {total_equipos})"