from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from database.config import Base

class Nomina(Base):
    __tablename__ = "nominas"
    
    id_nomina = Column(Integer, primary_key=True, autoincrement=True)
    id_chofer = Column(Integer, ForeignKey("choferes.id_chofer"), nullable=False)
    fecha_emision = Column(Date)
    periodo_desde = Column(Date)
    periodo_hasta = Column(Date)
    total_ingresos_fletes = Column(Numeric(7, 2))
    total_costo_gasoil = Column(Numeric(7, 2))
    monto_neto_comision = Column(Numeric(7, 2))

    # Relación para el joinedload en el controlador
    chofer = relationship("Chofer")

class Viaje(Base):
    __tablename__ = "viajes"
    id_viaje = Column(Integer, primary_key=True, autoincrement=True)
    # Puedes agregar los campos de viajes aquí cuando los necesites

class Mantenimiento(Base):
    __tablename__ = "mantenimientos"

    id_mantenimiento = Column(Integer, primary_key=True, autoincrement=True)
    id_tipo = Column(Integer, ForeignKey("tipos_mantenimiento.id_tipo"), nullable=False)
    fecha_servicio = Column(Date)
    descripcion_trabajo = Column(Text)
    monto_invertido = Column(Numeric(7, 2))
    tecnico_responsable = Column(String(30))
    
    id_camion = Column(Integer, ForeignKey("camiones.id_camion"), nullable=True)
    id_remolque = Column(Integer, ForeignKey("remolques.id_remolque"), nullable=True)

    # Relaciones necesarias para el joinedload
    camion = relationship("Camion")
    remolque = relationship("Remolque")
    tipo = relationship("TipoMantenimiento")