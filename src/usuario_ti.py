from db_connection import get_conn
import hashlib
import re

def hash_password(password: str) -> str:
    if password is None:
        return None
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def validar_email(email: str) -> bool:
    """Valida el formato del email"""
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron, email) is not None

class UsuarioTI:
    def __init__(self, id_, nombre, email, role='coordinador'):
        self.id = id_
        self.nombre = nombre
        self.email = email
        self.role = role

    @classmethod
    def verificar_duplicados(cls, nombre, email):
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

    @classmethod
    def crear(cls, nombre, email, role='coordinador', password=None):
        # Validaciones
        if not nombre or not nombre.strip():
            raise ValueError("El nombre no puede estar vacío")
        
        if not email or not email.strip():
            raise ValueError("El email no puede estar vacío")
        
        if not validar_email(email):
            raise ValueError("El formato del email no es válido")
        
        if role not in ['coordinador', 'admin', 'analista', 'auxiliar']:
            raise ValueError("Rol debe ser 'coordinador', 'admin', 'analista' o 'auxiliar'")
        
        # Verificar duplicados
        duplicados = cls.verificar_duplicados(nombre, email)
        if duplicados:
            raise ValueError(" | ".join(duplicados))
        
        conn = get_conn()
        try:
            cur = conn.cursor()
            pwd_hash = hash_password(password) if password else None
            cur.execute(
                "INSERT INTO usuarios_ti (nombre, email, role, password) VALUES (%s, %s, %s, %s)",
                (nombre, email, role, pwd_hash)
            )
            conn.commit()
            uid = cur.lastrowid
            if role == 'admin':
                return AdministradorTI(uid, nombre, email, role)
            elif role == 'coordinador':
                return CoordinadorTI(uid, nombre, email, role)
            return cls(uid, nombre, email, role)
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
            cur.execute("SELECT id, nombre, email, role FROM usuarios_ti ORDER BY nombre")
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
            cur.execute("SELECT id, nombre, email, role FROM usuarios_ti WHERE nombre = %s", (nombre,))
            r = cur.fetchone()
            if r:
                if r[3] == 'admin':
                    return AdministradorTI(r[0], r[1], r[2], r[3])
                elif r[3] == 'coordinador':
                    return CoordinadorTI(r[0], r[1], r[2], r[3])
                return cls(r[0], r[1], r[2], r[3])
            return None
        finally:
            cur.close()
            conn.close()

    @classmethod
    def buscar_por_email(cls, email):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, nombre, email, role FROM usuarios_ti WHERE email = %s", (email,))
            r = cur.fetchone()
            if r:
                if r[3] == 'admin':
                    return AdministradorTI(r[0], r[1], r[2], r[3])
                elif r[3] == 'coordinador':
                    return CoordinadorTI(r[0], r[1], r[2], r[3])
                return cls(r[0], r[1], r[2], r[3])
            return None
        finally:
            cur.close()
            conn.close()

    @classmethod
    def autenticar(cls, nombre, password):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, nombre, email, role, password FROM usuarios_ti WHERE nombre = %s", (nombre,))
            r = cur.fetchone()
            if not r:
                return None

            stored_hash = r[4]
            input_hash = hash_password(password) if password else None

            # Acepta contraseña vacía o NULL
            if stored_hash in (None, '', 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'):
                if not password or password == "":
                    if r[3] == 'admin':
                        return AdministradorTI(r[0], r[1], r[2], r[3])
                    elif r[3] == 'coordinador':
                        return CoordinadorTI(r[0], r[1], r[2], r[3])
                    return cls(r[0], r[1], r[2], r[3])

            # Caso normal con contraseña
            if input_hash == stored_hash:
                if r[3] == 'admin':
                    return AdministradorTI(r[0], r[1], r[2], r[3])
                elif r[3] == 'coordinador':
                    return CoordinadorTI(r[0], r[1], r[2], r[3])
                return cls(r[0], r[1], r[2], r[3])

            return None
        finally:
            cur.close()
            conn.close()

    def generarReporte(self):
        return f"Reporte general por {self.nombre} (rol: {self.role})"

    def __str__(self):
        return f"{self.nombre} ({self.role}, {self.email})"

class AdministradorTI(UsuarioTI):
    def asignarPolitica(self, equipo_id, politica_id):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("UPDATE equipos SET politica_id = %s WHERE id = %s", (politica_id, equipo_id))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise
        finally:
            cur.close()
            conn.close()

    def generarReporte(self):
        return f"Reporte filtrado por área/equipo por Administrador {self.nombre}"

class CoordinadorTI(UsuarioTI):
    def generarReporte(self):
        return f"Reporte global por Coordinador {self.nombre}"