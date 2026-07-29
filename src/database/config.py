import os
import sys
import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

# Asegurar que la carpeta 'src' esté en el PYTHONPATH
sys_src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if sys_src_path not in sys.path:
    sys.path.insert(0, sys_src_path)

def obtener_ruta_config_db():
    """Obtiene la ruta del archivo de configuración JSON en la carpeta Documentos del usuario."""
    user_docs = os.path.expanduser("~/Documents")
    if not os.path.exists(user_docs):
        user_docs = os.path.expanduser("~")
    target_dir = os.path.join(user_docs, "SGTM")
    os.makedirs(target_dir, exist_ok=True)
    return os.path.join(target_dir, "config_db.json")

def cargar_o_crear_config():
    """Carga o genera la configuración de conexión a la base de datos PostgreSQL desde JSON."""
    config_file = obtener_ruta_config_db()
    default_config = {
        "host": "localhost",
        "port": 5432,
        "user": "postgres",
        "password": "1234",
        "dbname": "transporte_montenegro"
    }

    # Leer variables de entorno si existen
    if os.getenv("DB_HOST"):
        default_config["host"] = os.getenv("DB_HOST")
    if os.getenv("DB_PORT"):
        try:
            default_config["port"] = int(os.getenv("DB_PORT"))
        except ValueError:
            pass
    if os.getenv("DB_USER"):
        default_config["user"] = os.getenv("DB_USER")
    if os.getenv("DB_PASSWORD") is not None:
        default_config["password"] = os.getenv("DB_PASSWORD")
    if os.getenv("DB_NAME"):
        default_config["dbname"] = os.getenv("DB_NAME")

    if os.path.exists(config_file):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                saved_cfg = json.load(f)
                default_config.update(saved_cfg)
        except Exception as e:
            print(f"[-] Error leyendo config_db.json: {e}")
    else:
        try:
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=4)
            print(f"[+] Archivo de configuración creado en: {config_file}")
        except Exception as e:
            print(f"[-] Error creando config_db.json: {e}")

    return default_config

def construir_engine():
    """Construye un motor SQLAlchemy para PostgreSQL leyendo el JSON y autocreando la BD si no existe."""
    cfg = cargar_o_crear_config()

    user = cfg.get("user", "postgres")
    pwd = cfg.get("password", "1234")
    host = cfg.get("host", "localhost")
    port = cfg.get("port", 5432)
    dbname = cfg.get("dbname", "transporte_montenegro")

    # Armar la URL de conexión de PostgreSQL
    url = f"postgresql+psycopg://{user}:{pwd}@{host}:{port}/{dbname}"

    try:
        # Intentar conectar a la base de datos PostgreSQL indicada
        eng = create_engine(url, echo=False, pool_pre_ping=True)
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"[+] Conexión exitosa a PostgreSQL: '{dbname}' en {host}:{port}.")
        return eng

    except Exception as e:
        err_msg = str(e).lower()
        # Si la base de datos PostgreSQL no existe, la creamos automáticamente
        if "does not exist" in err_msg or "no existe" in err_msg or "unknown database" in err_msg:
            try:
                print(f"[!] La base de datos '{dbname}' no existe en PostgreSQL. Creándola automáticamente...")
                url_default = f"postgresql+psycopg://{user}:{pwd}@{host}:{port}/postgres"
                eng_temp = create_engine(url_default, isolation_level="AUTOCOMMIT")
                with eng_temp.connect() as conn:
                    conn.execute(text(f'CREATE DATABASE "{dbname}"'))
                print(f"[+] Base de datos '{dbname}' creada exitosamente en PostgreSQL.")
                
                # Reconectar a la base recién creada
                eng_nueva = create_engine(url, echo=False, pool_pre_ping=True)
                return eng_nueva
            except Exception as ex_create:
                print(f"[-] Error al intentar crear la base de datos automáticamente: {ex_create}")
                raise e
        else:
            print(f"[-] Error al conectar a PostgreSQL: {e}")
            raise e

engine = construir_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# TEST DE CONEXIÓN
# ==========================================
if __name__ == "__main__":
    try:
        with engine.connect() as connection:
            print("[+] EXITO! Conexion a PostgreSQL establecida correctamente.")
    except Exception as e:
        print(f"[-] ERROR de conexion a PostgreSQL: {e}")