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

    # Operaciones de respaldo
    def respaldar_equipo(self, nombre_equipo, nas_id):
        equipo = self.buscar_equipo(nombre_equipo)
        if equipo is None:
            return "Equipo no encontrado."
        try:
            ok = equipo.respaldar(nas_id)
            if ok:
                return f"Respaldo creado para '{equipo.nombre}' en NAS {nas_id}."
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
        if not isinstance(usuario, AdministradorTI):
            return "Solo administradores pueden asignar políticas."
        equipo = self.buscar_equipo(nombre_equipo)
        if equipo is None:
            return "Equipo no encontrado."
        try:
            ok = usuario.asignarPolitica(equipo.id, politica_id)
            if ok:
                return f"Política {politica_id} asignada a '{equipo.nombre}'."
            else:
                return "No se pudo asignar la política."
        except Exception as e:
            return f"Error al asignar: {e}"