import re
from db_connection import get_conn

class Validador:
    @staticmethod
    def validar_email(email):
        """Valida el formato del email"""
        if not email or not email.strip():
            return False, "El email no puede estar vacío"
        
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(patron, email):
            return False, "El formato del email no es válido"
        
        return True, ""

    @staticmethod
    def validar_nombre_usuario(nombre):
        """Valida el nombre de usuario"""
        if not nombre or not nombre.strip():
            return False, "El nombre no puede estar vacío"
        
        if len(nombre) < 2 or len(nombre) > 50:
            return False, "El nombre debe tener entre 2 y 50 caracteres"
        
        # Solo letras, números, espacios y algunos caracteres especiales
        if not re.match(r'^[A-Za-z0-9áéíóúÁÉÍÓÚñÑ\s\-_.]+$', nombre):
            return False, "El nombre contiene caracteres no permitidos"
        
        return True, ""

    @staticmethod
    def validar_nombre_equipo(nombre):
        """Valida el nombre del equipo"""
        if not nombre or not nombre.strip():
            return False, "El nombre del equipo no puede estar vacío"
        
        if len(nombre) < 3 or len(nombre) > 50:
            return False, "El nombre debe tener entre 3 y 50 caracteres"
        
        # Debe empezar con letra, puede contener números, guiones y underscores
        if not re.match(r'^[A-Za-z][A-Za-z0-9\-_]*$', nombre):
            return False, "El nombre debe empezar con una letra y puede contener letras, números, guiones y underscores"
        
        return True, ""

    @staticmethod
    def verificar_usuario_duplicado(nombre, email):
        """Verifica si ya existe un usuario con el mismo nombre o email"""
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, nombre, email FROM usuarios_ti WHERE nombre = %s OR email = %s",
                (nombre, email)
            )
            existentes = cur.fetchall()
            duplicados = []
            for usuario in existentes:
                if usuario[1] == nombre:
                    duplicados.append(f"Nombre de usuario '{nombre}' ya existe")
                if usuario[2] == email:
                    duplicados.append(f"Email '{email}' ya está registrado")
            return duplicados
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def verificar_equipo_duplicado(nombre):
        """Verifica si ya existe un equipo con el mismo nombre"""
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id FROM equipos WHERE nombre = %s", (nombre,))
            return cur.fetchone() is not None
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def validar_ip_nas(ip):
        """Valida la dirección IP del NAS"""
        if not ip or not ip.strip():
            return False, "La dirección IP no puede estar vacía"
        
        patron = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(patron, ip):
            return False, "El formato de la IP no es válido"
        
        # Validar cada octeto
        octetos = ip.split('.')
        for octeto in octetos:
            if not 0 <= int(octeto) <= 255:
                return False, "La IP contiene octetos inválidos"
        
        return True, ""