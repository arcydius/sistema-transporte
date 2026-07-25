from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, Text, Enum
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

    chofer = relationship("Chofer")

class Viaje(Base):
    __tablename__ = "viajes"
    
    id_viaje = Column(Integer, primary_key=True, autoincrement=True)
    fecha_operacion = Column(Date)
    id_chofer = Column(Integer, ForeignKey("choferes.id_chofer"), nullable=True)
    id_camion = Column(Integer, ForeignKey("camiones.id_camion"), nullable=False)
    id_remolque = Column(Integer, ForeignKey("remolques.id_remolque"), nullable=True)
    id_cliente = Column(Integer, ForeignKey("clientes.id_cliente"), nullable=False)
    id_ruta = Column(Integer, ForeignKey("rutas.id_ruta"), nullable=False)
    cantidad_fletes = Column(Integer, default=1)
    costo_unitario_aplicado = Column(Numeric(7, 2))
    monto_mora_espera = Column(Numeric(7, 2))
    litros_gasoil_consumido = Column(Numeric(7, 2))
    precio_litro_gasoil = Column(Numeric(7, 2))
    costo_total_gasoil = Column(Numeric(7, 2))
    
    # Se corrige el tipo para enlazarse correctamente con el ENUM de PostgreSQL
    estatus_pago_cliente = Column(Enum("Pendiente", "Pagado", name="estatus_pago", create_type=False))
    
    id_nomina_pago = Column(Integer, nullable=True)

    chofer = relationship("Chofer")
    camion = relationship("Camion")
    remolque = relationship("Remolque")
    cliente = relationship("Cliente")
    ruta = relationship("Ruta")

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

    camion = relationship("Camion")
    remolque = relationship("Remolque")
    tipo = relationship("TipoMantenimiento")