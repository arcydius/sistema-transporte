import os
import sys
sys_src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if sys_src_path not in sys.path:
    sys.path.insert(0, sys_src_path)

import datetime
from decimal import Decimal
from sqlalchemy.orm import joinedload
from database.config import SessionLocal
from models.maestros import Chofer, Camion, Remolque
from models.operaciones import Viaje, Nomina

MESES_ESPANOL = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

def obtener_metricas_dashboard():
    """
    Calcula métricas financieras y operativas en tiempo real para el mes actual,
    conteo de choferes, camiones, remolques y alertas de vencimiento urgentes.
    """
    db = SessionLocal()
    try:
        hoy = datetime.date.today()
        primer_dia_mes = datetime.date(hoy.year, hoy.month, 1)
        if hoy.month == 12:
            ultimo_dia_mes = datetime.date(hoy.year, 12, 31)
        else:
            ultimo_dia_mes = datetime.date(hoy.year, hoy.month + 1, 1) - datetime.timedelta(days=1)

        nombre_mes = f"{MESES_ESPANOL.get(hoy.month, 'Mes')} {hoy.year}"

        # 1. Conteo de Flota y Personal
        tot_choferes = db.query(Chofer).count()
        tot_camiones = db.query(Camion).count()
        tot_remolques = db.query(Remolque).count()

        # 2. Viajes y Utilidades del Mes Actual (Reinicia automáticamente al cambiar de mes)
        viajes_mes = db.query(Viaje).filter(
            Viaje.fecha_operacion >= primer_dia_mes,
            Viaje.fecha_operacion <= ultimo_dia_mes
        ).all()

        cant_viajes_mes = 0
        ingresos_fletes_mes = 0.0
        gasoil_mes = 0.0
        comisiones_mes = 0.0

        for v in viajes_mes:
            cant = int(getattr(v, 'cantidad_fletes', 1) or 1)
            costo_u = float(getattr(v, 'costo_unitario_aplicado', 0.0) or 0.0)
            mora = float(getattr(v, 'monto_mora_espera', 0.0) or 0.0)
            gasoil = float(getattr(v, 'costo_total_gasoil', 0.0) or 0.0)

            flete_item = (cant * costo_u) + mora
            base_item = max(0.0, flete_item - gasoil)
            comision_item = base_item * 0.20

            cant_viajes_mes += cant
            ingresos_fletes_mes += flete_item
            gasoil_mes += gasoil
            comisiones_mes += comision_item

        utilidad_neta_mes = ingresos_fletes_mes - gasoil_mes - comisiones_mes

        # 3. Alertas de Vencimiento (Camiones y Remolques)
        alertas = []
        cant_alertas_urgentes = 0
        cant_alertas_proximas = 0

        camiones = db.query(Camion).all()
        for c in camiones:
            placa = getattr(c, 'placa', 'S/P')
            alias = getattr(c, 'alias_identificador', '')
            label_u = f"Camión {placa}" + (f" ({alias})" if alias else "")

            # RCV
            v_rcv = getattr(c, 'vencimiento_rcv', None)
            if v_rcv:
                dias = (v_rcv - hoy).days
                if dias < 0:
                    cant_alertas_urgentes += 1
                    alertas.append({
                        "unidad": label_u,
                        "tipo": "Seguro RCV",
                        "fecha": v_rcv.strftime("%d/%m/%Y"),
                        "estado": "VENCIDO",
                        "nivel": "URGENTE",
                        "dias": abs(dias),
                        "obs": f"Venció hace {abs(dias)} día(s)"
                    })
                elif dias <= 15:
                    cant_alertas_proximas += 1
                    alertas.append({
                        "unidad": label_u,
                        "tipo": "Seguro RCV",
                        "fecha": v_rcv.strftime("%d/%m/%Y"),
                        "estado": "POR VENCER",
                        "nivel": "ADVERTENCIA",
                        "dias": dias,
                        "obs": f"Vence en {dias} día(s)"
                    })

            # Trimestre
            v_trim = getattr(c, 'vencimiento_trimestre', None)
            if v_trim:
                dias = (v_trim - hoy).days
                if dias < 0:
                    cant_alertas_urgentes += 1
                    alertas.append({
                        "unidad": label_u,
                        "tipo": "Impuesto Trimestre",
                        "fecha": v_trim.strftime("%d/%m/%Y"),
                        "estado": "VENCIDO",
                        "nivel": "URGENTE",
                        "dias": abs(dias),
                        "obs": f"Venció hace {abs(dias)} día(s)"
                    })
                elif dias <= 15:
                    cant_alertas_proximas += 1
                    alertas.append({
                        "unidad": label_u,
                        "tipo": "Impuesto Trimestre",
                        "fecha": v_trim.strftime("%d/%m/%Y"),
                        "estado": "POR VENCER",
                        "nivel": "ADVERTENCIA",
                        "dias": dias,
                        "obs": f"Vence en {dias} día(s)"
                    })

        remolques = db.query(Remolque).all()
        for r in remolques:
            placa = getattr(r, 'placa', 'S/P')
            alias = getattr(r, 'alias_identificador', '')
            label_u = f"Remolque {placa}" + (f" ({alias})" if alias else "")

            # RCV
            v_rcv = getattr(r, 'vencimiento_rcv', None)
            if v_rcv:
                dias = (v_rcv - hoy).days
                if dias < 0:
                    cant_alertas_urgentes += 1
                    alertas.append({
                        "unidad": label_u,
                        "tipo": "Seguro RCV",
                        "fecha": v_rcv.strftime("%d/%m/%Y"),
                        "estado": "VENCIDO",
                        "nivel": "URGENTE",
                        "dias": abs(dias),
                        "obs": f"Venció hace {abs(dias)} día(s)"
                    })
                elif dias <= 15:
                    cant_alertas_proximas += 1
                    alertas.append({
                        "unidad": label_u,
                        "tipo": "Seguro RCV",
                        "fecha": v_rcv.strftime("%d/%m/%Y"),
                        "estado": "POR VENCER",
                        "nivel": "ADVERTENCIA",
                        "dias": dias,
                        "obs": f"Vence en {dias} día(s)"
                    })

            # Trimestre
            v_trim = getattr(r, 'vencimiento_trimestre', None)
            if v_trim:
                dias = (v_trim - hoy).days
                if dias < 0:
                    cant_alertas_urgentes += 1
                    alertas.append({
                        "unidad": label_u,
                        "tipo": "Impuesto Trimestre",
                        "fecha": v_trim.strftime("%d/%m/%Y"),
                        "estado": "VENCIDO",
                        "nivel": "URGENTE",
                        "dias": abs(dias),
                        "obs": f"Venció hace {abs(dias)} día(s)"
                    })
                elif dias <= 15:
                    cant_alertas_proximas += 1
                    alertas.append({
                        "unidad": label_u,
                        "tipo": "Impuesto Trimestre",
                        "fecha": v_trim.strftime("%d/%m/%Y"),
                        "estado": "POR VENCER",
                        "nivel": "ADVERTENCIA",
                        "dias": dias,
                        "obs": f"Vence en {dias} día(s)"
                    })

        # 4. Fletes Pendientes de Pago por Clientes
        fletes_pendientes_cliente = db.query(Viaje).filter(
            Viaje.estatus_pago_cliente == "Pendiente"
        ).count()

        return {
            "mes_nombre": nombre_mes,
            "cant_choferes": tot_choferes,
            "cant_camiones": tot_camiones,
            "cant_remolques": tot_remolques,
            "cant_viajes_mes": cant_viajes_mes,
            "ingresos_fletes_mes": ingresos_fletes_mes,
            "gasoil_mes": gasoil_mes,
            "comisiones_mes": comisiones_mes,
            "utilidad_neta_mes": utilidad_neta_mes,
            "cant_alertas_urgentes": cant_alertas_urgentes,
            "cant_alertas_proximas": cant_alertas_proximas,
            "fletes_pendientes_cliente": fletes_pendientes_cliente,
            "alertas": alertas
        }
    except Exception as e:
        print(f"Error calculando métricas del dashboard: {e}")
        return {
            "mes_nombre": "",
            "cant_choferes": 0, "cant_camiones": 0, "cant_remolques": 0,
            "cant_viajes_mes": 0, "ingresos_fletes_mes": 0.0, "gasoil_mes": 0.0,
            "comisiones_mes": 0.0, "utilidad_neta_mes": 0.0,
            "cant_alertas_urgentes": 0, "cant_alertas_proximas": 0,
            "fletes_pendientes_cliente": 0, "alertas": []
        }
    finally:
        db.close()
