from usuario_ti import UsuarioTI
from equipo import Equipo
from nas import NAS
from politica_backup import PoliticaBackup
from respaldo import Respaldo

class SistemaRespaldo:
    def __init__(self):
        pass

    # Registro
    def registrar_usuario(self, nombre, email, role='coordinador', password=None):
        return UsuarioTI.crear(nombre, email, role, password)

    def registrar_equipo(self, nombre, area):
        return Equipo.crear(nombre, area)

    def registrar_nas(self, direccion, capacidad_total, rol='principal'):
        return NAS.crear(direccion, capacidad_total, rol)

    def registrar_politica(self, frecuencia, retencion, destino_nas_id):
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
        """Lista todos los respaldos de un equipo específico"""
        equipo = self.buscar_equipo(equipo_nombre)
        if equipo is None:
            return "Equipo no encontrado."
        
        respaldos = Respaldo.listar_por_equipo(equipo.id)
        if not respaldos:
            return f"El equipo {equipo_nombre} no tiene respaldos."
        
        resultado = f"=== RESPALDOS DEL EQUIPO {equipo_nombre} ===\n\n"
        for respaldo in respaldos:
            # Obtener información del NAS
            nas = NAS.buscar_por_id(respaldo.nas_id)
            nas_info = f"NAS {nas.id} ({nas.direccion})" if nas else "NAS desconocido"
            
            # Formatear fecha
            fecha = respaldo.fecha_inicio.strftime("%Y-%m-%d %H:%M:%S") if hasattr(respaldo.fecha_inicio, 'strftime') else str(respaldo.fecha_inicio)
            
            resultado += f"• Respaldo ID: {respaldo.id}\n"
            resultado += f"  Ubicación: {nas_info}\n"
            resultado += f"  Estado: {respaldo.estado}\n"
            resultado += f"  Fecha: {fecha}\n"
            resultado += "\n"
        
        return resultado

    # Operaciones de respaldo
    def respaldar_equipo(self, nombre_equipo, nas_id):
        equipo = self.buscar_equipo(nombre_equipo)
        if equipo is None:
            return "Equipo no encontrado."
        try:
            ok = equipo.respaldar(nas_id)
            if ok:
                # Obtener información del NAS para el mensaje
                nas = NAS.buscar_por_id(nas_id)
                nas_info = f"NAS {nas.id} ({nas.direccion})" if nas else f"NAS {nas_id}"
                return f"Respaldo creado para '{equipo.nombre}' en {nas_info}."
            else:
                return f"No se pudo respaldar '{equipo.nombre}'."
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
            # Actualizar directamente en la base de datos
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