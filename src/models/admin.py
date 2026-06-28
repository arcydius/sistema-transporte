from sqlalchemy import Column, Integer, String
from src.database.config import Base

class Administrador(Base):
    __tablename__ = "administrador"
    id_admin = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(15), unique=True, nullable=False)
    password_hash = Column(String(255))
    nombre_completo = Column(String(25))