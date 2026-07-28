import os
import sys
sys_src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if sys_src_path not in sys.path:
    sys.path.insert(0, sys_src_path)

import tempfile
import subprocess
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

def generar_pdf_recibo_nomina(nomina, chofer, viajes, output_path=None):
    """
    Genera un archivo PDF profesional del recibo de nómina para un chofer.
    Retorna la ruta absoluta del archivo PDF generado.
    """
    if not output_path:
        os.makedirs("comprobantes_pdf", exist_ok=True)
        filename = f"Recibo_Nomina_NOM-{nomina.id_nomina:05d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.abspath(os.path.join("comprobantes_pdf", filename))

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
    f_emision = nomina.fecha_emision.strftime("%d/%m/%Y") if getattr(nomina, 'fecha_emision', None) else "N/A"
    f_desde = nomina.periodo_desde.strftime("%d/%m/%Y") if getattr(nomina, 'periodo_desde', None) else "N/A"
    f_hasta = nomina.periodo_hasta.strftime("%d/%m/%Y") if getattr(nomina, 'periodo_hasta', None) else "N/A"

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
            fecha_v = v.fecha_operacion.strftime("%d/%m/%Y") if getattr(v, 'fecha_operacion', None) else "N/A"
            cliente_v = v.cliente.nombre_cliente if getattr(v, 'cliente', None) else "N/A"
            ruta_v = v.ruta.descripcion_trayecto if getattr(v, 'ruta', None) else "N/A"
            
            # Formateo de cantidades y costos
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

def abrir_pdf(output_path):
    """Abre automáticamente el archivo PDF en el visor predeterminado del SO."""
    try:
        if os.name == 'nt':  # Windows
            os.startfile(output_path)
        elif os.name == 'posix':
            subprocess.run(['open', output_path] if os.uname().sysname == 'Darwin' else ['xdg-open', output_path])
    except Exception as e:
        print(f"No se pudo abrir el PDF automáticamente: {e}")
