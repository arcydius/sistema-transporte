import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Asegurar que la carpeta 'src' esté en el PYTHONPATH
sys_src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if sys_src_path not in sys.path:
    sys.path.insert(0, sys_src_path)

# URL de conexión
DATABASE_URL = "postgresql+psycopg://postgres:1234@localhost:5432/transporte_montenegro"

engine = create_engine(DATABASE_URL, echo=False) 
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
            print("✅ ¡ÉXITO! Conexión a PostgreSQL establecida correctamente.")
    except Exception as e:
        print(f"❌ ERROR de conexión: {e}")