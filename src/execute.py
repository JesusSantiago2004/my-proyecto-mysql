import sys
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import hashlib
import re

from sistema_respaldo import SistemaRespaldo
from usuario_ti import UsuarioTI

sis = SistemaRespaldo()
current_user = None

ADMIN_SECRET_CODE = "ADMIN2024"

# Colores simples y profesionales
COLOR_PRIMARIO = "#2c3e50"
COLOR_SECUNDARIO = "#3498db"
COLOR_FONDO = "#f8f9fa"
COLOR_TEXTO = "#2c3e50"
COLOR_BORDE = "#dee2e6"

def centrar_ventana(ventana, ancho=1000, alto=700):
    pantalla_ancho = ventana.winfo_screenwidth()
    pantalla_alto = ventana.winfo_screenheight()
    x = (pantalla_ancho // 2) - (ancho // 2)
    y = (pantalla_alto // 2) - (alto // 2)
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

def crear_ventana_login():
    """Ventana de login simple y limpia"""
    login_window = tk.Toplevel(root)
    login_window.title("Iniciar Sesión")
    login_window.geometry("350x400")
    login_window.configure(bg=COLOR_FONDO)
    login_window.resizable(False, False)
    login_window.transient(root)
    login_window.grab_set()
    
    # Frame principal
    main_frame = tk.Frame(login_window, bg=COLOR_FONDO, padx=30, pady=40)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Título
    title_label = tk.Label(main_frame, text="Sistema de Respaldos", 
                          font=('Arial', 18, 'bold'), 
                          bg=COLOR_FONDO, fg=COLOR_PRIMARIO)
    title_label.pack(pady=(0, 30))
    
    # Formulario de login
    form_frame = tk.Frame(main_frame, bg=COLOR_FONDO)
    form_frame.pack(fill=tk.X, pady=(0, 20))
    
    # Usuario
    tk.Label(form_frame, text="Usuario:", font=('Arial', 10), 
            bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(anchor='w', pady=(0, 5))
    usuario_entry = ttk.Entry(form_frame, width=25, font=('Arial', 10))
    usuario_entry.pack(fill=tk.X, pady=(0, 15))
    
    # Contraseña
    tk.Label(form_frame, text="Contraseña:", font=('Arial', 10), 
            bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(anchor='w', pady=(0, 5))
    password_entry = ttk.Entry(form_frame, width=25, show='•', font=('Arial', 10))
    password_entry.pack(fill=tk.X, pady=(0, 25))
    
    # Botones
    button_frame = tk.Frame(main_frame, bg=COLOR_FONDO)
    button_frame.pack(fill=tk.X, pady=(0, 10))
    
    def hacer_login():
        usuario = usuario_entry.get().strip()
        password = password_entry.get()
        
        if not usuario:
            messagebox.showerror("Error", "Por favor ingresa tu usuario")
            return
        
        user = UsuarioTI.autenticar(usuario, password)
        if user:
            global current_user
            current_user = user
            messagebox.showinfo("Bienvenido", f"¡Hola {user.nombre}!")
            login_window.destroy()
            actualizar_info_usuario()
            ajustar_menu_por_rol()
            # Mostrar lista de equipos al iniciar
            listar_equipos()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
            password_entry.delete(0, tk.END)
    
    login_btn = ttk.Button(button_frame, text="Iniciar Sesión", command=hacer_login)
    login_btn.pack(fill=tk.X, pady=(0, 10))
    
    def registrar_nuevo():
        login_window.destroy()
        crear_ventana_registro()
    
    register_btn = ttk.Button(button_frame, text="Crear Cuenta", command=registrar_nuevo)
    register_btn.pack(fill=tk.X)
    
    # Enter para login
    login_window.bind('<Return>', lambda e: hacer_login())
    
    usuario_entry.focus()
    centrar_ventana(login_window, 350, 400)
    
    return login_window

def crear_ventana_registro():
    """Ventana de registro simple"""
    reg_window = tk.Toplevel(root)
    reg_window.title("Registrar Usuario")
    reg_window.geometry("400x450")
    reg_window.configure(bg=COLOR_FONDO)
    reg_window.resizable(False, False)
    reg_window.transient(root)
    reg_window.grab_set()
    
    # Frame principal
    main_frame = tk.Frame(reg_window, bg=COLOR_FONDO, padx=30, pady=30)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Título
    title_label = tk.Label(main_frame, text="Registrar Usuario", 
                          font=('Arial', 16, 'bold'), 
                          bg=COLOR_FONDO, fg=COLOR_PRIMARIO)
    title_label.pack(pady=(0, 20))
    
    # Formulario de registro
    form_frame = tk.Frame(main_frame, bg=COLOR_FONDO)
    form_frame.pack(fill=tk.X, pady=(0, 20))
    
    # Nombre
    tk.Label(form_frame, text="Nombre completo:", font=('Arial', 9), 
            bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(anchor='w', pady=(0, 5))
    nombre_entry = ttk.Entry(form_frame, width=30, font=('Arial', 10))
    nombre_entry.pack(fill=tk.X, pady=(0, 10))
    
    # Email
    tk.Label(form_frame, text="Email:", font=('Arial', 9), 
            bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(anchor='w', pady=(0, 5))
    email_entry = ttk.Entry(form_frame, width=30, font=('Arial', 10))
    email_entry.pack(fill=tk.X, pady=(0, 10))
    
    # Rol
    tk.Label(form_frame, text="Rol:", font=('Arial', 9), 
            bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(anchor='w', pady=(0, 5))
    rol_var = tk.StringVar(value="auxiliar")
    rol_combo = ttk.Combobox(form_frame, textvariable=rol_var, 
                            values=["auxiliar", "analista", "admin"], 
                            state="readonly", font=('Arial', 10))
    rol_combo.pack(fill=tk.X, pady=(0, 10))
    
    # Contraseña
    tk.Label(form_frame, text="Contraseña:", font=('Arial', 9), 
            bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(anchor='w', pady=(0, 5))
    password_entry = ttk.Entry(form_frame, width=30, show='•', font=('Arial', 10))
    password_entry.pack(fill=tk.X, pady=(0, 10))
    
    def registrar_usuario():
        nombre = nombre_entry.get().strip()
        email = email_entry.get().strip()
        role = rol_var.get()
        password = password_entry.get()
        
        # Validaciones básicas
        if not nombre or not email:
            messagebox.showerror("Error", "Nombre y email son obligatorios")
            return
        
        if role == 'admin':
            codigo = simpledialog.askstring("Código Admin", 
                                          "Código secreto para admin:", 
                                          show='*', parent=reg_window)
            if codigo != ADMIN_SECRET_CODE:
                messagebox.showerror("Error", "Código incorrecto")
                return
        
        try:
            user = sis.registrar_usuario(nombre, email, role, password)
            global current_user
            current_user = user
            messagebox.showinfo("Éxito", f"Usuario {user.nombre} registrado")
            reg_window.destroy()
            actualizar_info_usuario()
            ajustar_menu_por_rol()
            listar_equipos()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Error al registrar: {str(e)}")
    
    def volver_login():
        reg_window.destroy()
        crear_ventana_login()
    
    # Botones
    button_frame = tk.Frame(main_frame, bg=COLOR_FONDO)
    button_frame.pack(fill=tk.X, pady=(0, 10))
    
    ttk.Button(button_frame, text="Registrar", command=registrar_usuario).pack(fill=tk.X, pady=(0, 5))
    ttk.Button(button_frame, text="Volver al Login", command=volver_login).pack(fill=tk.X)
    
    reg_window.bind('<Return>', lambda e: registrar_usuario())
    nombre_entry.focus()
    centrar_ventana(reg_window, 400, 450)
    
    return reg_window

def crear_dialogo_simple(titulo, campos, callback_confirmar, ancho=350):
    """Crea un diálogo simple"""
    dialog = tk.Toplevel(root)
    dialog.title(titulo)
    dialog.configure(bg=COLOR_FONDO)
    dialog.resizable(False, False)
    dialog.transient(root)
    dialog.grab_set()
    
    main_frame = tk.Frame(dialog, bg=COLOR_FONDO, padx=20, pady=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Campos del formulario
    entries = {}
    for campo in campos:
        tk.Label(main_frame, text=campo['text'], font=('Arial', 9), 
                bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(anchor='w', pady=(5, 2))
        
        if campo['tipo'] == 'entry':
            entry = ttk.Entry(main_frame, width=30, font=('Arial', 10))
            entry.pack(fill=tk.X, pady=(0, 10))
            if 'default' in campo:
                entry.insert(0, campo['default'])
            entries[campo['name']] = entry
        elif campo['tipo'] == 'combobox':
            var = tk.StringVar(value=campo['values'][0] if campo['values'] else '')
            combo = ttk.Combobox(main_frame, textvariable=var, 
                               values=campo['values'], state="readonly",
                               font=('Arial', 10))
            combo.pack(fill=tk.X, pady=(0, 10))
            entries[campo['name']] = var
    
    # Botones
    button_frame = tk.Frame(main_frame, bg=COLOR_FONDO)
    button_frame.pack(fill=tk.X, pady=(10, 0))
    
    def confirmar():
        valores = {}
        for name, widget in entries.items():
            if isinstance(widget, tk.StringVar):
                valores[name] = widget.get()
            else:
                valores[name] = widget.get()
        callback_confirmar(valores, dialog)
    
    ttk.Button(button_frame, text="Aceptar", command=confirmar).pack(side=tk.RIGHT, padx=(5, 0))
    ttk.Button(button_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.RIGHT)
    
    # Calcular alto automáticamente
    alto = len(campos) * 60 + 100
    dialog.geometry(f"{ancho}x{alto}")
    centrar_ventana(dialog, ancho, alto)
    
    # Focus en el primer campo
    for entry in entries.values():
        if hasattr(entry, 'focus'):
            entry.focus()
            break
    
    return dialog

# Funciones para registrar elementos
def registrar_equipo():
    campos = [
        {'tipo': 'entry', 'name': 'nombre', 'text': 'Nombre del equipo:'},
        {'tipo': 'combobox', 'name': 'tipo', 'text': 'Tipo:', 'values': ['pc', 'laptop', 'celular', 'servidor', 'tablet']},
        {'tipo': 'entry', 'name': 'usuario', 'text': 'Usuario asignado:'},
        {'tipo': 'combobox', 'name': 'area', 'text': 'Área:', 'values': ['Administrativa', 'Contable', 'TI', 'Ventas', 'Soporte']},
    ]
    
    def confirmar(valores, dialog):
        try:
            equipo = sis.registrar_equipo(
                valores['nombre'],
                valores['tipo'],
                valores['usuario'],
                valores['area']
            )
            messagebox.showinfo("Éxito", f"Equipo {equipo.nombre} registrado\nID: {equipo.id_unico}\nUsername: {equipo.username}")
            listar_equipos()
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    crear_dialogo_simple("Registrar Equipo", campos, confirmar)

def registrar_nas():
    campos = [
        {'tipo': 'entry', 'name': 'direccion', 'text': 'Dirección IP:', 'default': '192.168.1.200'},
        {'tipo': 'entry', 'name': 'capacidad', 'text': 'Capacidad (GB):', 'default': '1000'},
        {'tipo': 'combobox', 'name': 'rol', 'text': 'Rol:', 'values': ['principal', 'secundario', 'respaldo']},
    ]
    
    def confirmar(valores, dialog):
        try:
            capacidad_bytes = int(valores['capacidad']) * 1024 * 1024 * 1024
            nas = sis.registrar_nas(valores['direccion'], capacidad_bytes, valores['rol'])
            messagebox.showinfo("Éxito", f"NAS registrado: {nas.direccion}")
            listar_nas()
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    crear_dialogo_simple("Registrar NAS", campos, confirmar)

def registrar_politica():
    nas_options = obtener_lista_nas()
    if not nas_options:
        messagebox.showwarning("Advertencia", "Primero registre un NAS")
        return
    
    campos = [
        {'tipo': 'combobox', 'name': 'frecuencia', 'text': 'Frecuencia:', 'values': ['diario', 'semanal', 'mensual']},
        {'tipo': 'entry', 'name': 'retencion', 'text': 'Días de retención:', 'default': '7'},
        {'tipo': 'combobox', 'name': 'nas_id', 'text': 'NAS destino:', 'values': [nas[1] for nas in nas_options]},
    ]
    
    def confirmar(valores, dialog):
        try:
            # Extraer ID del NAS de forma segura - CORREGIDO
            nas_seleccionado = valores['nas_id']
            
            # El formato es: "NAS 1 - 192.168.1.100 (principal)"
            match = re.search(r'NAS\s+(\d+)', nas_seleccionado)
            if match:
                nas_id = int(match.group(1))
            else:
                messagebox.showerror("Error", "Formato de NAS no válido")
                return
            
            retencion = int(valores['retencion'])
            politica = sis.registrar_politica(valores['frecuencia'], retencion, nas_id)
            messagebox.showinfo("Éxito", f"Política {politica.id} registrada")
            listar_politicas()
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    crear_dialogo_simple("Registrar Política", campos, confirmar)

def respaldar_equipo():
    equipos = obtener_lista_equipos()
    nas_list = obtener_lista_nas()
    
    if not equipos:
        messagebox.showwarning("Advertencia", "No hay equipos registrados")
        return
    if not nas_list:
        messagebox.showwarning("Advertencia", "No hay NAS registrados")
        return
    
    campos = [
        {'tipo': 'combobox', 'name': 'equipo', 'text': 'Equipo:', 'values': equipos},
        {'tipo': 'combobox', 'name': 'nas_id', 'text': 'NAS destino:', 'values': [nas[1] for nas in nas_list]},
    ]
    
    def confirmar(valores, dialog):
        try:
            # Verificar selecciones
            if not valores['equipo']:
                messagebox.showerror("Error", "Seleccione un equipo")
                return
                
            if not valores['nas_id']:
                messagebox.showerror("Error", "Seleccione un NAS")
                return
            
            # Extraer ID del NAS de forma segura - CORREGIDO
            nas_seleccionado = valores['nas_id']
            
            # El formato es: "NAS 1 - 192.168.1.100 (principal)"
            match = re.search(r'NAS\s+(\d+)', nas_seleccionado)
            if match:
                nas_id = int(match.group(1))
            else:
                messagebox.showerror("Error", "Formato de NAS no válido")
                return
            
            resultado = sis.respaldar_equipo(valores['equipo'], nas_id)
            messagebox.showinfo("Resultado", resultado)
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error al respaldar: {str(e)}")
    
    crear_dialogo_simple("Respaldar Equipo", campos, confirmar)

def restaurar_equipo():
    equipos = obtener_lista_equipos()
    if not equipos:
        messagebox.showwarning("Advertencia", "No hay equipos registrados")
        return
    
    campos = [
        {'tipo': 'combobox', 'name': 'equipo', 'text': 'Equipo a restaurar:', 'values': equipos},
    ]
    
    def confirmar(valores, dialog):
        try:
            if not valores['equipo']:
                messagebox.showerror("Error", "Seleccione un equipo")
                return
                
            resultado = sis.restaurar_equipo(valores['equipo'])
            messagebox.showinfo("Resultado", resultado)
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    crear_dialogo_simple("Restaurar Equipo", campos, confirmar)

def listar_respaldos_equipo():
    equipos = obtener_lista_equipos()
    if not equipos:
        messagebox.showwarning("Advertencia", "No hay equipos registrados")
        return
    
    campos = [
        {'tipo': 'combobox', 'name': 'equipo', 'text': 'Seleccionar equipo:', 'values': equipos},
    ]
    
    def mostrar(valores, dialog):
        try:
            if not valores['equipo']:
                messagebox.showerror("Error", "Seleccione un equipo")
                return
                
            limpiar_salida()
            resultado = sis.listar_respaldos_por_equipo(valores['equipo'])
            lineas = resultado.split('\n')
            for linea in lineas:
                lb_output.insert(tk.END, linea)
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    crear_dialogo_simple("Ver Respaldos", campos, mostrar)

def listar_equipos_nas():
    nas_list = obtener_lista_nas()
    if not nas_list:
        messagebox.showwarning("Advertencia", "No hay NAS registrados")
        return
    
    campos = [
        {'tipo': 'combobox', 'name': 'nas_id', 'text': 'Seleccionar NAS:', 'values': [nas[1] for nas in nas_list]},
    ]
    
    def mostrar(valores, dialog):
        try:
            if not valores['nas_id']:
                messagebox.showerror("Error", "Seleccione un NAS")
                return
                
            # Extraer ID del NAS de forma segura - CORREGIDO
            nas_seleccionado = valores['nas_id']
            
            match = re.search(r'NAS\s+(\d+)', nas_seleccionado)
            if match:
                nas_id = int(match.group(1))
            else:
                messagebox.showerror("Error", "Formato de NAS no válido")
                return
                
            limpiar_salida()
            from nas import NAS
            nas = NAS.buscar_por_id(nas_id)
            if nas:
                resultado = nas.obtener_info_equipos()
                lineas = resultado.split('\n')
                for linea in lineas:
                    lb_output.insert(tk.END, linea)
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    crear_dialogo_simple("Equipos en NAS", campos, mostrar)

# Funciones auxiliares
def obtener_lista_equipos():
    try:
        equipos = sis.listar_equipos()
        return [equipo.nombre for equipo in equipos] if equipos else []
    except Exception as e:
        print(f"Error al obtener equipos: {e}")
        return []

def obtener_lista_nas():
    try:
        nas_list = sis.listar_nas()
        if not nas_list:
            return []
        # Formato más claro: "NAS 1 - 192.168.1.100 (principal)"
        return [(nas.id, f"NAS {nas.id} - {nas.direccion} ({nas.rol})") for nas in nas_list]
    except Exception as e:
        print(f"Error al obtener NAS: {e}")
        return []

def obtener_lista_politicas():
    try:
        politicas = sis.listar_politicas()
        return [(p.id, f"Política {p.id} - {p.frecuencia}") for p in politicas] if politicas else []
    except Exception as e:
        print(f"Error al obtener políticas: {e}")
        return []

def limpiar_salida():
    lb_output.delete(0, tk.END)

def listar_usuarios():
    try:
        limpiar_salida()
        usuarios = sis.listar_usuarios()
        lb_output.insert(tk.END, "=== USUARIOS ===")
        lb_output.insert(tk.END, "")
        for u in usuarios:
            lb_output.insert(tk.END, f"• {u.nombre} ({u.role}) - {u.email}")
        if not usuarios:
            lb_output.insert(tk.END, "No hay usuarios registrados")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def listar_equipos():
    try:
        limpiar_salida()
        equipos = sis.listar_equipos()
        lb_output.insert(tk.END, "=== EQUIPOS ===")
        lb_output.insert(tk.END, "")
        for e in equipos:
            lb_output.insert(tk.END, f"• {e.nombre}")
            lb_output.insert(tk.END, f"  ID: {e.id_unico} | Tipo: {e.tipo}")
            lb_output.insert(tk.END, f"  Usuario: {e.usuario} | Área: {e.area}")
            lb_output.insert(tk.END, f"  Username: {e.username}")
            lb_output.insert(tk.END, "")
        if not equipos:
            lb_output.insert(tk.END, "No hay equipos registrados")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def listar_nas():
    try:
        limpiar_salida()
        nas_list = sis.listar_nas()
        lb_output.insert(tk.END, "=== NAS ===")
        lb_output.insert(tk.END, "")
        for n in nas_list:
            # Convertir bytes a GB para mejor legibilidad
            capacidad_total_gb = n.capacidad_total / (1024**3)
            capacidad_usada_gb = n.capacidad_usada / (1024**3)
            
            tipo = "PREDEFINIDO" if n.predefinido else "personalizado"
            
            lb_output.insert(tk.END, f"• {n.direccion} ({n.rol}) - {tipo}")
            lb_output.insert(tk.END, f"  Capacidad: {capacidad_usada_gb:.1f}/{capacidad_total_gb:.1f} GB")
            lb_output.insert(tk.END, f"  ID: {n.id}")
            lb_output.insert(tk.END, "")
        if not nas_list:
            lb_output.insert(tk.END, "No hay NAS registrados")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def listar_politicas():
    try:
        limpiar_salida()
        politicas = sis.listar_politicas()
        lb_output.insert(tk.END, "=== POLÍTICAS ===")
        lb_output.insert(tk.END, "")
        for p in politicas:
            lb_output.insert(tk.END, f"• {p.frecuencia} - Retención: {p.retencion} días")
            lb_output.insert(tk.END, f"  NAS destino: {p.destino_nas_id}")
            lb_output.insert(tk.END, "")
        if not politicas:
            lb_output.insert(tk.END, "No hay políticas registradas")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def generar_reporte():
    try:
        limpiar_salida()
        reporte = current_user.generarReporte()
        lb_output.insert(tk.END, "=== REPORTE ===")
        lb_output.insert(tk.END, "")
        lb_output.insert(tk.END, reporte)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def salir():
    if messagebox.askyesno("Salir", "¿Está seguro de salir?"):
        root.destroy()
        sys.exit(0)

def ajustar_menu_por_rol():
    if current_user is None:
        return
    
    # Deshabilitar todo primero
    for i in range(menu_acciones.index("end") + 1):
        try:
            menu_acciones.entryconfig(i, state="disabled")
        except:
            pass
    
    rol = current_user.role
    
    # Admin: acceso completo
    if rol == 'admin':
        for i in range(menu_acciones.index("end") + 1):
            try:
                menu_acciones.entryconfig(i, state="normal")
            except:
                pass
    
    # Analista: puede ver y restaurar, pero no registrar
    elif rol == 'analista':
        menu_acciones.entryconfig("Restaurar equipo", state="normal")
        menu_acciones.entryconfig("Ver usuarios", state="normal")
        menu_acciones.entryconfig("Ver equipos", state="normal")
        menu_acciones.entryconfig("Ver NAS", state="normal")
        menu_acciones.entryconfig("Ver políticas", state="normal")
        menu_acciones.entryconfig("Ver respaldos", state="normal")
        menu_acciones.entryconfig("Ver equipos en NAS", state="normal")
        menu_acciones.entryconfig("Generar reporte", state="normal")
    
    # Auxiliar: solo puede ver información básica
    elif rol == 'auxiliar':
        menu_acciones.entryconfig("Ver equipos", state="normal")
        menu_acciones.entryconfig("Ver NAS", state="normal")
        menu_acciones.entryconfig("Ver políticas", state="normal")
        menu_acciones.entryconfig("Ver respaldos", state="normal")
        menu_acciones.entryconfig("Ver equipos en NAS", state="normal")

def actualizar_info_usuario():
    if current_user:
        lbl_usuario.config(text=f"Usuario: {current_user.nombre} ({current_user.role})")
    else:
        lbl_usuario.config(text="No autenticado")

def login_inicial():
    crear_ventana_login()

# Interfaz principal simple
root = tk.Tk()
root.title("Sistema de Respaldos")
root.geometry("900x600")
root.configure(bg=COLOR_FONDO)

# Header simple
header_frame = tk.Frame(root, bg=COLOR_PRIMARIO, height=50)
header_frame.pack(fill=tk.X)
header_frame.pack_propagate(False)

tk.Label(header_frame, text="Sistema de Gestión de Respaldos", 
         font=('Arial', 14, 'bold'), bg=COLOR_PRIMARIO, fg='white'
         ).pack(side=tk.LEFT, padx=10, pady=10)

lbl_usuario = tk.Label(header_frame, text="No autenticado", 
                      font=('Arial', 10), bg=COLOR_PRIMARIO, fg='white')
lbl_usuario.pack(side=tk.RIGHT, padx=10, pady=10)

# Menú principal
menubar = tk.Menu(root, font=('Arial', 10))

# Menú de Archivo
menu_archivo = tk.Menu(menubar, tearoff=0)
menu_archivo.add_command(label="Salir", command=salir)
menubar.add_cascade(label="Archivo", menu=menu_archivo)

# Menú de Acciones (se ajusta por rol)
menu_acciones = tk.Menu(menubar, tearoff=0)
menu_acciones.add_command(label="Registrar usuario", command=crear_ventana_registro)
menu_acciones.add_command(label="Registrar equipo", command=registrar_equipo)
menu_acciones.add_command(label="Registrar NAS", command=registrar_nas)
menu_acciones.add_command(label="Registrar política", command=registrar_politica)
menu_acciones.add_separator()
menu_acciones.add_command(label="Respaldar equipo", command=respaldar_equipo)
menu_acciones.add_command(label="Restaurar equipo", command=restaurar_equipo)
menu_acciones.add_separator()
menu_acciones.add_command(label="Ver usuarios", command=listar_usuarios)
menu_acciones.add_command(label="Ver equipos", command=listar_equipos)
menu_acciones.add_command(label="Ver NAS", command=listar_nas)
menu_acciones.add_command(label="Ver políticas", command=listar_politicas)
menu_acciones.add_command(label="Ver respaldos", command=listar_respaldos_equipo)
menu_acciones.add_command(label="Ver equipos en NAS", command=listar_equipos_nas)
menu_acciones.add_separator()
menu_acciones.add_command(label="Generar reporte", command=generar_reporte)

menubar.add_cascade(label="Acciones", menu=menu_acciones)
root.config(menu=menubar)

# Área de salida
output_frame = tk.Frame(root, bg=COLOR_FONDO)
output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Scrollbar y Listbox
scrollbar = tk.Scrollbar(output_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

lb_output = tk.Listbox(output_frame, yscrollcommand=scrollbar.set,
                      font=('Consolas', 10), bg='white')
lb_output.pack(fill=tk.BOTH, expand=True)

scrollbar.config(command=lb_output.yview)

# Mensaje inicial
lb_output.insert(tk.END, "Bienvenido al Sistema de Gestión de Respaldos")
lb_output.insert(tk.END, "Por favor inicie sesión para continuar...")
lb_output.insert(tk.END, "")

# Centrar y iniciar
centrar_ventana(root, 900, 600)
root.after(100, login_inicial)

root.mainloop()