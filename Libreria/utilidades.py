import streamlit as st
from typing import Dict, Any, List
import json

def formatear_valor_monetario(valor: Any) -> str:
    """
    Formatea un valor monetario con el símbolo de peso y separadores de miles.
    """
    try:
        if isinstance(valor, str):
            # Eliminar caracteres no numéricos
            valor = ''.join(filter(str.isdigit, valor))
            valor = int(valor)
        return f"${valor:,}"
    except:
        return "$0"

def mostrar_resultados_comparacion(resultados: Dict[str, Any]) -> None:
    """
    Muestra los resultados de la comparación en la interfaz de Streamlit.
    """
    st.subheader("Resultados de la Comparación")
    st.write(f"Porcentaje de coincidencia promedio: {resultados['porcentaje']}")
    st.write(f"Explicación: {resultados['explicacion']}")
    
    if 'resultados_individuales' in resultados:
        st.subheader("Resultados por Colilla")
        for i, resultado in enumerate(resultados['resultados_individuales'], 1):
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

def mostrar_datos_carta_laboral(datos: Dict[str, str]) -> None:
    """
    Muestra los datos extraídos de la carta laboral en la interfaz de Streamlit.
    """
    if datos:
        st.subheader("Datos de la Carta Laboral")
        
        # Datos personales
        st.write("**Datos Personales:**")
        st.write(f"- Nombre: {datos.get('nombre', 'No disponible')}")
        st.write(f"- Cédula: {datos.get('cedula', 'No disponible')}")
        st.write(f"- Origen Cédula: {datos.get('de_donde_es_la_cedula', 'No disponible')}")
        
        # Datos laborales
        st.write("**Datos Laborales:**")
        st.write(f"- Cargo: {datos.get('cargo', 'No disponible')}")
        st.write(f"- Tipo de Contrato: {datos.get('tipo_de_contrato', 'No disponible')}")
        st.write(f"- Salario: {formatear_valor_monetario(datos.get('salario', '0'))}")
        st.write(f"- Bonificación: {formatear_valor_monetario(datos.get('bonificacion', '0'))}")
        
        # Datos de la empresa
        st.write("**Datos de la Empresa:**")
        st.write(f"- Nombre: {datos.get('nombre_de_la_empresa', 'No disponible')}")
        st.write(f"- NIT: {datos.get('nit_de_la_empresa', 'No disponible')}")
        
        # Fechas
        st.write("**Fechas:**")
        st.write(f"- Inicio: {datos.get('fecha_inicio_labor', 'No disponible')}")
        st.write(f"- Fin: {datos.get('fecha_fin_labor', 'No disponible')}")
        st.write(f"- Expedición: {datos.get('fecha_de_expedicion_carta', 'No disponible')}")
