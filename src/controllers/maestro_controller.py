from database.config import SessionLocal
from models.maestros import Chofer, Camion, Cliente, Ruta, TipoMantenimiento, Remolque
from models.operaciones import Mantenimiento, Nomina, Viaje
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
def _parse_fecha_maestro(date_val):
    if not date_val:
        return None
    if isinstance(date_val, datetime.date):
        return date_val
    try:
        return datetime.datetime.strptime(str(date_val).strip(), "%d/%m/%Y").date()
    except ValueError:
        try:
            return datetime.datetime.strptime(str(date_val).strip(), "%Y-%m-%d").date()
        except ValueError:
            return None

def registrar_camion(placa, alias, marca, vencimiento_rcv=None, vencimiento_trimestre=None):
    db = SessionLocal()
    try:
        nuevo_camion = Camion(
            placa=placa.upper(),
            alias_identificador=alias,
            marca=marca,
            vencimiento_rcv=_parse_fecha_maestro(vencimiento_rcv),
            vencimiento_trimestre=_parse_fecha_maestro(vencimiento_trimestre)
        )
        db.add(nuevo_camion)
        db.commit()
        return True, "Camión registrado exitosamente."
    except Exception as e:
        db.rollback()
        return False, f"Error: {str(e)}"
    finally: db.close()

def obtener_camiones():
    db = SessionLocal()
    try: return db.query(Camion).order_by(Camion.placa).all()
    finally: db.close()

def actualizar_camion(id_camion, placa, alias, marca, vencimiento_rcv=None, vencimiento_trimestre=None):
    db = SessionLocal()
    try:
        camion = db.query(Camion).filter(Camion.id_camion == id_camion).first()
        if not camion: return False, "No encontrado."
        camion.placa = placa.upper()
        camion.alias_identificador = alias
        camion.marca = marca
        camion.vencimiento_rcv = _parse_fecha_maestro(vencimiento_rcv)
        camion.vencimiento_trimestre = _parse_fecha_maestro(vencimiento_trimestre)
        db.commit()
        return True, "Camión actualizado exitosamente."
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
            return True, "Camión eliminado."
        return False, "No encontrado."
    except Exception as e:
        db.rollback()
        return False, f"Error: {str(e)}"
    finally: db.close()

def obtener_remolques():
    db = SessionLocal()
    try: return db.query(Remolque).order_by(Remolque.placa).all()
    finally: db.close()

def registrar_remolque(placa, alias, vencimiento_rcv=None, vencimiento_trimestre=None):
    db = SessionLocal()
    try:
        nuevo_remolque = Remolque(
            placa=placa.upper(),
            alias_identificador=alias,
            vencimiento_rcv=_parse_fecha_maestro(vencimiento_rcv),
            vencimiento_trimestre=_parse_fecha_maestro(vencimiento_trimestre)
        )
        db.add(nuevo_remolque)
        db.commit()
        return True, "Remolque registrado exitosamente."
    except Exception as e:
        db.rollback()
        return False, f"Error: {str(e)}"
    finally: db.close()

def actualizar_remolque(id_remolque, placa, alias, vencimiento_rcv=None, vencimiento_trimestre=None):
    db = SessionLocal()
    try:
        remolque = db.query(Remolque).filter(Remolque.id_remolque == id_remolque).first()
        if not remolque: return False, "No encontrado."
        remolque.placa = placa.upper()
        remolque.alias_identificador = alias
        remolque.vencimiento_rcv = _parse_fecha_maestro(vencimiento_rcv)
        remolque.vencimiento_trimestre = _parse_fecha_maestro(vencimiento_trimestre)
        db.commit()
        return True, "Remolque actualizado exitosamente."
    except Exception as e:
        db.rollback()
        return False, f"Error: {str(e)}"
    finally: db.close()

def eliminar_remolque(id_remolque):
    db = SessionLocal()
    try:
        remolque = db.query(Remolque).filter(Remolque.id_remolque == id_remolque).first()
        if remolque:
            db.delete(remolque)
            db.commit()
            return True, "Remolque eliminado."
        return False, "No encontrado."
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
        ruta.costo_unitario_sugerido = Decimal(costo) if costo else Decimal("0.00")  # type: ignore
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

def registrar_mantenimiento(id_tipo: int, descripcion: str, monto: float, tecnico: str, id_camion: int | None = None, id_remolque: int | None = None):
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

def actualizar_mantenimiento(id_mantenimiento, id_tipo, descripcion, monto, tecnico, id_camion=None, id_remolque=None):
    db = SessionLocal()
    try:
        registro = db.query(Mantenimiento).filter(Mantenimiento.id_mantenimiento == id_mantenimiento).first()
        if not registro:
            return False, "Registro de mantenimiento no encontrado."
        
        registro.id_tipo = id_tipo
        registro.descripcion_trabajo = descripcion
        registro.monto_invertido = Decimal(str(monto or 0))  # type: ignore
        registro.tecnico_responsable = tecnico
        registro.id_camion = id_camion if id_camion else None  # type: ignore
        registro.id_remolque = id_remolque if id_remolque else None  # type: ignore
        
        db.commit()
        return True, "Orden de mantenimiento actualizada correctamente."
    except Exception as e:
        db.rollback()
        return False, f"Error al actualizar: {str(e)}"
    finally:
        db.close()

def eliminar_mantenimiento(id_mantenimiento):
    db = SessionLocal()
    try:
        registro = db.query(Mantenimiento).filter(Mantenimiento.id_mantenimiento == id_mantenimiento).first()
        if registro:
            db.delete(registro)
            db.commit()
            return True, "Registro de mantenimiento eliminado correctamente."
        return False, "Registro de mantenimiento no encontrado."
    except Exception as e:
        db.rollback()
        return False, f"Error al eliminar: {str(e)}"
    finally:
        db.close()


# ==========================================
# 6. NÓMINAS Y FINANZAS
# ==========================================
def parse_date(date_str):
    if not date_str: return None
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

def obtener_nominas():
    db = SessionLocal()
    try:
        return db.query(Nomina).options(joinedload(Nomina.chofer)).order_by(Nomina.fecha_emision.desc()).all()
    except Exception as e:
        print(f"Error al obtener nóminas: {e}")
        return []
    finally:
        db.close()

def registrar_nomina(id_chofer, fecha_emision, periodo_desde, periodo_hasta, ingresos, gasoil, comision):
    db = SessionLocal()
    try:
        nueva_nomina = Nomina(
            id_chofer=id_chofer,
            fecha_emision=parse_date(fecha_emision),
            periodo_desde=parse_date(periodo_desde),
            periodo_hasta=parse_date(periodo_hasta),
            total_ingresos_fletes=Decimal(str(ingresos or 0)),
            total_costo_gasoil=Decimal(str(gasoil or 0)),
            monto_neto_comision=Decimal(str(comision or 0))
        )
        db.add(nueva_nomina)
        db.commit()
        return True, "Nómina registrada correctamente."
    except Exception as e:
        db.rollback()
        return False, f"Error al registrar: {str(e)}"
    finally:
        db.close()

def actualizar_nomina(id_nomina, id_chofer, fecha_emision, periodo_desde, periodo_hasta, ingresos, gasoil, comision):
    db = SessionLocal()
    try:
        nomina = db.query(Nomina).filter(Nomina.id_nomina == id_nomina).first()
        if not nomina:
            return False, "Nómina no encontrada."
        
        nomina.id_chofer = id_chofer
        nomina.fecha_emision = parse_date(fecha_emision)  # type: ignore
        nomina.periodo_desde = parse_date(periodo_desde)  # type: ignore
        nomina.periodo_hasta = parse_date(periodo_hasta)  # type: ignore
        nomina.total_ingresos_fletes = Decimal(str(ingresos or 0))  # type: ignore
        nomina.total_costo_gasoil = Decimal(str(gasoil or 0))  # type: ignore
        nomina.monto_neto_comision = Decimal(str(comision or 0))  # type: ignore
        
        db.commit()
        return True, "Nómina actualizada correctamente."
    except Exception as e:
        db.rollback()
        return False, f"Error al actualizar: {str(e)}"
    finally:
        db.close()

def eliminar_nomina(id_nomina):
    db = SessionLocal()
    try:
        nomina = db.query(Nomina).filter(Nomina.id_nomina == id_nomina).first()
        if nomina:
            db.delete(nomina)
            db.commit()
            return True, "Nómina eliminada correctamente."
        return False, "Nómina no encontrada."
    except Exception as e:
        db.rollback()
        return False, f"Error al eliminar: {str(e)}"
    finally:
        db.close()


# ==========================================
# 7. VIAJES (FLETES)
# ==========================================
def registrar_flete(id_cliente, id_ruta, id_chofer, id_camion, id_remolque, estatus, gasoil, precio_gasoil, mora, costo_unitario, cantidad_fletes=1):
    db = SessionLocal()
    try:
        try:
            cant = int(cantidad_fletes) if cantidad_fletes else 1
            if cant < 1:
                cant = 1
        except (ValueError, TypeError):
            cant = 1

        litros = Decimal(str(gasoil or 0))
        precio_litro = Decimal(str(precio_gasoil or 0))
        costo_gasoil_total = litros * precio_litro
        costo_unit = Decimal(str(costo_unitario or 0))
        
        nuevo_viaje = Viaje(
            fecha_operacion=datetime.date.today(),
            id_chofer=int(id_chofer) if id_chofer and id_chofer != "0" else None,
            id_camion=int(id_camion) if id_camion else None,
            id_remolque=int(id_remolque) if id_remolque and id_remolque != "none" else None,
            id_cliente=int(id_cliente) if id_cliente else None,
            id_ruta=int(id_ruta) if id_ruta else None,
            cantidad_fletes=cant,
            costo_unitario_aplicado=costo_unit,
            monto_mora_espera=Decimal(str(mora or 0)),
            litros_gasoil_consumido=litros,
            precio_litro_gasoil=precio_litro,
            costo_total_gasoil=costo_gasoil_total,
            estatus_pago_cliente=estatus,
            id_nomina_pago=None
        )
        db.add(nuevo_viaje)
        db.commit()
        return True, "Viaje registrado correctamente en el sistema."
    except Exception as e:
        db.rollback()
        return False, f"Error al registrar viaje: {str(e)}"
    finally:
        db.close()