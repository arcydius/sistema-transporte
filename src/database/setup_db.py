import os
import sys

sys_src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if sys_src_path not in sys.path:
    sys.path.insert(0, sys_src_path)

from database.config import engine, Base, SessionLocal
from models.maestros import Chofer, Camion, Remolque, Cliente, Ruta, TipoMantenimiento
from models.operaciones import Nomina, Viaje, Mantenimiento
from models.admin import Administrador
from controllers.configuracion_controller import hash_password

print("Iniciando la construccion completa de la base de datos...")

# Esta instruccion lee todos los modelos importados arriba y los crea en PostgreSQL
# Respetando automaticamente el orden logico de las llaves foraneas.
Base.metadata.create_all(bind=engine)

print("[OK] Exito! Todas las tablas y sus relaciones fueron creadas en PostgreSQL.")

# Inicialización de usuario administrador por defecto si la tabla está vacía
db = SessionLocal()
try:
    if db.query(Administrador).count() == 0:
        admin_defecto = Administrador(
            username="admin",
            password_hash=hash_password("admin123"),
            nombre_completo="Administrador Principal"
        )
        db.add(admin_defecto)
        db.commit()
        print("[OK] Usuario administrador por defecto creado ('admin' / 'admin123').")
    else:
        print("[OK] La tabla de administradores ya contiene usuarios registrados.")
except Exception as e:
    db.rollback()
    print(f"[WARN] Nota al verificar administrador inicial: {e}")
finally:
    db.close()