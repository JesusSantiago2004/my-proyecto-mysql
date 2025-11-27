import sys
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from sistema_respaldo import SistemaRespaldo
from usuario_ti import UsuarioTI

sis = SistemaRespaldo()
current_user = None  # UsuarioTI autenticado

ADMIN_SECRET_CODE = "ADMIN2024"

def login_inicial():
    global current_user
    tiene = messagebox.askyesno("Bienvenido", "¿Tienes una cuenta?")
    if not tiene:
        u = registrar_usuario_publico()
        if u:
            current_user = u
            lbl_help.config(text=f"Usuario: {current_user.nombre} ({current_user.role})")
            ajustar_menu_por_rol()
            listar_equipos()
            return
    for _ in range(3):
        login = simpledialog.askstring("Inicio", "Nombre de usuario:")
        if login is None: salir()
        pwd = simpledialog.askstring("Inicio", "Contraseña:", show='*')
        if pwd is None: salir()
        usuario = UsuarioTI.autenticar(login.strip(), pwd)
        if usuario:
            current_user = usuario
            lbl_help.config(text=f"Usuario: {current_user.nombre} ({current_user.role})")
            ajustar_menu_por_rol()
            listar_equipos()
            return
        else:
            retry = messagebox.askretrycancel("Error", "Credenciales incorrectas. ¿Reintentar?")
            if not retry: salir()
    messagebox.showerror("Error", "Demasiados intentos. Saliendo.")
    salir()

def requiere_admin(func):
    def wrapper(*args, **kwargs):
        if current_user is None or current_user.role != 'admin':
            messagebox.showerror("Permisos", "Requiere admin.")
            return
        return func(*args, **kwargs)
    return wrapper

def registrar_usuario_publico():
    nombre = simpledialog.askstring("Registrar", "Nombre:")
    if not nombre: return None
    email = simpledialog.askstring("Registrar", "Email:")
    if not email: return None
    role = simpledialog.askstring("Registrar", "Rol (coordinador/admin):", initialvalue="coordinador")
    role = role.strip().lower()
    if role == 'admin':
        codigo = simpledialog.askstring("Código", "Código secreto para admin:", show='*')
        if codigo != ADMIN_SECRET_CODE:
            messagebox.showerror("Error", "Código incorrecto.")
            return None
    if role not in ('coordinador', 'admin'):
        role = 'coordinador'
    pwd = simpledialog.askstring("Registrar", "Contraseña:", show='*')
    u = sis.registrar_usuario(nombre, email, role, pwd)
    messagebox.showinfo("OK", f"Registrado: {u.nombre}")
    return u

@requiere_admin
def registrar_usuario():
    nombre = simpledialog.askstring("Registrar usuario", "Nombre:")
    if not nombre: return
    email = simpledialog.askstring("Registrar usuario", "Email:")
    if not email: return
    role = simpledialog.askstring("Registrar usuario", "Rol (admin/coordinador):", initialvalue="coordinador")
    if role == 'admin':
        codigo = simpledialog.askstring("Código", "Código secreto:", show='*')
        if codigo != ADMIN_SECRET_CODE:
            messagebox.showerror("Error", "Código incorrecto.")
            return
    pwd = simpledialog.askstring("Registrar usuario", "Contraseña:", show='*')
    try:
        u = sis.registrar_usuario(nombre, email, role, pwd)
        messagebox.showinfo("OK", f"Registrado: {u}")
        listar_usuarios()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def registrar_equipo():
    nombre = simpledialog.askstring("Registrar equipo", "Nombre:")
    if not nombre: return
    area = simpledialog.askstring("Registrar equipo", "Área (administrativa/contable/operativa):")
    if not area: return
    try:
        e = sis.registrar_equipo(nombre, area)
        messagebox.showinfo("OK", f"Equipo registrado: {e}")
        listar_equipos()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def registrar_nas():
    direccion = simpledialog.askstring("Registrar NAS", "Dirección:")
    if not direccion: return
    capacidad = simpledialog.askinteger("Registrar NAS", "Capacidad total (bytes):")
    if not capacidad: return
    rol = simpledialog.askstring("Registrar NAS", "Rol (principal/secundario):", initialvalue="principal")
    try:
        n = sis.registrar_nas(direccion, capacidad, rol)
        messagebox.showinfo("OK", f"NAS registrado: {n}")
        listar_nas()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def registrar_politica():
    frecuencia = simpledialog.askstring("Registrar política", "Frecuencia (diario/semanal/mensual):")
    if not frecuencia: return
    retencion = simpledialog.askinteger("Registrar política", "Retención (días):")
    if not retencion: return
    destino_nas = simpledialog.askinteger("Registrar política", "ID de NAS destino:")
    if not destino_nas: return
    try:
        p = sis.registrar_politica(frecuencia, retencion, destino_nas)
        messagebox.showinfo("OK", f"Política registrada: {p}")
        listar_politicas()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def respaldar_equipo():
    nombre = simpledialog.askstring("Respaldar", "Nombre del equipo:")
    if not nombre: return
    nas_id = simpledialog.askinteger("Respaldar", "ID de NAS:")
    if not nas_id: return
    msg = sis.respaldar_equipo(nombre, nas_id)
    messagebox.showinfo("Resultado", msg)

def restaurar_equipo():
    nombre = simpledialog.askstring("Restaurar", "Nombre del equipo:")
    if not nombre: return
    msg = sis.restaurar_equipo(nombre)
    messagebox.showinfo("Resultado", msg)

@requiere_admin
def asignar_politica():
    nombre = simpledialog.askstring("Asignar política", "Nombre del equipo:")
    if not nombre: return
    politica_id = simpledialog.askinteger("Asignar política", "ID de política:")
    if not politica_id: return
    msg = sis.asignar_politica(nombre, politica_id, current_user)
    messagebox.showinfo("Resultado", msg)

def listar_usuarios():
    lb_output.delete(0, tk.END)
    usuarios = sis.listar_usuarios()
    lb_output.insert(tk.END, "Usuarios:")
    for u in usuarios:
        lb_output.insert(tk.END, str(u))

def listar_equipos():
    lb_output.delete(0, tk.END)
    equipos = sis.listar_equipos()
    lb_output.insert(tk.END, "Equipos:")
    for e in equipos:
        lb_output.insert(tk.END, str(e))

def listar_nas():
    lb_output.delete(0, tk.END)
    nas_list = sis.listar_nas()
    lb_output.insert(tk.END, "NAS:")
    for n in nas_list:
        lb_output.insert(tk.END, str(n))

def listar_politicas():
    lb_output.delete(0, tk.END)
    politicas = sis.listar_politicas()
    lb_output.insert(tk.END, "Políticas:")
    for p in politicas:
        lb_output.insert(tk.END, str(p))

def generar_reporte():
    lb_output.delete(0, tk.END)
    reporte = current_user.generarReporte()
    lb_output.insert(tk.END, reporte)

def salir():
    root.destroy()
    sys.exit(0)

def ajustar_menu_por_rol():
    if current_user is None:
        return
    if current_user.role == 'admin':
        acciones_menu.entryconfig("Registrar usuario", state="normal")
        acciones_menu.entryconfig("Registrar equipo", state="normal")
        acciones_menu.entryconfig("Registrar NAS", state="normal")
        acciones_menu.entryconfig("Registrar política", state="normal")
        acciones_menu.entryconfig("Asignar política", state="normal")
        acciones_menu.entryconfig("Respaldar equipo", state="normal")
        acciones_menu.entryconfig("Restaurar equipo", state="normal")
        acciones_menu.entryconfig("Listar usuarios", state="normal")
        acciones_menu.entryconfig("Listar equipos", state="normal")
        acciones_menu.entryconfig("Listar NAS", state="normal")
        acciones_menu.entryconfig("Listar políticas", state="normal")
        acciones_menu.entryconfig("Generar reporte", state="normal")
    elif current_user.role == 'coordinador':
        acciones_menu.entryconfig("Registrar usuario", state="disabled")
        acciones_menu.entryconfig("Registrar equipo", state="disabled")
        acciones_menu.entryconfig("Registrar NAS", state="disabled")
        acciones_menu.entryconfig("Registrar política", state="disabled")
        acciones_menu.entryconfig("Asignar política", state="disabled")
        acciones_menu.entryconfig("Respaldar equipo", state="disabled")
        acciones_menu.entryconfig("Restaurar equipo", state="normal")
        acciones_menu.entryconfig("Listar usuarios", state="normal")
        acciones_menu.entryconfig("Listar equipos", state="normal")
        acciones_menu.entryconfig("Listar NAS", state="normal")
        acciones_menu.entryconfig("Listar políticas", state="normal")
        acciones_menu.entryconfig("Generar reporte", state="normal")
    else:
        acciones_menu.entryconfig("Registrar usuario", state="disabled")
        acciones_menu.entryconfig("Registrar equipo", state="disabled")
        acciones_menu.entryconfig("Registrar NAS", state="disabled")
        acciones_menu.entryconfig("Registrar política", state="disabled")
        acciones_menu.entryconfig("Asignar política", state="disabled")
        acciones_menu.entryconfig("Respaldar equipo", state="disabled")
        acciones_menu.entryconfig("Restaurar equipo", state="disabled")
        acciones_menu.entryconfig("Listar usuarios", state="disabled")
        acciones_menu.entryconfig("Listar equipos", state="normal")
        acciones_menu.entryconfig("Listar NAS", state="normal")
        acciones_menu.entryconfig("Listar políticas", state="normal")
        acciones_menu.entryconfig("Generar reporte", state="disabled")

# Interfaz gráfica
root = tk.Tk()
root.title("Sistema de Gestión de Respaldos")
root.geometry("800x480")
root.minsize(700, 420)

menubar = tk.Menu(root)
acciones_menu = tk.Menu(menubar, tearoff=0)
acciones_menu.add_command(label="Registrar usuario", command=registrar_usuario)
acciones_menu.add_command(label="Registrar equipo", command=registrar_equipo)
acciones_menu.add_command(label="Registrar NAS", command=registrar_nas)
acciones_menu.add_command(label="Registrar política", command=registrar_politica)
acciones_menu.add_separator()
acciones_menu.add_command(label="Asignar política", command=asignar_politica)
acciones_menu.add_command(label="Respaldar equipo", command=respaldar_equipo)
acciones_menu.add_command(label="Restaurar equipo", command=restaurar_equipo)
acciones_menu.add_separator()
acciones_menu.add_command(label="Listar usuarios", command=listar_usuarios)
acciones_menu.add_command(label="Listar equipos", command=listar_equipos)
acciones_menu.add_command(label="Listar NAS", command=listar_nas)
acciones_menu.add_command(label="Listar políticas", command=listar_politicas)
acciones_menu.add_separator()
acciones_menu.add_command(label="Generar reporte", command=generar_reporte)
menubar.add_cascade(label="Acciones", menu=acciones_menu)

archivo_menu = tk.Menu(menubar, tearoff=0)
archivo_menu.add_command(label="Salir", command=salir)
menubar.add_cascade(label="Archivo", menu=archivo_menu)

root.config(menu=menubar)

frame_output = ttk.Frame(root, padding=(12, 12))
frame_output.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

lbl_output = ttk.Label(frame_output, text="Salida", font=("Segoe UI", 12, "bold"))
lbl_output.pack(anchor="w")

frame_list = ttk.Frame(frame_output)
frame_list.pack(fill=tk.BOTH, expand=True, pady=(6, 0))

sb = ttk.Scrollbar(frame_list, orient=tk.VERTICAL)
lb_output = tk.Listbox(frame_list, yscrollcommand=sb.set, font=("Consolas", 10))
sb.config(command=lb_output.yview)
sb.pack(side=tk.RIGHT, fill=tk.Y)
lb_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

lbl_help = ttk.Label(frame_output, text="Iniciando...", font=("Segoe UI", 9))
lbl_help.pack(anchor="w", pady=(8, 0))

root.after(100, login_inicial)
root.mainloop()