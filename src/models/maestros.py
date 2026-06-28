from sqlalchemy import Column, Integer, String, Date, Numeric
from database.config import Base

class Chofer(Base):
    __tablename__ = "choferes"
    id_chofer = Column(Integer, primary_key=True, autoincrement=True)
    cedula_identidad = Column(String(8), unique=True, nullable=False)
    nombre_completo = Column(String(25), nullable=False)
    contacto = Column(String(30))

class Camion(Base):
    __tablename__ = "camiones"
    id_camion = Column(Integer, primary_key=True, autoincrement=True)
    placa = Column(String(7), unique=True, nullable=False)
    alias_identificador = Column(String(15))
    marca = Column(String(20))
    vencimiento_rcv = Column(Date)
    vencimiento_trimestre = Column(Date)

class Remolque(Base):
    __tablename__ = "remolques"
    id_remolque = Column(Integer, primary_key=True, autoincrement=True)
    placa = Column(String(7), unique=True, nullable=False)
    alias_identificador = Column(String(20))
    vencimiento_rcv = Column(Date)
    vencimiento_trimestre = Column(Date)

class Cliente(Base):
    __tablename__ = "clientes"
    id_cliente = Column(Integer, primary_key=True, autoincrement=True)
    nombre_cliente = Column(String(25), nullable=False)
    contacto_principal = Column(String(100))

class Ruta(Base):
    __tablename__ = "rutas"
    id_ruta = Column(Integer, primary_key=True, autoincrement=True)
    descripcion_trayecto = Column(String(255), nullable=False)
    costo_unitario_sugerido = Column(Numeric(7, 2))

class TipoMantenimiento(Base):
    __tablename__ = "tipos_mantenimiento"
    id_tipo = Column(Integer, primary_key=True, autoincrement=True)
    nombre_tipo = Column(String(45))