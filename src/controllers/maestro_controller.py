from database.config import SessionLocal
from models.maestros import Chofer, Camion, Cliente, Ruta, TipoMantenimiento, Remolque
from models.operaciones import Mantenimiento
from sqlalchemy.orm import joinedload
from decimal import Decimal
import datetime

# ==========================================
# 1. CHOFERES
# ==========================================
def registrar_chofer(cedula, nombre, contacto):
    db = SessionLocal()
    try:
        nuevo_chofer = Chofer(cedula_identidad=cedula, nombre_completo=nombre, contacto=contacto)
        db.add(nuevo_chofer)
        db.commit()
        return True, "Chofer registrado."
    except Exception as e:
        db.rollback()
        return False, f"Error: {str(e)}"
    finally: db.close()

def obtener_choferes():
    db = SessionLocal()
    try: return db.query(Chofer).order_by(Chofer.nombre_completo).all()
    finally: db.close()

def actualizar_chofer(id_chofer, cedula, nombre, contacto):
    db = SessionLocal()
    try:
        chofer = db.query(Chofer).filter(Chofer.id_chofer == id_chofer).first()
        if not chofer: return False, "No encontrado."
        chofer.cedula_identidad, chofer.nombre_completo, chofer.contacto = cedula, nombre, contacto
        db.commit()
        return True, "Chofer actualizado."
    except Exception as e:
        db.rollback()
        return False, f"Error: {str(e)}"
    finally: db.close()

def eliminar_chofer(id_chofer):
    db = SessionLocal()
    try:
        chofer = db.query(Chofer).filter(Chofer.id_chofer == id_chofer).first()
        if chofer:
            db.delete(chofer)
            db.commit()
            return True, "Chofer eliminado."
        return False, "No encontrado."
    except Exception as e:
        db.rollback()
        return False, f"Error al eliminar: {str(e)}"
    finally: db.close()


# ==========================================
# 2. CAMIONES Y REMOLQUES (FLOTA)
# ==========================================
def registrar_camion(placa, alias, marca):
    db = SessionLocal()
    try:
        nuevo_camion = Camion(placa=placa.upper(), alias_identificador=alias, marca=marca)
        db.add(nuevo_camion)
        db.commit()
        return True, "Unidad registrada."
    except Exception as e:
        db.rollback()
        return False, f"Error: {str(e)}"
    finally: db.close()

def obtener_camiones():
    db = SessionLocal()
    try: return db.query(Camion).order_by(Camion.placa).all()
    finally: db.close()

def obtener_remolques():
    db = SessionLocal()
    try: return db.query(Remolque).order_by(Remolque.placa).all()
    finally: db.close()

def actualizar_camion(id_camion, placa, alias, marca):
    db = SessionLocal()
    try:
        camion = db.query(Camion).filter(Camion.id_camion == id_camion).first()
        if not camion: return False, "No encontrado."
        camion.placa, camion.alias_identificador, camion.marca = placa.upper(), alias, marca
        db.commit()
        return True, "Unidad actualizada."
    except Exception as e:
        db.rollback()
        return False, f"Error: {str(e)}"
    finally: db.close()

def eliminar_camion(id_camion):
    db = SessionLocal()
    try:
        camion = db.query(Camion).filter(Camion.id_camion == id_camion).first()
        if camion:
            db.delete(camion)
            db.commit()
            return True, "Unidad eliminada."
        return False, "No encontrada."
    except Exception as e:
        db.rollback()
        return False, f"Error: {str(e)}"
    finally: db.close()


# ==========================================
# 3. CLIENTES
# ==========================================
def registrar_cliente(nombre, contacto):
    db = SessionLocal()
    try:
        nuevo_cliente = Cliente(nombre_cliente=nombre, contacto_principal=contacto)
        db.add(nuevo_cliente)
        db.commit()
        return True, "Cliente registrado."
    except Exception as e:
        db.rollback()
        return False, f"Error: {str(e)}"
    finally: db.close()

def obtener_clientes():
    db = SessionLocal()
    try: return db.query(Cliente).order_by(Cliente.nombre_cliente).all()
    finally: db.close()

def actualizar_cliente(id_cliente, nombre, contacto):
    db = SessionLocal()
    try:
        cliente = db.query(Cliente).filter(Cliente.id_cliente == id_cliente).first()
        if not cliente: return False, "No encontrado."
        cliente.nombre_cliente, cliente.contacto_principal = nombre, contacto
        db.commit()
        return True, "Cliente actualizado."
    except Exception as e:
        db.rollback()
        return False, f"Error: {str(e)}"
    finally: db.close()

def eliminar_cliente(id_cliente):
    db = SessionLocal()
    try:
        cliente = db.query(Cliente).filter(Cliente.id_cliente == id_cliente).first()
        if cliente:
            db.delete(cliente)
            db.commit()
            return True, "Cliente eliminado."
        return False, "No encontrado."
    except Exception as e:
        db.rollback()
        return False, f"Error: {str(e)}"
    finally: db.close()


# ==========================================
# 4. RUTAS
# ==========================================
def registrar_ruta(descripcion, costo):
    db = SessionLocal()
    try:
        costo_val = Decimal(costo) if costo else Decimal("0.00")
        nueva_ruta = Ruta(descripcion_trayecto=descripcion, costo_unitario_sugerido=costo_val)
        db.add(nueva_ruta)
        db.commit()
        return True, "Ruta registrada."
    except Exception as e:
        db.rollback()
        return False, f"Error: {str(e)}"
    finally: db.close()

def obtener_rutas():
    db = SessionLocal()
    try: return db.query(Ruta).order_by(Ruta.descripcion_trayecto).all()
    finally: db.close()

def actualizar_ruta(id_ruta, descripcion, costo):
    db = SessionLocal()
    try:
        ruta = db.query(Ruta).filter(Ruta.id_ruta == id_ruta).first()
        if not ruta: return False, "No encontrado."
        ruta.descripcion_trayecto = descripcion
        ruta.costo_unitario_sugerido = Decimal(costo) if costo else Decimal("0.00") # type: ignore
        db.commit()
        return True, "Ruta actualizada."
    except Exception as e:
        db.rollback()
        return False, f"Error: {str(e)}"
    finally: db.close()

def eliminar_ruta(id_ruta):
    db = SessionLocal()
    try:
        ruta = db.query(Ruta).filter(Ruta.id_ruta == id_ruta).first()
        if ruta:
            db.delete(ruta)
            db.commit()
            return True, "Ruta eliminada."
        return False, "No encontrada."
    except Exception as e:
        db.rollback()
        return False, f"Error: {str(e)}"
    finally: db.close()


# ==========================================
# 5. TIPOS DE MANTENIMIENTO Y HISTORIAL
# ==========================================
def registrar_tipo_mantenimiento(nombre):
    db = SessionLocal()
    try:
        nuevo_tipo = TipoMantenimiento(nombre_tipo=nombre)
        db.add(nuevo_tipo)
        db.commit()
        return True, "Tipo de mantenimiento registrado."
    except Exception as e:
        db.rollback()
        return False, f"Error: {str(e)}"
    finally: db.close()

def obtener_tipos_mantenimiento():
    db = SessionLocal()
    try: return db.query(TipoMantenimiento).order_by(TipoMantenimiento.nombre_tipo).all()
    finally: db.close()

def actualizar_tipo_mantenimiento(id_tipo, nombre):
    db = SessionLocal()
    try:
        tipo = db.query(TipoMantenimiento).filter(TipoMantenimiento.id_tipo == id_tipo).first()
        if not tipo: return False, "No encontrado."
        tipo.nombre_tipo = nombre
        db.commit()
        return True, "Tipo actualizado."
    except Exception as e:
        db.rollback()
        return False, f"Error: {str(e)}"
    finally: db.close()

def eliminar_tipo_mantenimiento(id_tipo):
    db = SessionLocal()
    try:
        tipo = db.query(TipoMantenimiento).filter(TipoMantenimiento.id_tipo == id_tipo).first()
        if tipo:
            db.delete(tipo)
            db.commit()
            return True, "Tipo eliminado."
        return False, "No encontrado."
    except Exception as e:
        db.rollback()
        return False, f"Error: {str(e)}"
    finally: db.close()

def registrar_mantenimiento(id_tipo: int, descripcion: str, monto: float, tecnico: str, id_camion: int = None, id_remolque: int = None):
    db = SessionLocal()
    try:
        nuevo = Mantenimiento(
            id_tipo=id_tipo,
            fecha_servicio=datetime.date.today(),
            descripcion_trabajo=descripcion,
            monto_invertido=Decimal(str(monto or 0)),
            tecnico_responsable=tecnico,
            id_camion=id_camion if id_camion else None,
            id_remolque=id_remolque if id_remolque else None
        )
        db.add(nuevo)
        db.commit()
        return True, "Orden de mantenimiento registrada correctamente."
    except Exception as e:
        db.rollback()
        return False, f"Error al guardar: {str(e)}"
    finally:
        db.close()

def obtener_historial_mantenimiento():
    db = SessionLocal()
    try:
        return db.query(Mantenimiento).options(
            joinedload(Mantenimiento.camion),
            joinedload(Mantenimiento.remolque),
            joinedload(Mantenimiento.tipo)
        ).order_by(Mantenimiento.fecha_servicio.desc()).all()
    except Exception as e:
        print(f"Error al obtener historial: {e}")
        return []
    finally:
        db.close()