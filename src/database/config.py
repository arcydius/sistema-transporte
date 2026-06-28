import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# URL de conexión sin contraseña
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
# TEST DE CONEXIÓN (Puedes borrar esto luego)
# ==========================================
if __name__ == "__main__":
    try:
        with engine.connect() as connection:
            print("✅ ¡ÉXITO! Conexión a PostgreSQL establecida correctamente.")
    except Exception as e:
        print(f"❌ ERROR de conexión: {e}")