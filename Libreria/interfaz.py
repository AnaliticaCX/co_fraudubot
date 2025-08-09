import streamlit as st
from typing import Dict, Any
from .generador_pdf import generar_pdf_report

def mostrar_resultados_comparacion(resultados: Dict[str, Any]):
    """
    Muestra los resultados de la comparación en la interfaz.
    """
    st.subheader("Resultados de la Comparación")
    st.write(f"Porcentaje de coincidencia: {resultados['resultado_comparacion']['porcentaje']}")
    st.write(f"Explicación: {resultados['resultado_comparacion']['explicacion']}")
    
    # Mostrar resultados individuales
    st.subheader("Resultados por Colilla")
    for i, resultado in enumerate(resultados['resultado_comparacion']['resultados_individuales'], 1):
        st.write(f"Colilla {i}:")
        st.write(f"- Porcentaje: {resultado['porcentaje']}")
        st.write(f"- Explicación: {resultado['explicacion']}")
        if resultado['no_coincide']:
            st.write("Diferencias encontradas:")
            for campo, valores in resultado['no_coincide'].items():
                st.write(f"- {campo}:")
                st.write(f"  - Carta Laboral: {valores['carta_laboral']}")
                st.write(f"  - Colilla de Pago: {valores['colilla_pago']}")
        st.write("---")

def mostrar_boton_descarga_pdf(resultados: Dict[str, Any]):
    """
    Muestra el botón de descarga del PDF.
    """
    if st.button("Descargar Reporte PDF"):
        try:
            pdf_bytes = generar_pdf_report(resultados)
            st.download_button(
                label="Descargar PDF",
                data=pdf_bytes,
                file_name="reporte_comparacion.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Error al generar el PDF: {str(e)}")
