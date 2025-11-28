from usuario_ti import UsuarioTI
from equipo import Equipo
from nas import NAS
from politica_backup import PoliticaBackup
from respaldo import Respaldo
from reporte import Reporte

class SistemaRespaldo:
    def __init__(self):
        pass

    # Registro
    def registrar_usuario(self, nombre, email, role='coordinador', password=None):
        return UsuarioTI.crear(nombre, email, role, password)

    def registrar_equipo(self, nombre, tipo, usuario, area, password=None):
        equipo = Equipo.crear(nombre, tipo, usuario, area)
        
        if password:
            from db_connection import get_conn
            conn = get_conn()
            try:
                cur = conn.cursor()
                import hashlib
                pwd_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
                cur.execute("UPDATE equipos SET password = %s WHERE id = %s", (pwd_hash, equipo.id))
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                cur.close()
                conn.close()
        
        return equipo

    def registrar_nas(self, direccion, capacidad_total, rol='principal'):
        for nas_id, nas_data in NAS.NAS_PREDEFINIDOS.items():
            if nas_data["direccion"] == direccion:
                raise ValueError(f"La dirección {direccion} está reservada para NAS predefinidos del sistema")
        return NAS.crear(direccion, capacidad_total, rol)

    def registrar_politica(self, frecuencia, retencion, destino_nas_id):
        nas = NAS.buscar_por_id(destino_nas_id)
        if not nas:
            raise ValueError(f"NAS con ID {destino_nas_id} no encontrado")
        return PoliticaBackup.crear(frecuencia, retencion, destino_nas_id)

    # Búsqueda
    def buscar_usuario(self, nombre):
        return UsuarioTI.buscar_por_nombre(nombre)

    def buscar_equipo(self, nombre):
        return Equipo.buscar_por_nombre(nombre)

    # Listados
    def listar_usuarios(self):
        return UsuarioTI.listar_todos()

    def listar_equipos(self):
        return Equipo.listar_todos()

    def listar_nas(self):
        return NAS.listar_todos()

    def listar_politicas(self):
        return PoliticaBackup.listar_todos()

    def listar_respaldos_por_equipo(self, equipo_nombre):
        equipo = self.buscar_equipo(equipo_nombre)
        if equipo is None:
            return "Equipo no encontrado."
        
        respaldos = Respaldo.listar_por_equipo(equipo.id)
        if not respaldos:
            return f"El equipo {equipo_nombre} no tiene respaldos."
        
        resultado = f"=== RESPALDOS DEL EQUIPO {equipo_nombre} ===\n\n"
        resultado += f"ID Único: {equipo.id_unico}\n"
        resultado += f"Username: {equipo.username}\n"
        resultado += f"Tipo: {equipo.tipo}\n"
        resultado += f"Usuario: {equipo.usuario}\n"
        resultado += f"Área: {equipo.area}\n\n"
        
        for respaldo in respaldos:
            nas = NAS.buscar_por_id(respaldo.nas_id)
            nas_info = f"NAS {nas.id} ({nas.direccion})" if nas else "NAS desconocido"
            fecha = respaldo.fecha_inicio.strftime("%Y-%m-%d %H:%M:%S") if hasattr(respaldo.fecha_inicio, 'strftime') else str(respaldo.fecha_inicio)
            
            resultado += f"• Respaldo ID: {respaldo.id}\n"
            resultado += f"  Ubicación: {nas_info}\n"
            resultado += f"  Estado: {respaldo.estado}\n"
            resultado += f"  Fecha: {fecha}\n\n"
        
        return resultado

    # Operaciones de respaldo
    def respaldar_equipo(self, nombre_equipo, nas_id):
        equipo = self.buscar_equipo(nombre_equipo)
        if equipo is None:
            return "Equipo no encontrado."
        
        nas = NAS.buscar_por_id(nas_id)
        if nas is None:
            return f"NAS con ID {nas_id} no encontrado."
        
        try:
            ok = equipo.respaldar(nas_id)
            if ok:
                return f"Respaldo creado para '{equipo.nombre}' en NAS {nas.direccion}."
            else:
                return f"No se pudo respaldar '{equipo.nombre}'. El NAS puede estar lleno."
        except Exception as e:
            return f"Error al respaldar: {e}"

    def restaurar_equipo(self, nombre_equipo):
        equipo = self.buscar_equipo(nombre_equipo)
        if equipo is None:
            return "Equipo no encontrado."
        try:
            ok = equipo.restaurar()
            if ok:
                return f"Restauración completada para '{equipo.nombre}'."
            else:
                return f"No se pudo restaurar '{equipo.nombre}'."
        except Exception as e:
            return f"Error al restaurar: {e}"

    def asignar_politica(self, nombre_equipo, politica_id, usuario):
        if not hasattr(usuario, 'role') or usuario.role != 'admin':
            return "Solo administradores pueden asignar políticas."
        equipo = self.buscar_equipo(nombre_equipo)
        if equipo is None:
            return "Equipo no encontrado."
        try:
            from db_connection import get_conn
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("UPDATE equipos SET politica_id = %s WHERE id = %s", (politica_id, equipo.id))
            conn.commit()
            cur.close()
            conn.close()
            
            return f"Política {politica_id} asignada a '{equipo.nombre}'."
        except Exception as e:
            return f"Error al asignar: {e}"

    def eliminar_nas(self, nas_id, usuario):
        if not hasattr(usuario, 'role') or usuario.role != 'admin':
            return "Solo administradores pueden eliminar NAS."
        
        nas = NAS.buscar_por_id(nas_id)
        if nas is None:
            return "NAS no encontrado."
        
        if nas.predefinido:
            return "No se pueden eliminar los NAS predefinidos del sistema."
        
        try:
            nas.eliminar()
            return f"NAS {nas.direccion} eliminado correctamente."
        except Exception as e:
            return f"Error al eliminar NAS: {str(e)}"

    #Crear reporte
    def crear_reporte(self, equipo_nombre, usuario, titulo, descripcion, tipo='problema'):
        equipo = self.buscar_equipo(equipo_nombre)
        if equipo is None:
            return "Equipo no encontrado."
        
        try:
            reporte = Reporte.crear(equipo.id, usuario.id, titulo, descripcion, tipo)
            return f"Reporte creado exitosamente: {reporte.titulo}"
        except Exception as e:
            return f"Error al crear reporte: {str(e)}"

    # Listar reportes (solo admin)
    def listar_reportes(self, usuario):
        if not hasattr(usuario, 'role') or usuario.role != 'admin':
            return "Solo administradores pueden ver todos los reportes."
        
        try:
            reportes = Reporte.listar_todos()
            if not reportes:
                return "No hay reportes en el sistema."
            
            resultado = "=== REPORTES DEL SISTEMA ===\n\n"
            for r in reportes:
                resultado += f"• Reporte #{r.id}\n"
                resultado += f"  Equipo: {r.nombre_equipo}\n"
                resultado += f"  Reportado por: {r.nombre_usuario} ({r.role_usuario})\n"
                resultado += f"  Tipo: {r.tipo}\n"
                resultado += f"  Estado: {r.estado}\n"
                resultado += f"  Fecha: {r.fecha_creacion}\n"
                resultado += f"  Título: {r.titulo}\n"
                resultado += f"  Descripción: {r.descripcion}\n\n"
            
            return resultado
        except Exception as e:
            return f"Error al listar reportes: {str(e)}"

    def _get_connection(self):
        from db_connection import get_conn
        return get_conn()
