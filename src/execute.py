import sys
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from sistema_respaldo import SistemaRespaldo
from usuario_ti import UsuarioTI

sis = SistemaRespaldo()
current_user = None  # UsuarioTI autenticado

ADMIN_SECRET_CODE = "ADMIN2024"

def centrar_ventana(ventana, ancho=900, alto=600):
    """Centra la ventana en la pantalla"""
    pantalla_ancho = ventana.winfo_screenwidth()
    pantalla_alto = ventana.winfo_screenheight()
    x = (pantalla_ancho // 2) - (ancho // 2)
    y = (pantalla_alto // 2) - (alto // 2)
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

def obtener_lista_equipos():
    """Obtiene lista de equipos para combobox"""
    try:
        equipos = sis.listar_equipos()
        return [equipo.nombre for equipo in equipos]
    except Exception as e:
        print(f"Error al obtener equipos: {e}")
        return []

def obtener_lista_nas():
    """Obtiene lista de NAS para combobox"""
    try:
        nas_list = sis.listar_nas()
        return [(nas.id, f"NAS {nas.id} - {nas.direccion}") for nas in nas_list]
    except Exception as e:
        print(f"Error al obtener NAS: {e}")
        return []

def obtener_lista_politicas():
    """Obtiene lista de políticas para combobox"""
    try:
        politicas = sis.listar_politicas()
        return [(p.id, f"Política {p.id} - {p.frecuencia}") for p in politicas]
    except Exception as e:
        print(f"Error al obtener políticas: {e}")
        return []

def login_inicial():
    global current_user
    try:
        tiene = messagebox.askyesno("Bienvenido", "¿Tienes una cuenta?")
        if not tiene:
            u = registrar_usuario_publico()
            if u:
                current_user = u
                actualizar_info_usuario()
                ajustar_menu_por_rol()
                listar_equipos()
                return
        
        for _ in range(3):
            login = simpledialog.askstring("Inicio", "Nombre de usuario:")
            if login is None: 
                salir()
                return
            pwd = simpledialog.askstring("Inicio", "Contraseña:", show='*')
            if pwd is None: 
                salir()
                return
            
            usuario = UsuarioTI.autenticar(login.strip(), pwd)
            if usuario:
                current_user = usuario
                actualizar_info_usuario()
                ajustar_menu_por_rol()
                listar_equipos()
                return
            else:
                retry = messagebox.askretrycancel("Error", "Credenciales incorrectas. ¿Reintentar?")
                if not retry: 
                    salir()
                    return
        
        messagebox.showerror("Error", "Demasiados intentos. Saliendo.")
        salir()
    except Exception as e:
        messagebox.showerror("Error", f"Error en login: {str(e)}")
        salir()

def requiere_admin(func):
    def wrapper(*args, **kwargs):
        if current_user is None or current_user.role != 'admin':
            messagebox.showerror("Permisos", "Se requiere rol de administrador para esta acción.")
            return
        return func(*args, **kwargs)
    return wrapper

def registrar_usuario_publico():
    try:
        nombre = simpledialog.askstring("Registrar", "Nombre:")
        if not nombre: 
            return None
        email = simpledialog.askstring("Registrar", "Email:")
        if not email: 
            return None
        
        role = simpledialog.askstring("Registrar", "Rol (coordinador/admin):", initialvalue="coordinador")
        if role:
            role = role.strip().lower()
        else:
            role = "coordinador"
            
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
    except Exception as e:
        messagebox.showerror("Error", f"Error al registrar usuario: {str(e)}")
        return None

@requiere_admin
def registrar_usuario():
    try:
        # Diálogo personalizado para registrar usuario
        dialog = tk.Toplevel(root)
        dialog.title("Registrar Usuario")
        dialog.geometry("400x250")
        dialog.transient(root)
        dialog.grab_set()
        centrar_ventana(dialog, 400, 250)
        
        ttk.Label(dialog, text="Nombre:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        nombre_entry = ttk.Entry(dialog, width=30)
        nombre_entry.grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Email:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        email_entry = ttk.Entry(dialog, width=30)
        email_entry.grid(row=1, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Rol:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        rol_var = tk.StringVar(value="coordinador")
        rol_combo = ttk.Combobox(dialog, textvariable=rol_var, values=["coordinador", "admin"], state="readonly", width=27)
        rol_combo.grid(row=2, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Contraseña:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        pwd_entry = ttk.Entry(dialog, show='*', width=30)
        pwd_entry.grid(row=3, column=1, padx=10, pady=10)
        
        def confirmar():
            try:
                nombre = nombre_entry.get().strip()
                email = email_entry.get().strip()
                role = rol_var.get()
                pwd = pwd_entry.get()
                
                if not nombre or not email:
                    messagebox.showerror("Error", "Nombre y email son obligatorios.")
                    return
                
                if role == 'admin':
                    codigo = simpledialog.askstring("Código", "Código secreto para admin:", show='*', parent=dialog)
                    if codigo != ADMIN_SECRET_CODE:
                        messagebox.showerror("Error", "Código incorrecto.")
                        return
                
                u = sis.registrar_usuario(nombre, email, role, pwd)
                messagebox.showinfo("OK", f"Usuario registrado: {u}")
                listar_usuarios()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Error al registrar: {str(e)}")
        
        def cancelar():
            dialog.destroy()
        
        ttk.Button(dialog, text="Registrar", command=confirmar).grid(row=4, column=0, padx=10, pady=20)
        ttk.Button(dialog, text="Cancelar", command=cancelar).grid(row=4, column=1, padx=10, pady=20)
        
        nombre_entry.focus()
    except Exception as e:
        messagebox.showerror("Error", f"Error al abrir diálogo: {str(e)}")

def registrar_equipo():
    try:
        # Diálogo personalizado para registrar equipo
        dialog = tk.Toplevel(root)
        dialog.title("Registrar Equipo")
        dialog.geometry("400x200")
        dialog.transient(root)
        dialog.grab_set()
        centrar_ventana(dialog, 400, 200)
        
        ttk.Label(dialog, text="Nombre del equipo:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        nombre_entry = ttk.Entry(dialog, width=30)
        nombre_entry.grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Área:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        area_var = tk.StringVar(value="administrativa")
        area_combo = ttk.Combobox(dialog, textvariable=area_var, 
                                 values=["administrativa", "contable", "operativa"], 
                                 state="readonly", width=27)
        area_combo.grid(row=1, column=1, padx=10, pady=10)
        
        def confirmar():
            try:
                nombre = nombre_entry.get().strip()
                area = area_var.get()
                
                if not nombre:
                    messagebox.showerror("Error", "El nombre del equipo es obligatorio.")
                    return
                
                e = sis.registrar_equipo(nombre, area)
                messagebox.showinfo("OK", f"Equipo registrado: {e}")
                listar_equipos()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Error al registrar equipo: {str(e)}")
        
        def cancelar():
            dialog.destroy()
        
        ttk.Button(dialog, text="Registrar", command=confirmar).grid(row=2, column=0, padx=10, pady=20)
        ttk.Button(dialog, text="Cancelar", command=cancelar).grid(row=2, column=1, padx=10, pady=20)
        
        nombre_entry.focus()
    except Exception as e:
        messagebox.showerror("Error", f"Error al abrir diálogo: {str(e)}")

def registrar_nas():
    try:
        # Diálogo personalizado para registrar NAS
        dialog = tk.Toplevel(root)
        dialog.title("Registrar NAS")
        dialog.geometry("400x250")
        dialog.transient(root)
        dialog.grab_set()
        centrar_ventana(dialog, 400, 250)
        
        ttk.Label(dialog, text="Dirección IP:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        direccion_entry = ttk.Entry(dialog, width=30)
        direccion_entry.grid(row=0, column=1, padx=10, pady=10)
        direccion_entry.insert(0, "192.168.1.")
        
        ttk.Label(dialog, text="Capacidad (GB):").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        capacidad_entry = ttk.Entry(dialog, width=30)
        capacidad_entry.grid(row=1, column=1, padx=10, pady=10)
        capacidad_entry.insert(0, "1000")
        
        ttk.Label(dialog, text="Rol:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        rol_var = tk.StringVar(value="principal")
        rol_combo = ttk.Combobox(dialog, textvariable=rol_var, 
                                values=["principal", "secundario"], 
                                state="readonly", width=27)
        rol_combo.grid(row=2, column=1, padx=10, pady=10)
        
        def confirmar():
            try:
                direccion = direccion_entry.get().strip()
                capacidad = capacidad_entry.get().strip()
                rol = rol_var.get()
                
                if not direccion or not capacidad:
                    messagebox.showerror("Error", "Dirección y capacidad son obligatorios.")
                    return
                
                # Convertir GB a bytes
                capacidad_bytes = int(capacidad) * 1024 * 1024 * 1024
                n = sis.registrar_nas(direccion, capacidad_bytes, rol)
                messagebox.showinfo("OK", f"NAS registrado: {n}")
                listar_nas()
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "La capacidad debe ser un número válido.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al registrar NAS: {str(e)}")
        
        def cancelar():
            dialog.destroy()
        
        ttk.Button(dialog, text="Registrar", command=confirmar).grid(row=3, column=0, padx=10, pady=20)
        ttk.Button(dialog, text="Cancelar", command=cancelar).grid(row=3, column=1, padx=10, pady=20)
        
        direccion_entry.focus()
    except Exception as e:
        messagebox.showerror("Error", f"Error al abrir diálogo: {str(e)}")

def registrar_politica():
    try:
        # Diálogo personalizado para registrar política
        dialog = tk.Toplevel(root)
        dialog.title("Registrar Política de Respaldo")
        dialog.geometry("400x300")
        dialog.transient(root)
        dialog.grab_set()
        centrar_ventana(dialog, 400, 300)
        
        ttk.Label(dialog, text="Frecuencia:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        frecuencia_var = tk.StringVar(value="diario")
        frecuencia_combo = ttk.Combobox(dialog, textvariable=frecuencia_var, 
                                       values=["diario", "semanal", "mensual"], 
                                       state="readonly", width=27)
        frecuencia_combo.grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Retención (días):").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        retencion_entry = ttk.Entry(dialog, width=30)
        retencion_entry.grid(row=1, column=1, padx=10, pady=10)
        retencion_entry.insert(0, "7")
        
        ttk.Label(dialog, text="NAS destino:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        nas_options = obtener_lista_nas()
        nas_var = tk.StringVar()
        nas_combo = ttk.Combobox(dialog, textvariable=nas_var, 
                                values=[f"{nas[1]} (ID: {nas[0]})" for nas in nas_options],
                                state="readonly", width=27)
        nas_combo.grid(row=2, column=1, padx=10, pady=10)
        
        if nas_options:
            nas_combo.set(nas_options[0][1])
        else:
            messagebox.showwarning("Advertencia", "No hay NAS registrados. Debe registrar un NAS primero.")
            dialog.destroy()
            return
        
        def confirmar():
            try:
                frecuencia = frecuencia_var.get()
                retencion = retencion_entry.get().strip()
                
                if not frecuencia or not retencion or not nas_var.get():
                    messagebox.showerror("Error", "Todos los campos son obligatorios.")
                    return
                
                # Extraer ID del NAS seleccionado
                nas_seleccionado = nas_var.get()
                nas_id = int(nas_seleccionado.split("(ID: ")[1].replace(")", ""))
                
                retencion_int = int(retencion)
                p = sis.registrar_politica(frecuencia, retencion_int, nas_id)
                messagebox.showinfo("OK", f"Política registrada: {p}")
                listar_politicas()
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "La retención debe ser un número válido.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al registrar política: {str(e)}")
        
        def cancelar():
            dialog.destroy()
        
        ttk.Button(dialog, text="Registrar", command=confirmar).grid(row=3, column=0, padx=10, pady=20)
        ttk.Button(dialog, text="Cancelar", command=cancelar).grid(row=3, column=1, padx=10, pady=20)
    except Exception as e:
        messagebox.showerror("Error", f"Error al abrir diálogo: {str(e)}")

def respaldar_equipo():
    try:
        # Diálogo personalizado para respaldar equipo
        dialog = tk.Toplevel(root)
        dialog.title("Respaldar Equipo")
        dialog.geometry("400x200")
        dialog.transient(root)
        dialog.grab_set()
        centrar_ventana(dialog, 400, 200)
        
        ttk.Label(dialog, text="Equipo:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        equipo_options = obtener_lista_equipos()
        equipo_var = tk.StringVar()
        equipo_combo = ttk.Combobox(dialog, textvariable=equipo_var, 
                                   values=equipo_options, state="readonly", width=27)
        equipo_combo.grid(row=0, column=1, padx=10, pady=10)
        
        if equipo_options:
            equipo_combo.set(equipo_options[0])
        else:
            messagebox.showwarning("Advertencia", "No hay equipos registrados.")
            dialog.destroy()
            return
        
        ttk.Label(dialog, text="NAS destino:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        nas_options = obtener_lista_nas()
        nas_var = tk.StringVar()
        nas_combo = ttk.Combobox(dialog, textvariable=nas_var, 
                                values=[f"{nas[1]} (ID: {nas[0]})" for nas in nas_options],
                                state="readonly", width=27)
        nas_combo.grid(row=1, column=1, padx=10, pady=10)
        
        if nas_options:
            nas_combo.set(nas_options[0][1])
        
        def confirmar():
            try:
                equipo_nombre = equipo_var.get()
                nas_seleccionado = nas_var.get()
                
                if not equipo_nombre or not nas_seleccionado:
                    messagebox.showerror("Error", "Seleccione equipo y NAS.")
                    return
                
                # Extraer ID del NAS seleccionado
                nas_id = int(nas_seleccionado.split("(ID: ")[1].replace(")", ""))
                
                # Usar el sistema para respaldar (maneja mejor los errores)
                msg = sis.respaldar_equipo(equipo_nombre, nas_id)
                messagebox.showinfo("Resultado", msg)
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al respaldar: {str(e)}")
        
        def cancelar():
            dialog.destroy()
        
        ttk.Button(dialog, text="Iniciar Respaldo", command=confirmar).grid(row=2, column=0, padx=10, pady=20)
        ttk.Button(dialog, text="Cancelar", command=cancelar).grid(row=2, column=1, padx=10, pady=20)
    except Exception as e:
        messagebox.showerror("Error", f"Error al abrir diálogo: {str(e)}")

def restaurar_equipo():
    try:
        # Diálogo personalizado para restaurar equipo
        dialog = tk.Toplevel(root)
        dialog.title("Restaurar Equipo")
        dialog.geometry("400x150")
        dialog.transient(root)
        dialog.grab_set()
        centrar_ventana(dialog, 400, 150)
        
        ttk.Label(dialog, text="Equipo a restaurar:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        equipo_options = obtener_lista_equipos()
        equipo_var = tk.StringVar()
        equipo_combo = ttk.Combobox(dialog, textvariable=equipo_var, 
                                   values=equipo_options, state="readonly", width=27)
        equipo_combo.grid(row=0, column=1, padx=10, pady=10)
        
        if equipo_options:
            equipo_combo.set(equipo_options[0])
        else:
            messagebox.showwarning("Advertencia", "No hay equipos registrados.")
            dialog.destroy()
            return
        
        def confirmar():
            try:
                equipo_nombre = equipo_var.get()
                
                if not equipo_nombre:
                    messagebox.showerror("Error", "Seleccione un equipo.")
                    return
                
                msg = sis.restaurar_equipo(equipo_nombre)
                messagebox.showinfo("Resultado", msg)
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Error al restaurar: {str(e)}")
        
        def cancelar():
            dialog.destroy()
        
        ttk.Button(dialog, text="Iniciar Restauración", command=confirmar).grid(row=1, column=0, padx=10, pady=20)
        ttk.Button(dialog, text="Cancelar", command=cancelar).grid(row=1, column=1, padx=10, pady=20)
    except Exception as e:
        messagebox.showerror("Error", f"Error al abrir diálogo: {str(e)}")

@requiere_admin
def asignar_politica():
    try:
        # Diálogo personalizado para asignar política
        dialog = tk.Toplevel(root)
        dialog.title("Asignar Política a Equipo")
        dialog.geometry("400x200")
        dialog.transient(root)
        dialog.grab_set()
        centrar_ventana(dialog, 400, 200)
        
        ttk.Label(dialog, text="Equipo:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        equipo_options = obtener_lista_equipos()
        equipo_var = tk.StringVar()
        equipo_combo = ttk.Combobox(dialog, textvariable=equipo_var, 
                                   values=equipo_options, state="readonly", width=27)
        equipo_combo.grid(row=0, column=1, padx=10, pady=10)
        
        if equipo_options:
            equipo_combo.set(equipo_options[0])
        else:
            messagebox.showwarning("Advertencia", "No hay equipos registrados.")
            dialog.destroy()
            return
        
        ttk.Label(dialog, text="Política:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        politica_options = obtener_lista_politicas()
        politica_var = tk.StringVar()
        politica_combo = ttk.Combobox(dialog, textvariable=politica_var, 
                                     values=[f"{p[1]} (ID: {p[0]})" for p in politica_options],
                                     state="readonly", width=27)
        politica_combo.grid(row=1, column=1, padx=10, pady=10)
        
        if politica_options:
            politica_combo.set(politica_options[0][1])
        else:
            messagebox.showwarning("Advertencia", "No hay políticas registradas.")
            dialog.destroy()
            return
        
        def confirmar():
            try:
                equipo_nombre = equipo_var.get()
                politica_seleccionada = politica_var.get()
                
                if not equipo_nombre or not politica_seleccionada:
                    messagebox.showerror("Error", "Seleccione equipo y política.")
                    return
                
                # Extraer ID de la política seleccionada
                politica_id = int(politica_seleccionada.split("(ID: ")[1].replace(")", ""))
                
                # Actualizar la política del equipo directamente en la base de datos
                from db_connection import get_conn
                conn = get_conn()
                cur = conn.cursor()
                
                # Obtener ID del equipo
                cur.execute("SELECT id FROM equipos WHERE nombre = %s", (equipo_nombre,))
                resultado = cur.fetchone()
                if not resultado:
                    messagebox.showerror("Error", "Equipo no encontrado.")
                    return
                
                equipo_id = resultado[0]
                cur.execute("UPDATE equipos SET politica_id = %s WHERE id = %s", (politica_id, equipo_id))
                conn.commit()
                cur.close()
                conn.close()
                
                messagebox.showinfo("Éxito", f"Política {politica_id} asignada al equipo {equipo_nombre}")
                listar_equipos()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Error al asignar política: {str(e)}")
        
        def cancelar():
            dialog.destroy()
        
        ttk.Button(dialog, text="Asignar Política", command=confirmar).grid(row=2, column=0, padx=10, pady=20)
        ttk.Button(dialog, text="Cancelar", command=cancelar).grid(row=2, column=1, padx=10, pady=20)
    except Exception as e:
        messagebox.showerror("Error", f"Error al abrir diálogo: {str(e)}")

def listar_respaldos_equipo():
    try:
        # Diálogo para seleccionar equipo
        dialog = tk.Toplevel(root)
        dialog.title("Listar Respaldos por Equipo")
        dialog.geometry("400x150")
        dialog.transient(root)
        dialog.grab_set()
        centrar_ventana(dialog, 400, 150)
        
        ttk.Label(dialog, text="Equipo:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        equipo_options = obtener_lista_equipos()
        equipo_var = tk.StringVar()
        equipo_combo = ttk.Combobox(dialog, textvariable=equipo_var, 
                                   values=equipo_options, state="readonly", width=27)
        equipo_combo.grid(row=0, column=1, padx=10, pady=10)
        
        if equipo_options:
            equipo_combo.set(equipo_options[0])
        else:
            messagebox.showwarning("Advertencia", "No hay equipos registrados.")
            dialog.destroy()
            return
        
        def confirmar():
            try:
                equipo_nombre = equipo_var.get()
                
                if not equipo_nombre:
                    messagebox.showerror("Error", "Seleccione un equipo.")
                    return
                
                limpiar_salida()
                resultado = sis.listar_respaldos_por_equipo(equipo_nombre)
                
                # Mostrar el resultado en el Listbox
                lineas = resultado.split('\n')
                for linea in lineas:
                    lb_output.insert(tk.END, linea)
                
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Error al listar respaldos: {str(e)}")
        
        def cancelar():
            dialog.destroy()
        
        ttk.Button(dialog, text="Listar Respaldos", command=confirmar).grid(row=1, column=0, padx=10, pady=20)
        ttk.Button(dialog, text="Cancelar", command=cancelar).grid(row=1, column=1, padx=10, pady=20)
    except Exception as e:
        messagebox.showerror("Error", f"Error al abrir diálogo: {str(e)}")

def limpiar_salida():
    """Limpia completamente el área de salida"""
    lb_output.delete(0, tk.END)

def listar_usuarios():
    try:
        limpiar_salida()
        usuarios = sis.listar_usuarios()
        lb_output.insert(tk.END, "=== USUARIOS REGISTRADOS ===")
        lb_output.insert(tk.END, "")  # Línea en blanco
        for u in usuarios:
            lb_output.insert(tk.END, f"• {u}")
        if not usuarios:
            lb_output.insert(tk.END, "No hay usuarios registrados.")
    except Exception as e:
        messagebox.showerror("Error", f"Error al listar usuarios: {str(e)}")

def listar_equipos():
    try:
        limpiar_salida()
        equipos = sis.listar_equipos()
        lb_output.insert(tk.END, "=== EQUIPOS REGISTRADOS ===")
        lb_output.insert(tk.END, "")  # Línea en blanco
        
        for e in equipos:
            politica_text = e.politica_id if e.politica_id else "Ninguna"
            # Obtener información de respaldos
            info_respaldos = e.obtener_info_respaldos()
            
            lb_output.insert(tk.END, f"• {e.nombre}")
            lb_output.insert(tk.END, f"  Área: {e.area}")
            lb_output.insert(tk.END, f"  Política: {politica_text}")
            
            if info_respaldos['tiene_respaldos']:
                lb_output.insert(tk.END, f"  Respaldo en: {info_respaldos['ultimo_nas']}")
                if info_respaldos['total_respaldos'] > 1:
                    lb_output.insert(tk.END, f"  Total de respaldos: {info_respaldos['total_respaldos']}")
            else:
                lb_output.insert(tk.END, f"  Respaldo en: Sin respaldos")
                
            lb_output.insert(tk.END, "")  # Línea en blanco para separar
            
        if not equipos:
            lb_output.insert(tk.END, "No hay equipos registrados.")
    except Exception as e:
        messagebox.showerror("Error", f"Error al listar equipos: {str(e)}")

def listar_nas():
    try:
        limpiar_salida()
        nas_list = sis.listar_nas()
        lb_output.insert(tk.END, "=== NAS REGISTRADOS ===")
        lb_output.insert(tk.END, "")  # Línea en blanco
        for n in nas_list:
            lb_output.insert(tk.END, f"• {n}")
        if not nas_list:
            lb_output.insert(tk.END, "No hay NAS registrados.")
    except Exception as e:
        messagebox.showerror("Error", f"Error al listar NAS: {str(e)}")

def listar_politicas():
    try:
        limpiar_salida()
        politicas = sis.listar_politicas()
        lb_output.insert(tk.END, "=== POLÍTICAS DE RESPALDO ===")
        lb_output.insert(tk.END, "")  # Línea en blanco
        for p in politicas:
            lb_output.insert(tk.END, f"• {p}")
        if not politicas:
            lb_output.insert(tk.END, "No hay políticas registradas.")
    except Exception as e:
        messagebox.showerror("Error", f"Error al listar políticas: {str(e)}")

def generar_reporte():
    try:
        limpiar_salida()
        reporte = current_user.generarReporte()
        lb_output.insert(tk.END, "=== REPORTE DEL SISTEMA ===")
        lb_output.insert(tk.END, "")  # Línea en blanco
        lb_output.insert(tk.END, reporte)
    except Exception as e:
        messagebox.showerror("Error", f"Error al generar reporte: {str(e)}")

def salir():
    root.destroy()
    sys.exit(0)

def ajustar_menu_por_rol():
    if current_user is None:
        return
    
    # Primero deshabilitar todo
    for i in range(acciones_menu.index("end") + 1):
        try:
            acciones_menu.entryconfig(i, state="disabled")
        except:
            pass
    
    # Luego habilitar según el rol
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
        acciones_menu.entryconfig("Listar respaldos por equipo", state="normal")
        acciones_menu.entryconfig("Generar reporte", state="normal")
    elif current_user.role == 'coordinador':
        acciones_menu.entryconfig("Restaurar equipo", state="normal")
        acciones_menu.entryconfig("Listar usuarios", state="normal")
        acciones_menu.entryconfig("Listar equipos", state="normal")
        acciones_menu.entryconfig("Listar NAS", state="normal")
        acciones_menu.entryconfig("Listar políticas", state="normal")
        acciones_menu.entryconfig("Listar respaldos por equipo", state="normal")
        acciones_menu.entryconfig("Generar reporte", state="normal")

def actualizar_info_usuario():
    if current_user:
        lbl_user_info.config(text=f"Usuario: {current_user.nombre} ({current_user.role}) - {current_user.email}")
        lbl_help.config(text=f"Sistema listo. Bienvenido {current_user.nombre}. Use el menú 'Acciones' para comenzar.")
    else:
        lbl_user_info.config(text="Usuario: No autenticado")
        lbl_help.config(text="Sistema listo. Use el menú 'Acciones' para comenzar.")

# Interfaz gráfica mejorada
root = tk.Tk()
root.title("Sistema de Gestión de Respaldos")
root.geometry("900x600")
root.minsize(800, 500)

# Centrar la ventana principal
centrar_ventana(root, 900, 600)

# Configurar estilo para mejor apariencia
style = ttk.Style()
style.configure("TFrame", background="#f0f0f0")
style.configure("TLabel", background="#f0f0f0", font=("Segoe UI", 10))
style.configure("TButton", font=("Segoe UI", 9))
style.configure("Title.TLabel", font=("Segoe UI", 12, "bold"))

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
acciones_menu.add_command(label="Listar respaldos por equipo", command=listar_respaldos_equipo)
acciones_menu.add_separator()
acciones_menu.add_command(label="Generar reporte", command=generar_reporte)
menubar.add_cascade(label="Acciones", menu=acciones_menu)

archivo_menu = tk.Menu(menubar, tearoff=0)
archivo_menu.add_command(label="Salir", command=salir)
menubar.add_cascade(label="Archivo", menu=archivo_menu)

root.config(menu=menubar)

# Frame principal con mejor distribución
main_frame = ttk.Frame(root, padding=(15, 15))
main_frame.pack(fill=tk.BOTH, expand=True)

# Título de la aplicación
title_frame = ttk.Frame(main_frame)
title_frame.pack(fill=tk.X, pady=(0, 10))

lbl_title = ttk.Label(title_frame, text="Sistema de Gestión de Respaldos", 
                     style="Title.TLabel", foreground="#2c3e50")
lbl_title.pack()

# Frame de información del usuario
user_frame = ttk.Frame(main_frame)
user_frame.pack(fill=tk.X, pady=(0, 10))

lbl_user_info = ttk.Label(user_frame, text="Usuario: No autenticado", 
                         font=("Segoe UI", 10, "bold"), foreground="#34495e")
lbl_user_info.pack(side=tk.LEFT)

# Frame de salida con mejor organización
output_frame = ttk.LabelFrame(main_frame, text=" Salida del Sistema ", padding=(10, 10))
output_frame.pack(fill=tk.BOTH, expand=True)

# Configurar mejor el Listbox y Scrollbar
frame_list = ttk.Frame(output_frame)
frame_list.pack(fill=tk.BOTH, expand=True)

# Scrollbar horizontal y vertical
v_scrollbar = ttk.Scrollbar(frame_list, orient=tk.VERTICAL)
h_scrollbar = ttk.Scrollbar(frame_list, orient=tk.HORIZONTAL)

lb_output = tk.Listbox(frame_list, 
                      yscrollcommand=v_scrollbar.set,
                      xscrollcommand=h_scrollbar.set,
                      font=("Consolas", 10),
                      bg="white",
                      selectbackground="#3498db",
                      selectmode=tk.SINGLE)

v_scrollbar.config(command=lb_output.yview)
h_scrollbar.config(command=lb_output.xview)

# Grid layout para mejor control
v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
lb_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Frame de ayuda/información
help_frame = ttk.Frame(main_frame)
help_frame.pack(fill=tk.X, pady=(10, 0))

lbl_help = ttk.Label(help_frame, 
                    text="Sistema listo. Use el menú 'Acciones' para comenzar.",
                    font=("Segoe UI", 9),
                    foreground="#7f8c8d")
lbl_help.pack(side=tk.LEFT)

# Centrar también los diálogos
def centrar_dialogos():
    """Configura los diálogos para que aparezcan centrados"""
    simpledialog.Dialog.root = root

root.after(100, lambda: [centrar_dialogos(), login_inicial()])
root.mainloop()