# Sistema de Gestión de Respaldos en NAS Synology  
**Optativa - Ingeniería en Software - Politécnica Santa Rosa**  
**Jesús Santiago Serrano Ruiz - ISW-25**

## Descripción
Sistema centralizado de gestión y automatización de respaldos hacia dos servidores NAS Synology, aplicando principios de POO (abstracción, encapsulamiento, herencia y polimorfismo).

## Características implementadas
- Asignación de equipos a rutas de respaldo (NAS 1 / NAS 2)
- Políticas de backup (diario, semanal, mensual) con retención
- Monitoreo en tiempo real del estado y espacio
- Registro automático de respaldos y versiones de archivos
- Restauración de equipos específicos
- Sincronización entre NAS (simulada)
- Roles: AdministradorTI y CoordinadorTI con herencia
- Autenticación segura con hash SHA-256
- Interfaz gráfica con Tkinter y control de permisos

## Tecnologías
- Python 3.11
- MySQL + Connection Pooling
- Tkinter (GUI)
- dotenv para variables de entorno

## Instalación
```bash
git clone https://github.com/tu-usuario/respaldo-nas.git
cd respaldo-nas
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python src/mysql_env.py    # Crea DB y datos de ejemplo
python src/execute.py      # Inicia la aplicación