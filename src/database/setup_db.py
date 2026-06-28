from src.database.config import engine, Base

# Importamos TODAS las tablas para que SQLAlchemy las registre en su 'metadata'
# Si no las importamos aquí, SQLAlchemy no sabrá que existen y no las creará.
from src.models.maestros import Chofer, Camion, Remolque, Cliente, Ruta, TipoMantenimiento
from src.models.operaciones import Nomina, Viaje, Mantenimiento
from src.models.admin import Administrador

print("Iniciando la construcción completa de la base de datos...")

# Esta instrucción lee todos los modelos importados arriba y los crea en PostgreSQL
# Respetando automáticamente el orden lógico de las llaves foráneas.
Base.metadata.create_all(bind=engine)

print("✅ ¡Éxito! Todas las 10 tablas y sus relaciones fueron creadas en PostgreSQL.")