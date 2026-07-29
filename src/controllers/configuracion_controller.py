import os
import hashlib
import datetime
from sqlalchemy import inspect, text
try:
    from database.config import SessionLocal, engine
    from models.admin import Administrador
except ImportError:
    from src.database.config import SessionLocal, engine
    from src.models.admin import Administrador

# ==========================================
# SEGURIDAD Y HASHING DE CONTRASEÑAS
# ==========================================
def hash_password(password: str) -> str:
    """Genera un hash seguro PBKDF2-HMAC-SHA256 con un salt aleatorio."""
    if not password:
        return ""
    salt = os.urandom(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return f"{salt.hex()}:{pwd_hash.hex()}"

def verify_password(password: str, stored_hash: str) -> bool:
    """Verifica si una contraseña coincide con el hash almacenado."""
    if not stored_hash or not password:
        return False
    if ":" not in stored_hash:
        # Compatibilidad con contraseñas en texto plano o SHA256 simple previa
        if stored_hash == hashlib.sha256(password.encode('utf-8')).hexdigest() or stored_hash == password:
            return True
        return False
    try:
        salt_hex, hash_hex = stored_hash.split(":", 1)
        salt = bytes.fromhex(salt_hex)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return pwd_hash.hex() == hash_hex
    except Exception:
        return False

# ==========================================
# GESTIÓN DE USUARIOS / ADMINISTRADORES
# ==========================================
def obtener_usuarios():
    """Devuelve la lista de todos los administradores/usuarios."""
    db = SessionLocal()
    try:
        return db.query(Administrador).order_by(Administrador.id_admin).all()
    except Exception as e:
        print(f"Error al obtener usuarios: {e}")
        return []
    finally:
        db.close()

def obtener_usuario_por_id(id_admin: int):
    """Obtiene un usuario por su ID."""
    db = SessionLocal()
    try:
        return db.query(Administrador).filter(Administrador.id_admin == id_admin).first()
    finally:
        db.close()

def registrar_usuario(username: str, password: str, nombre_completo: str):
    """Registra un nuevo usuario en la base de datos."""
    if not username or not password or not nombre_completo:
        return False, "Todos los campos (usuario, contraseña y nombre) son obligatorios."
    
    username_clean = username.strip()
    if len(username_clean) > 15:
        return False, "El nombre de usuario no puede exceder 15 caracteres."
        
    db = SessionLocal()
    try:
        # Verificar si el nombre de usuario ya existe
        existente = db.query(Administrador).filter(Administrador.username.ilike(username_clean)).first()
        if existente:
            return False, f"El nombre de usuario '{username_clean}' ya está registrado."
            
        nuevo_user = Administrador(
            username=username_clean,
            password_hash=hash_password(password),
            nombre_completo=nombre_completo.strip()
        )
        db.add(nuevo_user)
        db.commit()
        return True, f"Usuario '{username_clean}' registrado con éxito."
    except Exception as e:
        db.rollback()
        return False, f"Error al registrar usuario: {str(e)}"
    finally:
        db.close()

def actualizar_usuario(id_admin: int, username: str, nombre_completo: str, password: str | None = None):
    """Actualiza los datos de un usuario existente. Opcionalmente actualiza la contraseña."""
    if not username or not nombre_completo:
        return False, "El usuario y el nombre completo son obligatorios."
        
    username_clean = username.strip()
    if len(username_clean) > 15:
        return False, "El nombre de usuario no puede exceder 15 caracteres."

    db = SessionLocal()
    try:
        user = db.query(Administrador).filter(Administrador.id_admin == id_admin).first()
        if not user:
            return False, "Usuario no encontrado."
            
        # Verificar duplicado de username en otro usuario
        duplicado = db.query(Administrador).filter(
            Administrador.username.ilike(username_clean),
            Administrador.id_admin != id_admin
        ).first()
        if duplicado:
            return False, f"El nombre de usuario '{username_clean}' ya pertenece a otro usuario."
            
        user.username = username_clean
        user.nombre_completo = nombre_completo.strip()
        if password and password.strip():
            user.password_hash = hash_password(password.strip())
            
        db.commit()
        return True, f"Usuario '{username_clean}' actualizado correctamente."
    except Exception as e:
        db.rollback()
        return False, f"Error al actualizar usuario: {str(e)}"
    finally:
        db.close()

def eliminar_usuario(id_admin: int):
    """Elimina un usuario. Evita eliminar si es el único usuario administrador en el sistema."""
    db = SessionLocal()
    try:
        total_usuarios = db.query(Administrador).count()
        if total_usuarios <= 1:
            return False, "No se puede eliminar el único usuario administrador del sistema."
            
        user = db.query(Administrador).filter(Administrador.id_admin == id_admin).first()
        if not user:
            return False, "Usuario no encontrado."
            
        username_del = user.username
        db.delete(user)
        db.commit()
        return True, f"Usuario '{username_del}' eliminado correctamente."
    except Exception as e:
        db.rollback()
        return False, f"Error al eliminar usuario: {str(e)}"
    finally:
        db.close()

def cambiar_contrasena(id_admin: int | None, pass_actual: str, pass_nueva: str):
    """Valida la contraseña actual y actualiza la contraseña de un usuario o del admin principal."""
    if not pass_actual or not pass_nueva:
        return False, "Debe ingresar la contraseña actual y la nueva contraseña."
        
    db = SessionLocal()
    try:
        if id_admin:
            user = db.query(Administrador).filter(Administrador.id_admin == id_admin).first()
        else:
            user = db.query(Administrador).order_by(Administrador.id_admin).first()
            
        if not user:
            return False, "Usuario no encontrado."
            
        if not verify_password(pass_actual, user.password_hash):
            return False, "La contraseña actual es incorrecta."
            
        user.password_hash = hash_password(pass_nueva)
        db.commit()
        return True, "Contraseña actualizada exitosamente."
    except Exception as e:
        db.rollback()
        return False, f"Error al actualizar la contraseña: {str(e)}"
    finally:
        db.close()

def verificar_credenciales(username: str, password: str):
    """Verifica las credenciales de inicio de sesión."""
    db = SessionLocal()
    try:
        user = db.query(Administrador).filter(Administrador.username.ilike(username.strip())).first()
        if user and verify_password(password, user.password_hash):
            return True, user
        return False, "Usuario o contraseña incorrectos."
    except Exception as e:
        return False, f"Error de autenticación: {str(e)}"
    finally:
        db.close()

# ==========================================
# GESTIÓN DE RESPALDOS (BACKUPS)
# ==========================================
def obtener_directorio_backups(custom_dir: str | None = None) -> str:
    """Obtiene la ruta del directorio de respaldos en la carpeta Documentos del usuario."""
    if custom_dir and os.path.exists(custom_dir):
        return custom_dir
    
    user_docs = os.path.expanduser("~/Documents")
    if not os.path.exists(user_docs):
        user_docs = os.path.expanduser("~")
    
    backup_dir = os.path.join(user_docs, "SGTM", "Backups")
    os.makedirs(backup_dir, exist_ok=True)
    return backup_dir

def crear_backup(directorio_destino: str | None = None):
    """
    Genera un respaldo de la base de datos.
    Genera un script de respaldo SQL exportando las tablas del sistema.
    """
    try:
        backup_dir = obtener_directorio_backups(directorio_destino)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"backup_transporte_{timestamp}.sql"
        filepath = os.path.join(backup_dir, filename)

        inspector = inspect(engine)
        table_names = inspector.get_table_names()

        with SessionLocal() as db, open(filepath, "w", encoding="utf-8") as f:
            f.write(f"-- SGTM Respaldo de Base de Datos\n")
            f.write(f"-- Fecha de generación: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            for table in table_names:
                f.write(f"-- Tabla: {table}\n")
                result = db.execute(text(f'SELECT * FROM "{table}"'))
                rows = result.fetchall()
                cols = result.keys()

                for row in rows:
                    cols_str = ", ".join([f'"{c}"' for c in cols])
                    vals = []
                    for v in row:
                        if v is None:
                            vals.append("NULL")
                        elif isinstance(v, (int, float)):
                            vals.append(str(v))
                        elif isinstance(v, (datetime.date, datetime.datetime)):
                            vals.append(f"'{v.isoformat()}'")
                        else:
                            val_escaped = str(v).replace("'", "''")
                            vals.append(f"'{val_escaped}'")
                    vals_str = ", ".join(vals)
                    f.write(f'INSERT INTO "{table}" ({cols_str}) VALUES ({vals_str});\n')
                f.write("\n")

        size_kb = os.path.getsize(filepath) / 1024
        return True, f"Respaldo generado exitosamente ({filename}, {size_kb:.1f} KB) en {filepath}."
    except Exception as e:
        return False, f"Error al generar respaldo: {str(e)}"

def obtener_lista_backups(directorio_destino: str | None = None):
    """Devuelve la lista de archivos de respaldo disponibles en Documentos y carpeta local."""
    try:
        backup_dir = obtener_directorio_backups(directorio_destino)
        directorios = [backup_dir]
        
        # También buscar en la carpeta 'backups' del proyecto por retrocompatibilidad
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        local_backup_dir = os.path.join(base_dir, "backups")
        if os.path.exists(local_backup_dir) and local_backup_dir not in directorios:
            directorios.append(local_backup_dir)

        backups = []
        archivos_procesados = set()

        for d in directorios:
            if os.path.exists(d):
                for file in sorted(os.listdir(d), reverse=True):
                    if (file.endswith(".sql") or file.endswith(".db") or file.endswith(".bak")) and file not in archivos_procesados:
                        archivos_procesados.add(file)
                        full_path = os.path.join(d, file)
                        stat = os.stat(full_path)
                        backups.append({
                            "filename": file,
                            "filepath": full_path,
                            "size_bytes": stat.st_size,
                            "fecha": datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                        })
        return sorted(backups, key=lambda x: x["filename"], reverse=True)
    except Exception as e:
        print(f"Error al listar respaldos: {e}")
        return []

def restaurar_backup(filepath: str):
    """Restaura la base de datos ejecutando las sentencias SQL del respaldo."""
    if not filepath or not os.path.exists(filepath):
        return False, "El archivo de respaldo no existe o la ruta no es válida."

    db = SessionLocal()
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            sql_script = f.read()

        statements = [stmt.strip() for stmt in sql_script.split(";") if stmt.strip() and not stmt.strip().startswith("--")]
        for stmt in statements:
            db.execute(text(stmt))
        db.commit()
        return True, f"Base de datos restaurada correctamente desde {os.path.basename(filepath)}."
    except Exception as e:
        db.rollback()
        return False, f"Error al restaurar respaldo: {str(e)}"
    finally:
        db.close()

def eliminar_backup(filepath: str):
    """Elimina un archivo de respaldo específico."""
    if not filepath or not os.path.exists(filepath):
        return False, "El archivo de respaldo no existe o la ruta no es válida."
        
    try:
        os.remove(filepath)
        return True, f"Respaldo '{os.path.basename(filepath)}' eliminado correctamente."
    except Exception as e:
        return False, f"Error al eliminar el respaldo: {str(e)}"
