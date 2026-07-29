import os
import sys
sys_src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if sys_src_path not in sys.path:
    sys.path.insert(0, sys_src_path)

import tempfile
import subprocess
from datetime import datetime
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#718096"))
        
        page_w, page_h = self._pagesize
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(36, 30, page_w - 36, 30)
        
        page_text = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(page_w - 36, 16, page_text)
        self.drawString(36, 16, "SISTEMA DE GESTIÓN DE TRANSPORTE MONTENEGRO (SGTM) - REPORTE OFICIAL")
        self.restoreState()

def _format_date_val(val, default="N/A"):
    if not val:
        return default
    if isinstance(val, str):
        try:
            d = datetime.strptime(val.strip(), "%Y-%m-%d")
            return d.strftime("%d/%m/%Y")
        except Exception:
            return val
    try:
        return val.strftime("%d/%m/%Y")
    except Exception:
        return str(val)

def _obtener_dir_predeterminado_sgtm(subcarpeta="Comprobantes_PDF"):
    user_docs = os.path.expanduser("~/Documents")
    if not os.path.exists(user_docs):
        user_docs = os.path.expanduser("~")
    target_dir = os.path.join(user_docs, "SGTM", subcarpeta)
    os.makedirs(target_dir, exist_ok=True)
    return target_dir

def seleccionar_carpeta_destino(titulo="Seleccionar carpeta para guardar el reporte"):
    """
    Abre un diálogo nativo del explorador de archivos del SO para seleccionar una carpeta.
    Retorna la ruta absoluta de la carpeta seleccionada o None si el usuario canceló.
    """
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        carpeta = filedialog.askdirectory(title=titulo, parent=root)
        root.destroy()
        if carpeta:
            return os.path.abspath(carpeta)
        return None
    except Exception as ex:
        print(f"[-] Error al seleccionar carpeta: {ex}")
        return None

def generar_pdf_recibo_nomina(nomina, chofer, viajes, output_path=None):
    """
    Genera un archivo PDF profesional del recibo de nómina para un chofer.
    Retorna la ruta absoluta del archivo PDF generado.
    """
    if not output_path:
        target_dir = _obtener_dir_predeterminado_sgtm("Comprobantes_PDF")
        filename = f"Recibo_Nomina_NOM-{nomina.id_nomina:05d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.abspath(os.path.join(target_dir, filename))

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Definir estilos personalizados
    style_title = ParagraphStyle(
        'HeaderTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1A365D")
    )

    style_subtitle = ParagraphStyle(
        'HeaderSub',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#2B6CB0")
    )

    style_meta_label = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#2D3748")
    )

    style_meta_val = ParagraphStyle(
        'MetaVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#1A202C")
    )

    style_table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.white
    )

    style_table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#2D3748")
    )

    style_table_cell_center = ParagraphStyle(
        'TableCellCenter',
        parent=style_table_cell,
        alignment=TA_CENTER
    )

    style_table_cell_right = ParagraphStyle(
        'TableCellRight',
        parent=style_table_cell,
        alignment=TA_RIGHT
    )

    style_total_label = ParagraphStyle(
        'TotalLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12,
        alignment=TA_RIGHT,
        textColor=colors.HexColor("#1A365D")
    )

    style_total_val = ParagraphStyle(
        'TotalVal',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=13,
        alignment=TA_RIGHT,
        textColor=colors.HexColor("#2B6CB0")
    )

    elements = []

    # 1. ENCABEZADO Y TÍTULO
    elements.append(Paragraph("SISTEMA DE GESTIÓN - TRANSPORTE MONTENEGRO", style_title))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph("COMPROBANTE DE LIQUIDACIÓN DE NÓMINA Y COMISIONES", style_subtitle))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1A365D"), spaceAfter=15))

    # 2. METADATA / DATOS DEL CHOFER Y NÓMINA
    f_emision = _format_date_val(getattr(nomina, 'fecha_emision', None))
    f_desde = _format_date_val(getattr(nomina, 'periodo_desde', None))
    f_hasta = _format_date_val(getattr(nomina, 'periodo_hasta', None))

    nombre_chofer = chofer.nombre_completo if chofer else "N/A"
    cedula_chofer = getattr(chofer, 'cedula_identidad', 'N/A') if chofer else "N/A"

    meta_data = [
        [
            Paragraph("N° COMPROBANTE:", style_meta_label),
            Paragraph(f"NOM-{nomina.id_nomina:05d}", style_meta_val),
            Paragraph("FECHA DE EMISIÓN:", style_meta_label),
            Paragraph(f_emision, style_meta_val)
        ],
        [
            Paragraph("CHOFER:", style_meta_label),
            Paragraph(f"{nombre_chofer}", style_meta_val),
            Paragraph("CÉDULA / ID:", style_meta_label),
            Paragraph(f"{cedula_chofer}", style_meta_val)
        ],
        [
            Paragraph("PERÍODO DESDE:", style_meta_label),
            Paragraph(f_desde, style_meta_val),
            Paragraph("PERÍODO HASTA:", style_meta_label),
            Paragraph(f_hasta, style_meta_val)
        ]
    ]

    t_meta = Table(meta_data, colWidths=[110, 160, 110, 160])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#EDF2F7")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(t_meta)
    elements.append(Spacer(1, 15))

    # 3. TABLA DE VIAJES / FLETES INCLUIDOS
    elements.append(Paragraph("DETALLE DE VIAJES Y FLETES LIQUIDADOS", ParagraphStyle(
        'SectionHeader', fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor("#1A365D")
    )))
    elements.append(Spacer(1, 6))

    table_data = [
        [
            Paragraph("N° Viaje", style_table_header),
            Paragraph("Fecha", style_table_header),
            Paragraph("Cliente", style_table_header),
            Paragraph("Ruta / Trayecto", style_table_header),
            Paragraph("Cant.", style_table_header),
            Paragraph("Monto Flete ($)", style_table_header),
            Paragraph("Costo Gasoil ($)", style_table_header),
        ]
    ]

    sum_fletes = 0.0
    sum_gasoil = 0.0

    if viajes:
        for v in viajes:
            fecha_v = _format_date_val(getattr(v, 'fecha_operacion', None))
            cliente_v = v.cliente.nombre_cliente if getattr(v, 'cliente', None) else "N/A"
            ruta_v = v.ruta.descripcion_trayecto if getattr(v, 'ruta', None) else "N/A"
            
            cant_f = getattr(v, 'cantidad_fletes', 1) or 1
            costo_u = float(getattr(v, 'costo_unitario_aplicado', 0) or 0)
            mora = float(getattr(v, 'monto_mora_espera', 0) or 0)
            flete_total = (cant_f * costo_u) + mora
            
            gasoil_v = float(getattr(v, 'costo_total_gasoil', 0) or 0)

            sum_fletes += flete_total
            sum_gasoil += gasoil_v

            table_data.append([
                Paragraph(f"#{v.id_viaje}", style_table_cell_center),
                Paragraph(fecha_v, style_table_cell_center),
                Paragraph(cliente_v, style_table_cell),
                Paragraph(ruta_v, style_table_cell),
                Paragraph(str(cant_f), style_table_cell_center),
                Paragraph(f"${flete_total:,.2f}", style_table_cell_right),
                Paragraph(f"${gasoil_v:,.2f}", style_table_cell_right),
            ])
    else:
        table_data.append([
            Paragraph("-", style_table_cell_center),
            Paragraph("-", style_table_cell_center),
            Paragraph("Sin fletes desglosados", style_table_cell),
            Paragraph("-", style_table_cell),
            Paragraph("1", style_table_cell_center),
            Paragraph(f"${float(nomina.total_ingresos_fletes or 0):,.2f}", style_table_cell_right),
            Paragraph(f"${float(nomina.total_costo_gasoil or 0):,.2f}", style_table_cell_right),
        ])
        sum_fletes = float(nomina.total_ingresos_fletes or 0)
        sum_gasoil = float(nomina.total_costo_gasoil or 0)

    t_viajes = Table(table_data, colWidths=[45, 55, 110, 150, 40, 70, 70])
    t_viajes.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2B6CB0")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
    ]))
    elements.append(t_viajes)
    elements.append(Spacer(1, 15))

    # 4. DESGLOSE DE CÁLCULO DE COMISIÓN (20%)
    base_comision = max(0.0, sum_fletes - sum_gasoil)
    monto_comision = float(nomina.monto_neto_comision or (base_comision * 0.20))

    resumen_data = [
        [Paragraph("TOTAL INGRESOS POR FLETES:", style_total_label), Paragraph(f"${sum_fletes:,.2f}", style_total_val)],
        [Paragraph("(-) TOTAL COSTO GASOIL:", style_total_label), Paragraph(f"${sum_gasoil:,.2f}", style_total_val)],
        [Paragraph("(=) BASE DE CÁLCULO DE COMISIÓN:", style_total_label), Paragraph(f"${base_comision:,.2f}", style_total_val)],
        [Paragraph("PORCENTAJE DE COMISIÓN:", style_total_label), Paragraph("20.00 %", style_total_val)],
        [
            Paragraph("TOTAL NETO A PAGAR AL CHOFER:", ParagraphStyle('BigTotalLbl', parent=style_total_label, fontSize=11, textColor=colors.HexColor("#2B6CB0"))),
            Paragraph(f"${monto_comision:,.2f}", ParagraphStyle('BigTotalVal', parent=style_total_val, fontSize=13, textColor=colors.HexColor("#2B6CB0")))
        ],
    ]

    t_resumen = Table(resumen_data, colWidths=[380, 160])
    t_resumen.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('LINEABOVE', (0, 2), (-1, 2), 1, colors.HexColor("#CBD5E0")),
        ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor("#EBF8FF")),
        ('BOX', (0, 4), (-1, 4), 1, colors.HexColor("#3182CE")),
        ('PADDING', (0, 4), (-1, 4), 6),
    ]))

    elements.append(KeepTogether([t_resumen]))
    elements.append(Spacer(1, 45))

    # 5. SECCIÓN DE FIRMAS
    firmas_data = [
        [
            Paragraph("___________________________________<br/><b>CHOFER (RECIBÍ CONFORME)</b>", ParagraphStyle('Firma1', parent=styles['Normal'], alignment=TA_CENTER, fontSize=9)),
            Paragraph("___________________________________<br/><b>ADMINISTRACIÓN / REVISADO POR</b>", ParagraphStyle('Firma2', parent=styles['Normal'], alignment=TA_CENTER, fontSize=9))
        ]
    ]

    t_firmas = Table(firmas_data, colWidths=[270, 270])
    t_firmas.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    elements.append(KeepTogether([t_firmas]))

    doc.build(elements)
    return output_path

def generar_pdf_reporte_fletes(viajes, filtro_chofer_nombre=None, fecha_desde=None, fecha_hasta=None, output_dir=None):
    """
    Genera un reporte PDF detallado de Fletes / Viajes filtrados por fecha y chofer.
    Guarda el archivo en `output_dir` (o 'comprobantes_pdf' por defecto).
    Retorna la ruta absoluta del PDF generado.
    """
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        filename = f"Reporte_Fletes_Viajes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.abspath(os.path.join(output_dir, filename))
    else:
        target_dir = _obtener_dir_predeterminado_sgtm("Reportes")
        filename = f"Reporte_Fletes_Viajes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.abspath(os.path.join(target_dir, filename))

    doc = SimpleDocTemplate(
        output_path,
        pagesize=landscape(letter),
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()

    style_title = ParagraphStyle(
        'HeaderTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1A365D")
    )

    style_subtitle = ParagraphStyle(
        'HeaderSub',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#2B6CB0")
    )

    style_meta_label = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#2D3748")
    )

    style_meta_val = ParagraphStyle(
        'MetaVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#1A202C")
    )

    style_table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        alignment=TA_CENTER,
        textColor=colors.white
    )

    style_table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#2D3748")
    )

    style_table_cell_center = ParagraphStyle(
        'TableCellCenter',
        parent=style_table_cell,
        alignment=TA_CENTER
    )

    style_table_cell_right = ParagraphStyle(
        'TableCellRight',
        parent=style_table_cell,
        alignment=TA_RIGHT
    )

    elements = []

    # 1. ENCABEZADO
    elements.append(Paragraph("SISTEMA DE GESTIÓN - TRANSPORTE MONTENEGRO", style_title))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph("REPORTE GENERAL DE FLETES Y VIAJES REGISTRADOS", style_subtitle))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1A365D"), spaceAfter=12))

    # 2. METADATA DE FILTROS Y EMISIÓN
    str_desde = _format_date_val(fecha_desde, "Inicio")
    str_hasta = _format_date_val(fecha_hasta, "Actualidad")
    periodo_txt = f"{str_desde} al {str_hasta}" if (fecha_desde or fecha_hasta) else "Todos los Registros Históricos"
    chofer_txt = filtro_chofer_nombre if (filtro_chofer_nombre and filtro_chofer_nombre != "Todos los Choferes") else "Todos los Choferes"
    emision_txt = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    meta_data = [
        [
            Paragraph("PERÍODO FILTRADO:", style_meta_label),
            Paragraph(periodo_txt, style_meta_val),
            Paragraph("CHOFER:", style_meta_label),
            Paragraph(chofer_txt, style_meta_val),
            Paragraph("FECHA GENERACIÓN:", style_meta_label),
            Paragraph(emision_txt, style_meta_val)
        ]
    ]

    t_meta = Table(meta_data, colWidths=[100, 160, 60, 180, 100, 120])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(t_meta)
    elements.append(Spacer(1, 12))

    # 3. CÁLCULO DE RESUMEN Y KPI
    sum_viajes_count = len(viajes) if viajes else 0
    sum_cant_fletes = 0
    sum_fletes_monto = 0.0
    sum_gasoil_monto = 0.0
    sum_mora_monto = 0.0
    sum_pagado_monto = 0.0
    sum_pendiente_monto = 0.0

    if viajes:
        for v in viajes:
            cant = int(getattr(v, 'cantidad_fletes', 1) or 1)
            costo_u = float(getattr(v, 'costo_unitario_aplicado', 0) or 0)
            mora = float(getattr(v, 'monto_mora_espera', 0) or 0)
            gasoil = float(getattr(v, 'costo_total_gasoil', 0) or 0)

            total_flete_item = (cant * costo_u) + mora
            sum_cant_fletes += cant
            sum_fletes_monto += total_flete_item
            sum_gasoil_monto += gasoil
            sum_mora_monto += mora

            est = str(getattr(v, 'estatus_pago_cliente', 'Pendiente'))
            if est.lower() == 'pagado':
                sum_pagado_monto += total_flete_item
            else:
                sum_pendiente_monto += total_flete_item

    kpi_data = [
        [
            Paragraph("REGISTROS:", style_meta_label),
            Paragraph(f"<b>{sum_viajes_count}</b> viajes ({sum_cant_fletes} fletes)", style_meta_val),
            Paragraph("TOTAL FLETES:", style_meta_label),
            Paragraph(f"<b>${sum_fletes_monto:,.2f}</b>", ParagraphStyle('GreenVal', parent=style_meta_val, textColor=colors.HexColor("#2B6CB0"))),
            Paragraph("TOTAL GASOIL:", style_meta_label),
            Paragraph(f"<b>${sum_gasoil_monto:,.2f}</b>", ParagraphStyle('OrangeVal', parent=style_meta_val, textColor=colors.HexColor("#DD6B20"))),
        ],
        [
            Paragraph("TOTAL MORA:", style_meta_label),
            Paragraph(f"${sum_mora_monto:,.2f}", style_meta_val),
            Paragraph("COBRADO (CLIENTE):", style_meta_label),
            Paragraph(f"<b>${sum_pagado_monto:,.2f}</b>", ParagraphStyle('CobradoVal', parent=style_meta_val, textColor=colors.HexColor("#2F855A"))),
            Paragraph("PENDIENTE COBRO:", style_meta_label),
            Paragraph(f"<b>${sum_pendiente_monto:,.2f}</b>", ParagraphStyle('PendVal', parent=style_meta_val, textColor=colors.HexColor("#C53030"))),
        ]
    ]

    t_kpi = Table(kpi_data, colWidths=[80, 160, 100, 140, 100, 140])
    t_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#EBF8FF")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#3182CE")),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(t_kpi)
    elements.append(Spacer(1, 14))

    # 4. TABLA DETALLADA DE REGISTROS
    table_data = [
        [
            Paragraph("N° Viaje", style_table_header),
            Paragraph("Fecha", style_table_header),
            Paragraph("Chofer", style_table_header),
            Paragraph("Cliente", style_table_header),
            Paragraph("Ruta / Trayecto", style_table_header),
            Paragraph("Cant.", style_table_header),
            Paragraph("Gasoil ($)", style_table_header),
            Paragraph("Mora ($)", style_table_header),
            Paragraph("Total ($)", style_table_header),
            Paragraph("Estatus Cliente", style_table_header),
            Paragraph("Estado Nómina", style_table_header),
        ]
    ]

    if viajes:
        for v in viajes:
            id_v = f"#{v.id_viaje}"
            f_op = _format_date_val(getattr(v, 'fecha_operacion', None))
            ch_name = v.chofer.nombre_completo if getattr(v, 'chofer', None) else "N/A"
            cl_name = v.cliente.nombre_cliente if getattr(v, 'cliente', None) else "N/A"
            rt_name = v.ruta.descripcion_trayecto if getattr(v, 'ruta', None) else "N/A"

            cant = int(getattr(v, 'cantidad_fletes', 1) or 1)
            costo_u = float(getattr(v, 'costo_unitario_aplicado', 0) or 0)
            mora = float(getattr(v, 'monto_mora_espera', 0) or 0)
            gasoil = float(getattr(v, 'costo_total_gasoil', 0) or 0)
            total_flete = (cant * costo_u) + mora

            estatus_cli = str(getattr(v, 'estatus_pago_cliente', 'Pendiente'))
            id_nom = getattr(v, 'id_nomina_pago', None)
            estatus_nom = f"NOM-{int(id_nom):05d}" if id_nom else "Pendiente"

            table_data.append([
                Paragraph(id_v, style_table_cell_center),
                Paragraph(f_op, style_table_cell_center),
                Paragraph(ch_name, style_table_cell),
                Paragraph(cl_name, style_table_cell),
                Paragraph(rt_name, style_table_cell),
                Paragraph(str(cant), style_table_cell_center),
                Paragraph(f"${gasoil:,.2f}", style_table_cell_right),
                Paragraph(f"${mora:,.2f}", style_table_cell_right),
                Paragraph(f"${total_flete:,.2f}", style_table_cell_right),
                Paragraph(estatus_cli, style_table_cell_center),
                Paragraph(estatus_nom, style_table_cell_center),
            ])
    else:
        table_data.append([
            Paragraph("-", style_table_cell_center),
            Paragraph("-", style_table_cell_center),
            Paragraph("No se encontraron registros de fletes para el filtro seleccionado.", style_table_cell),
            Paragraph("-", style_table_cell),
            Paragraph("-", style_table_cell),
            Paragraph("-", style_table_cell_center),
            Paragraph("$0.00", style_table_cell_right),
            Paragraph("$0.00", style_table_cell_right),
            Paragraph("$0.00", style_table_cell_right),
            Paragraph("-", style_table_cell_center),
            Paragraph("-", style_table_cell_center),
        ])

    t_viajes = Table(table_data, colWidths=[40, 55, 100, 95, 110, 35, 55, 50, 65, 55, 60])
    t_viajes.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1A365D")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
    ]))

    elements.append(t_viajes)
    doc.build(elements, canvasmaker=NumberedCanvas)
    return output_path

def generar_pdf_reporte_nomina(nominas, filtro_chofer_nombre=None, fecha_desde=None, fecha_hasta=None, output_dir=None):
    """
    Genera un reporte PDF detallado del Historial de Nóminas y Comisiones filtrado por fecha y chofer.
    Guarda el archivo en `output_dir` (o 'comprobantes_pdf' por defecto).
    Retorna la ruta absoluta del PDF generado.
    """
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        filename = f"Reporte_Nomina_Comisiones_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.abspath(os.path.join(output_dir, filename))
    else:
        target_dir = _obtener_dir_predeterminado_sgtm("Reportes")
        filename = f"Reporte_Nomina_Comisiones_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.abspath(os.path.join(target_dir, filename))

    doc = SimpleDocTemplate(
        output_path,
        pagesize=landscape(letter),
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()

    style_title = ParagraphStyle(
        'HeaderTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1565C0")
    )

    style_subtitle = ParagraphStyle(
        'HeaderSub',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#0D47A1")
    )

    style_meta_label = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#2D3748")
    )

    style_meta_val = ParagraphStyle(
        'MetaVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#1A202C")
    )

    style_table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.white
    )

    style_table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#2D3748")
    )

    style_table_cell_center = ParagraphStyle(
        'TableCellCenter',
        parent=style_table_cell,
        alignment=TA_CENTER
    )

    style_table_cell_right = ParagraphStyle(
        'TableCellRight',
        parent=style_table_cell,
        alignment=TA_RIGHT
    )

    elements = []

    # 1. ENCABEZADO
    elements.append(Paragraph("SISTEMA DE GESTIÓN - TRANSPORTE MONTENEGRO", style_title))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph("REPORTE GENERAL DE NÓMINA Y COMISIONES DE CHOFERES", style_subtitle))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1565C0"), spaceAfter=12))

    # 2. METADATA DE FILTROS Y EMISIÓN
    str_desde = _format_date_val(fecha_desde, "Inicio")
    str_hasta = _format_date_val(fecha_hasta, "Actualidad")
    periodo_txt = f"{str_desde} al {str_hasta}" if (fecha_desde or fecha_hasta) else "Todos los Registros Históricos"
    chofer_txt = filtro_chofer_nombre if (filtro_chofer_nombre and filtro_chofer_nombre != "Todos los Choferes") else "Todos los Choferes"
    emision_txt = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    meta_data = [
        [
            Paragraph("PERÍODO FILTRADO:", style_meta_label),
            Paragraph(periodo_txt, style_meta_val),
            Paragraph("CHOFER:", style_meta_label),
            Paragraph(chofer_txt, style_meta_val),
            Paragraph("FECHA GENERACIÓN:", style_meta_label),
            Paragraph(emision_txt, style_meta_val)
        ]
    ]

    t_meta = Table(meta_data, colWidths=[100, 160, 60, 180, 100, 120])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(t_meta)
    elements.append(Spacer(1, 12))

    # 3. CÁLCULO DE RESUMEN Y KPI DE NÓMINAS
    sum_recibos_count = len(nominas) if nominas else 0
    sum_fletes = 0.0
    sum_gasoil = 0.0
    sum_base = 0.0
    sum_neto_comision = 0.0

    if nominas:
        for n in nominas:
            f = float(getattr(n, 'total_ingresos_fletes', 0) or 0)
            g = float(getattr(n, 'total_costo_gasoil', 0) or 0)
            com = float(getattr(n, 'monto_neto_comision', 0) or 0)
            base = max(0.0, f - g)

            sum_fletes += f
            sum_gasoil += g
            sum_base += base
            sum_neto_comision += com

    kpi_data = [
        [
            Paragraph("N° RECIBOS:", style_meta_label),
            Paragraph(f"<b>{sum_recibos_count}</b> recibos", style_meta_val),
            Paragraph("INGRESOS FLETES:", style_meta_label),
            Paragraph(f"<b>${sum_fletes:,.2f}</b>", ParagraphStyle('FleteVal', parent=style_meta_val, textColor=colors.HexColor("#2B6CB0"))),
            Paragraph("DEDUCCIÓN GASOIL:", style_meta_label),
            Paragraph(f"<b>${sum_gasoil:,.2f}</b>", ParagraphStyle('GasoilVal', parent=style_meta_val, textColor=colors.HexColor("#DD6B20"))),
        ],
        [
            Paragraph("BASE CÁLCULO:", style_meta_label),
            Paragraph(f"${sum_base:,.2f}", style_meta_val),
            Paragraph("NETO PAGADO CHOFERES (20%):", style_meta_label),
            Paragraph(f"<b>${sum_neto_comision:,.2f}</b>", ParagraphStyle('ComVal', parent=style_meta_val, textColor=colors.HexColor("#2F855A"), fontSize=10)),
            Paragraph("-", style_meta_label),
            Paragraph("-", style_meta_val),
        ]
    ]

    t_kpi = Table(kpi_data, colWidths=[90, 150, 110, 130, 110, 130])
    t_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#EBF8FF")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#3182CE")),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(t_kpi)
    elements.append(Spacer(1, 14))

    # 4. TABLA DETALLADA DE REGISTROS DE NÓMINA
    table_data = [
        [
            Paragraph("N° Recibo", style_table_header),
            Paragraph("Fecha Emisión", style_table_header),
            Paragraph("Chofer", style_table_header),
            Paragraph("Cédula / ID", style_table_header),
            Paragraph("Período Liquidadas", style_table_header),
            Paragraph("Total Fletes ($)", style_table_header),
            Paragraph("Total Gasoil ($)", style_table_header),
            Paragraph("Pago Chofer 20% ($)", style_table_header),
        ]
    ]

    if nominas:
        for n in nominas:
            nid = int(getattr(n, 'id_nomina'))
            recibo_str = f"NOM-{nid:05d}"
            f_emision = _format_date_val(getattr(n, 'fecha_emision', None))
            
            ch_obj = getattr(n, 'chofer', None)
            chofer_name = ch_obj.nombre_completo if ch_obj else "N/A"
            cedula_str = getattr(ch_obj, 'cedula_identidad', 'N/A') if ch_obj else "N/A"

            p_desde = _format_date_val(getattr(n, 'periodo_desde', None))
            p_hasta = _format_date_val(getattr(n, 'periodo_hasta', None))
            periodo_str = f"{p_desde} al {p_hasta}"

            tot_f = float(getattr(n, 'total_ingresos_fletes', 0) or 0)
            tot_g = float(getattr(n, 'total_costo_gasoil', 0) or 0)
            pago_c = float(getattr(n, 'monto_neto_comision', 0) or 0)

            table_data.append([
                Paragraph(recibo_str, style_table_cell_center),
                Paragraph(f_emision, style_table_cell_center),
                Paragraph(chofer_name, style_table_cell),
                Paragraph(str(cedula_str), style_table_cell_center),
                Paragraph(periodo_str, style_table_cell_center),
                Paragraph(f"${tot_f:,.2f}", style_table_cell_right),
                Paragraph(f"${tot_g:,.2f}", style_table_cell_right),
                Paragraph(f"${pago_c:,.2f}", style_table_cell_right),
            ])
    else:
        table_data.append([
            Paragraph("-", style_table_cell_center),
            Paragraph("-", style_table_cell_center),
            Paragraph("No se encontraron registros de nómina para el filtro seleccionado.", style_table_cell),
            Paragraph("-", style_table_cell_center),
            Paragraph("-", style_table_cell_center),
            Paragraph("$0.00", style_table_cell_right),
            Paragraph("$0.00", style_table_cell_right),
            Paragraph("$0.00", style_table_cell_right),
        ])

    t_nominas = Table(table_data, colWidths=[70, 75, 160, 85, 110, 75, 75, 70])
    t_nominas.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1565C0")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
    ]))

    elements.append(t_nominas)
    doc.build(elements, canvasmaker=NumberedCanvas)
    return output_path

def abrir_pdf(output_path):
    """Abre automáticamente el archivo PDF en el visor predeterminado del SO."""
    try:
        if os.name == 'nt':  # Windows
            os.startfile(output_path)
        elif os.name == 'posix':
            subprocess.run(['open', output_path] if os.uname().sysname == 'Darwin' else ['xdg-open', output_path])
    except Exception as e:
        print(f"No se pudo abrir el PDF automáticamente: {e}")
