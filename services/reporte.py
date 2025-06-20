# services/reporte.py
"""
Módulo para la generación de reportes PDF.
"""
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime

# TODO: Permitir personalizar el formato del reporte y los estilos

def generar_pdf_report(documentos_clasificados, resultados_comparaciones):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12
    )
    elements = []
    elements.append(Paragraph("Reporte de Análisis de Documentos", title_style))
    elements.append(Paragraph(f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Resumen de Documentos Analizados", heading_style))
    resumen_docs = [
        ["Tipo de Documento", "Cantidad"],
        ["Carta Laboral", str(len(documentos_clasificados["carta laboral"]))],
        ["Colillas de Pago", str(len(documentos_clasificados["colilla de pago"]))],
        ["Extractos Bancarios", str(len(documentos_clasificados["extracto bancario"]))]
    ]
    t = Table(resumen_docs, colWidths=[3*inch, 3*inch])
    t.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))
    if resultados_comparaciones:
        elements.append(Paragraph("Resultados de Comparaciones", heading_style))
        for comparacion in resultados_comparaciones:
            resultado = comparacion["resultado"]
            elements.append(Paragraph(f"Comparación: {comparacion['tipo']}", styles["Heading3"]))
            info_comparacion = [
                ["Porcentaje de Coincidencia:", resultado.get("porcentaje", "N/A")],
                ["Explicación:", resultado.get("explicacion", "N/A")]
            ]
            t = Table(info_comparacion, colWidths=[2*inch, 4*inch])
            t.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (0, -1), colors.grey),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
            ]))
            elements.append(t)
            if "no_coincide" in resultado:
                elements.append(Paragraph("Discrepancias Encontradas:", styles["Heading4"]))
                for campo, valores in resultado["no_coincide"].items():
                    elementos_discrepancia = [
                        ["Campo", campo.title()],
                        ["Valor 1", str(valores.get('colilla_pago', valores.get('extracto_bancario', 'N/A')))],
                        ["Valor 2", str(valores.get('carta_laboral', valores.get('colilla_pago', 'N/A')))]
                    ]
                    t = Table(elementos_discrepancia, colWidths=[2*inch, 4*inch])
                    t.setStyle(TableStyle([
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('BACKGROUND', (0, 0), (0, -1), colors.grey),
                        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 12),
                    ]))
                    elements.append(t)
            elements.append(Spacer(1, 20))
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf 