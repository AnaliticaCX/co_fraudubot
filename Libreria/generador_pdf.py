from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
from datetime import datetime
from typing import Dict, Any, List

def generar_pdf_report(documentos_clasificados, resultados_comparaciones):
    """
    Genera un reporte PDF con los resultados del análisis.
    
    Args:
        documentos_clasificados (dict): Diccionario con los documentos clasificados
        resultados_comparaciones (list): Lista de resultados de comparaciones entre documentos
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Estilos
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
        fontSize=18,
        spaceAfter=20
    )
    
    # Título
    elements.append(Paragraph("Reporte de Análisis de Documentos", title_style))
    elements.append(Spacer(1, 20))
    
    # Resumen de documentos analizados
    elements.append(Paragraph("Resumen de Documentos Analizados", heading_style))
    elementos_resumen = [
        ["Tipo de Documento", "Cantidad"],
        ["Carta Laboral", str(len(documentos_clasificados["carta laboral"]))],
        ["Colillas de Pago", str(len(documentos_clasificados["colilla de pago"]))],
        ["Extractos Bancarios", str(len(documentos_clasificados["extracto bancario"]))]
    ]
    
    t = Table(elementos_resumen, colWidths=[3*inch, 3*inch])
        t.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 20))
    
    # Resultados de comparaciones
    if resultados_comparaciones:
        elements.append(Paragraph("Resultados de Comparaciones", heading_style))
        
        for comparacion in resultados_comparaciones:
            # Título de la comparación
            elements.append(Paragraph(comparacion["tipo"], styles["Heading3"]))
            resultado = comparacion["resultado"]
            
            # Porcentaje de coincidencia
            elementos_comparacion = [
                ["Métrica", "Valor"],
                ["Porcentaje de Coincidencia", resultado["porcentaje"]]
            ]
            
            t = Table(elementos_comparacion, colWidths=[3*inch, 3*inch])
            t.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 10))
    
            # Discrepancias encontradas
            if "no_coincide" in resultado:
                elements.append(Paragraph("Discrepancias Encontradas", styles["Heading4"]))
                elementos_discrepancias = [["Campo", "Documento 1", "Documento 2"]]
                
                for campo, valores in resultado["no_coincide"].items():
                    elementos_discrepancias.append([
                        campo.title(),
                        valores["doc1"],
                        valores["doc2"]
                    ])
                
                t = Table(elementos_discrepancias, colWidths=[2*inch, 2*inch, 2*inch])
                t.setStyle(TableStyle([
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 12),
                ]))
                elements.append(t)
                elements.append(Spacer(1, 10))
            
            # Análisis detallado
            if "analisis_discrepancias" in resultado:
                elements.append(Paragraph("Análisis Detallado", styles["Heading4"]))
                elements.append(Paragraph(resultado["analisis_discrepancias"], styles["Normal"]))
            
            elements.append(Spacer(1, 20))
    
    # Construir el PDF
    doc.build(elements)
    
    # Obtener el valor del buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    return pdf
