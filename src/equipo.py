from db_connection import get_conn
from respaldo import Respaldo
from nas import NAS
import re
import random
import string

class Equipo:
    def __init__(self, id_, id_unico, nombre, tipo, usuario, area, username, politica_id=None):
        self.id = id_
        self.id_unico = id_unico
        self.nombre = nombre
        self.tipo = tipo
        self.usuario = usuario
        self.area = area
        self.username = username
        self.politica_id = politica_id

    @classmethod
    def validar_nombre_equipo(cls, nombre):
        """Valida el formato del nombre del equipo"""
        if not nombre or not nombre.strip():
            return False, "El nombre del equipo no puede estar vacío"
        
        if len(nombre) < 3 or len(nombre) > 50:
            return False, "El nombre debe tener entre 3 y 50 caracteres"
        
        return True, ""

    @classmethod
    def verificar_nombre_duplicado(cls, nombre):
        """Verifica si ya existe un equipo con el mismo nombre"""
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id FROM equipos WHERE nombre = %s", (nombre,))
            return cur.fetchone() is not None
        finally:
            cur.close()
            conn.close()

    @classmethod
    def generar_id_unico(cls, tipo, area):
        """Genera un ID único basado en tipo, área y número aleatorio"""
        # Prefijo basado en tipo
        prefijo_tipo = {
            'laptop': 'LAP',
            'pc': 'PC',
            'celular': 'CEL',
            'servidor': 'SRV',
            'tablet': 'TAB'
        }.get(tipo.lower(), 'EQP')
        
        # Prefijo de área (primeras 3 letras)
        prefijo_area = area[:3].upper()
        
        # Número aleatorio de 4 dígitos
        numero = ''.join(random.choices(string.digits, k=4))
        
        id_unico = f"{prefijo_tipo}-{prefijo_area}-{numero}"
        
        # Verificar si ya existe y regenerar si es necesario
        conn = get_conn()
        try:
            cur = conn.cursor()
            contador = 1
            id_final = id_unico
            
            while True:
                cur.execute("SELECT id FROM equipos WHERE id_unico = %s", (id_final,))
                if not cur.fetchone():
                    break
                numero = ''.join(random.choices(string.digits, k=4))
                id_final = f"{prefijo_tipo}-{prefijo_area}-{numero}"
                contador += 1
                if contador > 10:  # Límite de intentos
                    id_final = f"{prefijo_tipo}-{prefijo_area}-{numero}-{contador}"
            
            return id_final
        finally:
            cur.close()
            conn.close()

    @classmethod
    def generar_username(cls, usuario, area, tipo):
        """Genera un username único basado en usuario, área y tipo"""
        # Tomar primeras 3 letras del usuario (sin espacios)
        usuario_limpio = usuario.replace(' ', '').lower()[:3]
        
        # Prefijo de área
        area_prefijo = area[:2].lower()
        
        # Sufijo basado en tipo
        tipo_sufijo = {
            'laptop': 'lap',
            'pc': 'pc',
            'celular': 'cel',
            'servidor': 'srv',
            'tablet': 'tab'
        }.get(tipo.lower(), 'eqp')
        
        # Número aleatorio de 3 dígitos
        numero = ''.join(random.choices(string.digits, k=3))
        
        username = f"{usuario_limpio}{area_prefijo}{tipo_sufijo}{numero}"
        
        # Verificar si ya existe y regenerar si es necesario
        conn = get_conn()
        try:
            cur = conn.cursor()
            contador = 1
            username_final = username
            
            while True:
                cur.execute("SELECT id FROM equipos WHERE username = %s", (username_final,))
                if not cur.fetchone():
                    break
                numero = ''.join(random.choices(string.digits, k=3))
                username_final = f"{usuario_limpio}{area_prefijo}{tipo_sufijo}{numero}"
                contador += 1
                if contador > 5:  # Límite de intentos
                    username_final = f"{usuario_limpio}{area_prefijo}{tipo_sufijo}{numero}{contador}"
            
            return username_final
        finally:
            cur.close()
            conn.close()

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
    def crear(cls, nombre, tipo, usuario, area, politica_id=None):
        # Validar nombre del equipo
        es_valido, mensaje_error = cls.validar_nombre_equipo(nombre)
        if not es_valido:
            raise ValueError(mensaje_error)
        
        # Verificar duplicados
        if cls.verificar_nombre_duplicado(nombre):
            raise ValueError(f"Ya existe un equipo con el nombre '{nombre}'")
        
        # Generar ID único y username
        id_unico = cls.generar_id_unico(tipo, area)
        username = cls.generar_username(usuario, area, tipo)
        
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO equipos (id_unico, nombre, tipo, usuario, area, username, politica_id) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (id_unico, nombre, tipo, usuario, area, username, politica_id))
            conn.commit()
            eid = cur.lastrowid
            return cls(eid, id_unico, nombre, tipo, usuario, area, username, politica_id)
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
            conn.close()

    @classmethod
    def listar_todos(cls):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, id_unico, nombre, tipo, usuario, area, username, politica_id FROM equipos ORDER BY nombre")
            rows = cur.fetchall()
            equipos = []
            for r in rows:
                equipo = cls(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7])
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
            cur.execute("SELECT id, id_unico, nombre, tipo, usuario, area, username, politica_id FROM equipos WHERE nombre = %s", (nombre,))
            r = cur.fetchone()
            return cls(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]) if r else None
        finally:
            cur.close()
            conn.close()

    @classmethod
    def buscar_por_id_unico(cls, id_unico):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, id_unico, nombre, tipo, usuario, area, username, politica_id FROM equipos WHERE id_unico = %s", (id_unico,))
            r = cur.fetchone()
            return cls(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]) if r else None
        finally:
            cur.close()
            conn.close()

    def __str__(self):
        return f"Equipo {self.nombre} (ID: {self.id_unico}, Tipo: {self.tipo}, Usuario: {self.usuario}, Área: {self.area}, Username: {self.username})"