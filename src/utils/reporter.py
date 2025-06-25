# src/utils/reporter.py

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime

def generar_reporte_ventas_pdf(ruta_archivo: str, ventas: list, datos_empresa: dict = None):
    """
    Genera un reporte en PDF del historial de ventas.

    Args:
        ruta_archivo (str): La ruta completa donde se guardará el PDF.
        ventas (list): Una lista de objetos de venta.
        datos_empresa (dict, optional): Datos de la empresa para el encabezado.
    """
    doc = SimpleDocTemplate(ruta_archivo, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # --- Encabezado del Reporte ---
    if datos_empresa and datos_empresa.get('nombre'):
        story.append(Paragraph(datos_empresa['nombre'], styles['h1']))
    else:
        story.append(Paragraph("Reporte de Ventas", styles['h1']))

    fecha_reporte = f"Fecha del reporte: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    story.append(Paragraph(fecha_reporte, styles['Normal']))
    story.append(Spacer(1, 0.2 * inch))

    # --- Tabla de Datos ---
    datos_tabla = [["ID", "Fecha", "Producto", "Cant.", "Precio Unit.", "Total"]]
    total_general = 0.0

    for venta in ventas:
        total_general += venta.total_venta
        datos_tabla.append([
            str(venta.id),
            venta.fecha_venta.strftime('%Y-%m-%d %H:%M'),
            venta.producto.nombre if venta.producto else "N/A",
            str(venta.cantidad),
            f"${venta.precio_unitario_venta:,.2f}",
            f"${venta.total_venta:,.2f}"
        ])

    tabla = Table(datos_tabla)
    estilo_tabla = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    tabla.setStyle(estilo_tabla)
    story.append(tabla)
    story.append(Spacer(1, 0.2 * inch))

    # --- Pie de página con el total ---
    story.append(Paragraph(f"<b>Total General de Ventas:</b> ${total_general:,.2f}", styles['h3']))

    # Construir el PDF
    doc.build(story)