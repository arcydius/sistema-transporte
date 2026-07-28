import os
import sys
sys_src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if sys_src_path not in sys.path:
    sys.path.insert(0, sys_src_path)

import datetime
from decimal import Decimal
from sqlalchemy.orm import joinedload
from database.config import SessionLocal
from models.maestros import Chofer
from models.operaciones import Nomina, Viaje

def parse_date(date_str):
    """Convierte una cadena YYYY-MM-DD a objeto datetime.date seguro."""
    if not date_str:
        return None
    if isinstance(date_str, (datetime.date, datetime.datetime)):
        return date_str if isinstance(date_str, datetime.date) else date_str.date()
    try:
        return datetime.datetime.strptime(str(date_str).strip(), "%Y-%m-%d").date()
    except ValueError:
        return None

def obtener_fletes_pendientes_chofer(id_chofer: int, fecha_desde: str | None = None, fecha_hasta: str | None = None):
    """
    Obtiene todos los fletes realizador por el chofer que NO han sido incluidos en ninguna nómina previa.
    Opcionalmente filtra dentro de un rango de fecha_operacion.
    """
    db = SessionLocal()
    try:
        query = db.query(Viaje).options(
            joinedload(Viaje.chofer),
            joinedload(Viaje.cliente),
            joinedload(Viaje.ruta),
            joinedload(Viaje.camion)
        ).filter(
            Viaje.id_chofer == id_chofer,
            Viaje.id_nomina_pago.is_(None)
        )

        d_desde = parse_date(fecha_desde)
        if d_desde:
            query = query.filter(Viaje.fecha_operacion >= d_desde)

        d_hasta = parse_date(fecha_hasta)
        if d_hasta:
            query = query.filter(Viaje.fecha_operacion <= d_hasta)

        return query.order_by(Viaje.fecha_operacion.asc()).all()
    except Exception as e:
        print(f"[-] Error al obtener fletes pendientes: {e}")
        return []
    finally:
        db.close()

def calcular_resumen_comision(viajes_lista):
    """
    Calcula los totales y la comisión del 20% desglosada viaje por viaje.
    Para cada viaje i:
       Flete_i = (Cantidad_i * Costo_Unitario_i) + Mora_i
       Gasoil_i = Litros_i * Precio_Litro_i
       Base_i = Flete_i - Gasoil_i
       Comisión_i = Base_i * 0.20
    Monto Final = Suma(Comisión_i)
    """
    total_fletes = 0.0
    total_gasoil = 0.0
    comision_total = 0.0
    total_cant_viajes = 0

    detalles_viajes = []

    for v in viajes_lista:
        cant = int(getattr(v, 'cantidad_fletes', 1) or 1)
        costo_u = float(getattr(v, 'costo_unitario_aplicado', 0) or 0)
        mora = float(getattr(v, 'monto_mora_espera', 0) or 0)
        gasoil = float(getattr(v, 'costo_total_gasoil', 0) or 0)

        flete_item = (cant * costo_u) + mora
        base_item = flete_item - gasoil
        comision_item = base_item * 0.20

        total_fletes += flete_item
        total_gasoil += gasoil
        comision_total += comision_item
        total_cant_viajes += cant

        detalles_viajes.append({
            "viaje": v,
            "cant": cant,
            "flete_item": round(flete_item, 2),
            "gasoil_item": round(gasoil, 2),
            "base_item": round(base_item, 2),
            "comision_item": round(comision_item, 2)
        })

    base_total = max(0.0, total_fletes - total_gasoil)

    return {
        "total_fletes": round(total_fletes, 2),
        "total_gasoil": round(total_gasoil, 2),
        "base_calculo": round(base_total, 2),
        "monto_comision": round(comision_total, 2),
        "cantidad_registros": len(viajes_lista),
        "cantidad_viajes": total_cant_viajes,
        "detalles": detalles_viajes
    }

def registrar_pago_nomina(id_chofer: int, fecha_emision: str, periodo_desde: str, periodo_hasta: str, viajes_ids: list[int]):
    """
    Registra una nueva nómina para el chofer y vincula los viajes seleccionados 
    marcándolos como PAGADOS en nómina.
    """
    if not id_chofer:
        return False, "Debe seleccionar un chofer válido.", None
    if not viajes_ids or len(viajes_ids) == 0:
        return False, "No hay fletes seleccionados/pendientes para liquidar en este período.", None

    db = SessionLocal()
    try:
        # Obtener los viajes directamente de la BD para recálculo seguro
        viajes = db.query(Viaje).filter(Viaje.id_viaje.in_(viajes_ids)).all()
        resumen = calcular_resumen_comision(viajes)

        nueva_nomina = Nomina(
            id_chofer=id_chofer,
            fecha_emision=parse_date(fecha_emision) or datetime.date.today(),
            periodo_desde=parse_date(periodo_desde),
            periodo_hasta=parse_date(periodo_hasta),
            total_ingresos_fletes=Decimal(str(resumen["total_fletes"])),
            total_costo_gasoil=Decimal(str(resumen["total_gasoil"])),
            porcentaje_comision=Decimal("0.20"),
            monto_neto_comision=Decimal(str(resumen["monto_comision"])),
            cantidad_viajes=resumen["cantidad_viajes"]
        )

        db.add(nueva_nomina)
        db.flush() # Generar id_nomina

        # Vincular viajes a esta nómina
        for v in viajes:
            v.id_nomina_pago = nueva_nomina.id_nomina

        db.commit()
        db.refresh(nueva_nomina)

        return True, f"Nómina N° NOM-{nueva_nomina.id_nomina:05d} registrada exitosamente.", nueva_nomina
    except Exception as e:
        db.rollback()
        return False, f"Error al registrar nómina: {str(e)}", None
    finally:
        db.close()

def obtener_nominas_filtradas(id_chofer: int | None = None, fecha_desde: str | None = None, fecha_hasta: str | None = None):
    """
    Consulta el historial de nóminas registradas permitiendo filtrar por Chofer y/o Rango de Fechas.
    """
    db = SessionLocal()
    try:
        query = db.query(Nomina).options(joinedload(Nomina.chofer))

        if id_chofer and str(id_chofer) not in ("0", "all", "None", ""):
            query = query.filter(Nomina.id_chofer == int(id_chofer))

        d_desde = parse_date(fecha_desde)
        if d_desde:
            query = query.filter(Nomina.periodo_desde >= d_desde)

        d_hasta = parse_date(fecha_hasta)
        if d_hasta:
            query = query.filter(Nomina.periodo_hasta <= d_hasta)

        return query.order_by(Nomina.fecha_emision.desc(), Nomina.id_nomina.desc()).all()
    except Exception as e:
        print(f"[-] Error al consultar nóminas: {e}")
        return []
    finally:
        db.close()

def obtener_detalles_nomina(id_nomina: int):
    """
    Obtiene el objeto Nómina, el Chofer y la lista de Viajes asociados para la reimpresión de PDF.
    """
    db = SessionLocal()
    try:
        nomina = db.query(Nomina).options(joinedload(Nomina.chofer)).filter(Nomina.id_nomina == id_nomina).first()
        if not nomina:
            return None, None, []

        viajes = db.query(Viaje).options(
            joinedload(Viaje.cliente),
            joinedload(Viaje.ruta)
        ).filter(Viaje.id_nomina_pago == id_nomina).all()

        return nomina, nomina.chofer, viajes
    except Exception as e:
        print(f"[-] Error al obtener detalles de nómina: {e}")
        return None, None, []
    finally:
        db.close()

def eliminar_nomina_y_liberar_viajes(id_nomina: int):
    """
    Elimina un registro de nómina y libera los viajes asociados (id_nomina_pago = NULL).
    """
    db = SessionLocal()
    try:
        nomina = db.query(Nomina).filter(Nomina.id_nomina == id_nomina).first()
        if not nomina:
            return False, "Registro de nómina no encontrado."

        # Liberar los viajes vinculados
        db.query(Viaje).filter(Viaje.id_nomina_pago == id_nomina).update({"id_nomina_pago": None})

        # Eliminar registro de nómina
        db.delete(nomina)
        db.commit()

        return True, "Nómina eliminada y viajes liberados correctamente."
    except Exception as e:
        db.rollback()
        return False, f"Error al eliminar nómina: {str(e)}"
    finally:
        db.close()
