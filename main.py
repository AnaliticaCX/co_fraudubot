import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


# main.py
import streamlit as st

# Primero, configurar la página
st.set_page_config(
    page_title="Fraudubot - Análisis de Documentos",
    page_icon="🔍",
    layout="wide"
)
from libreria.login import verificar_login

verificar_login()

##st.title(f"Bienvenida, {st.session_state['usuario']} 👋")
st.write(f"Bienvenida, {st.session_state['usuario']} 👋")

import streamlit as st
import os
import pandas as pd
from PIL import Image

# Importar servicios modularizados
from services.modelos import obtener_modelo_ia
from services.extraccion import extraer_texto, extraer_datos_carta_laboral, extraer_datos_extracto_bancario, extraer_datos_colilla_pago
from services.comparacion import comparar_documentos
from services.visual import analizar_documento_visual
from services.metadatos import extraer_metadatos
from services.reporte import generar_pdf_report
from services.utilidades import formatear_valor_monetario
from services.consulta_rues import consultar_empresa_por_nit


# Personalización de colores de fondo y texto
st.markdown("""
    <style>
    /* Fondo principal */
    .stApp {
        background-color: #fcfcfc !important;
        color: #222 !important;
    }
    /* Barra lateral: fondo y texto */
    section[data-testid="stSidebar"] {
        background-color: rgb(5, 27, 95) !important;
        color: #fff !important;
    }
    section[data-testid="stSidebar"] * {
        background-color: transparent !important;
        color: #fff !important;
        border-color: #fff !important;
    }
    section[data-testid="stSidebar"] .st-bw {
        background-color: rgb(5, 27, 95) !important;
    }
    section[data-testid="stSidebar"] .st-af {
        background-color: rgb(5, 27, 95) !important;
    }
    section[data-testid="stSidebar"] .st-c6 {
        background-color: rgb(5, 27, 95) !important;
    }
    section[data-testid="stSidebar"] .st-emotion-cache-1v0mbdj,
    section[data-testid="stSidebar"] .st-emotion-cache-1cpxqw2,
    section[data-testid="stSidebar"] .st-emotion-cache-1offfwp,
    section[data-testid="stSidebar"] label {
        color: #fff !important;
    }
    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] textarea,
    section[data-testid="stSidebar"] select {
        background-color: #fff !important;
        color: #051b5f !important;
        border-radius: 5px !important;
    }
    section[data-testid="stSidebar"] .st-emotion-cache-1v0mbdj {
        color: #fff !important;
    }
    /* Barra superior (header) */
    header[data-testid="stHeader"] {
        background-color: rgb(5, 27, 95) !important;
    }
    header[data-testid="stHeader"] > div {
        background-color: rgb(5, 27, 95) !important;
    }
    header[data-testid="stHeader"] .st-emotion-cache-1avcm0n,
    header[data-testid="stHeader"] .st-emotion-cache-1dp5vir,
    header[data-testid="stHeader"] .st-emotion-cache-18ni7ap,
    header[data-testid="stHeader"] .st-emotion-cache-6qob1r,
    header[data-testid="stHeader"] * {
        background-color: rgb(5, 27, 95) !important;
        color: #fff !important;
    }
    /* Tablas de Streamlit */
    .stTable, .tabla-personalizada {
        background-color: #f0f4fa !important;
        color: #222 !important;
        border-radius: 10px !important;
        border: 1px solid #051b5f !important;
        margin-bottom: 2rem !important;
        font-family: 'Inter', 'system-ui', 'sans-serif' !important;
        font-size: 1rem !important;
    }
    .stTable th, .tabla-personalizada th {
        background-color: #051b5f !important;
        color: #fff !important;
        font-weight: bold !important;
        font-family: 'Inter', 'system-ui', 'sans-serif' !important;
    }
    .stTable td, .tabla-personalizada td {
        background-color: #f8fafc !important;
        color: #222 !important;
        font-family: 'Inter', 'system-ui', 'sans-serif' !important;
    }
    /* Texto principal */
    .stApp {
        color: #222 !important;
    }
    /* Porcentaje Promedio destacado */
    .porcentaje-promedio {
        color: rgb(5, 27, 95) !important;
        font-weight: bold;
        font-size: 1.2rem;
    }
    /* Resumen de comparación y explicación detallada */
    .resumen-comparacion {
        font-family: 'Inter', 'system-ui', 'sans-serif';
        font-size: 1rem;
        color: #222;
        max-width: 100%;
        word-break: break-word;
        white-space: pre-line;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- MODELOS Y BASE DE DATOS ---
# Selección del modelo
st.sidebar.title("⚙️ Configuración")
modelo_seleccionado = st.sidebar.radio(
    "Selecciona el modelo de IA:",
    ["OpenAI", "Gemini", "DeepSeek Local"],
    index=0
)
modelo = obtener_modelo_ia(modelo_seleccionado)

# Mostrar el modelo seleccionado
st.sidebar.info(f"Modelo actual: {modelo_seleccionado}")

# --- INTERFAZ STREAMLIT ---
# TODO: Mantener solo la lógica de la interfaz y orquestación aquí
# El resto de la lógica debe estar en los módulos de services/

# Estilo personalizado
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .sospecha {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .coincidencia {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Mostrar logo centrado en la parte superior
logo = Image.open("img/logo_fraudubot.png")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image(logo, use_container_width=True)

# --- Input para número de solicitud ---
    with st.container():
        st.subheader("📝 Registra el número de solicitud")

        # Crear columnas para centrar el input y el botón
        col1, col2, col3 = st.columns([2, 3, 2])  # Ajusta proporciones según necesites

        with col2:
            id_solicitud = st.text_input("Número de solicitud", label_visibility="collapsed")

            if st.button("Confirmar"):
                if id_solicitud:
                    st.session_state['id_solicitud'] = id_solicitud
                    st.markdown(
                        f"""
                        <div style="background-color:#d4edda; padding:10px; border-radius:5px; border:1px solid #c3e6cb; display: inline-block; margin-bottom: 0px;">
                            <span style="color:#6c757d; white-space: nowrap;">Número de solicitud registrado: {id_solicitud}</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.warning("Por favor ingresa un número de solicitud válido.")


# Sección de carga de archivos
with st.container():
    st.subheader("📤 Carga de Documentos")
uploaded_files = st.file_uploader(
        "Sube los documentos a analizar (carta laboral, colillas, extractos)", 
    type=["pdf", "png", "jpg"], 
    accept_multiple_files=True
)

if uploaded_files:
    # Barra de progreso
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Procesamiento de documentos
    documentos_clasificados = {
        "colilla de pago": [],
        "carta laboral": [],
        "extracto bancario": [],
        "otro": []
    }

    # Procesar cada documento
    for i, archivo in enumerate(uploaded_files):
        status_text.text(f"Procesando {archivo.name}...")
        progress_bar.progress((i + 1) / len(uploaded_files))

        path = os.path.join("temp", archivo.name)
        with open(path, "wb") as f:
            f.write(archivo.getbuffer())

        # Análisis de texto y visual
        texto = extraer_texto(path)
        tipo = modelo.clasificar_documento(texto)
        analisis_visual = analizar_documento_visual(path)
        metadatos = extraer_metadatos(path)
        
        # Extraer datos según el tipo de documento
        datos_documento = {}
        if tipo == "extracto bancario":
            datos_documento = extraer_datos_extracto_bancario(modelo, texto)
            print("Datos del extracto bancario:", datos_documento)
        elif tipo == "colilla de pago":
            datos_documento = extraer_datos_colilla_pago(modelo, texto)
            print("Datos de la colilla de pago:", datos_documento)
        
        documentos_clasificados[tipo].append({
            "nombre_archivo": archivo.name,
            "texto": texto,
            "path": path,
            "analisis_visual": analisis_visual,
            "metadatos": metadatos,
            "datos_documento": datos_documento  # <-- aquí se guardan los datos extraídos
        })

    # Limpiar barra de progreso
    progress_bar.empty()
    status_text.empty()

    # Mostrar resultados por tipo de documento
    st.markdown("## 📊 Resumen de Documentos Analizados")
    
    # Crear DataFrame para la tabla resumen
    resumen_data = []
    
    for tipo, docs in documentos_clasificados.items():
        if docs:
            for doc in docs:
                analisis = doc["analisis_visual"]
                if "error" not in analisis:
                    # Determinar calidad
                    nitidez = analisis["calidad"]["nitidez"]
                    if nitidez > 200:
                        calidad = "Alta"
                    elif nitidez > 100:
                        calidad = "Media"
                    elif nitidez > 50:
                        calidad = "Baja"
                    else:
                        calidad = "Mala"
                    
                    resumen_data.append({
                        "Tipo de Documento": tipo.upper(),
                        "Nombre": doc["nombre_archivo"],
                        "Sellos": "Sí" if analisis["numero_sellos"] > 0 else "No",
                        "Marcas de Agua": "Sí" if analisis["marcas_agua"] > 0 else "No",
                        "Firmas": "Sí" if len(analisis["firmas_detectadas"]) > 0 else "No",
                        "Calidad": calidad
                    })
    
    if resumen_data:
        df_resumen = pd.DataFrame(resumen_data)
        st.table(df_resumen)
        
        # Mostrar alertas de cada documento
        st.markdown("## ⚠️ Alertas Detectadas")
        for tipo, docs in documentos_clasificados.items():
            if docs:
                for doc in docs:
                    analisis = doc["analisis_visual"]
                    if "error" not in analisis and analisis["sospechas"]:
                        st.markdown(f"""
                        <div style="background-color: #ffebee; padding: 15px; border-radius: 5px; margin: 10px 0;">
                            <h4 style="color: #c62828; margin: 0;">{doc['nombre_archivo']}</h4>
                            <ul style="margin: 10px 0;">
                        """, unsafe_allow_html=True)
                        
                        for sospecha in analisis["sospechas"]:
                            st.markdown(f"<li style='color: #b71c1c;'>{sospecha}</li>", unsafe_allow_html=True)
                    
                        st.markdown("</ul></div>", unsafe_allow_html=True)

    # Mostrar resumen de la carta laboral
    if documentos_clasificados["carta laboral"]:
        st.markdown("## 📄 Resumen de la Carta Laboral")
        
        # Extraer datos de la carta laboral
        carta = documentos_clasificados["carta laboral"][0]
        datos_carta = extraer_datos_carta_laboral(modelo, carta["texto"])
        print("Datos carta laboral:", datos_carta)

        if "error" not in datos_carta:
            # Crear columnas para mostrar la información
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### 👤 Datos Personales")
                st.markdown(f"**Nombre:** {datos_carta.get('nombre', 'No disponible')}")
                st.markdown(f"**Cédula:** {datos_carta.get('cedula', 'No disponible')}")
                st.markdown(f"**Ciudad de Origen:** {datos_carta.get('de_donde_es_la_cedula', 'No disponible')}")
            
            with col2:
                st.markdown("### 💼 Datos Laborales")
                st.markdown(f"**Cargo:** {datos_carta.get('cargo', 'No disponible')}")
                st.markdown(f"**Tipo de Contrato:** {datos_carta.get('tipo_de_contrato', 'No disponible')}")
                st.markdown(f"**Fecha Inicio:** {datos_carta.get('fecha_inicio_labor', 'No disponible')}")
                st.markdown(f"**Fecha Fin:** {datos_carta.get('fecha_fin_labor', 'No disponible')}")
            
            with col3:
                salario = datos_carta.get('salario')
                bonificacion = datos_carta.get('bonificacion')
                st.markdown("### 🏢 Datos de la Empresa")
                st.markdown(f"**Empresa:** {datos_carta.get('nombre_de_la_empresa', 'No disponible')}")
                st.markdown(f"**NIT:** {datos_carta.get('nit_de_la_empresa', 'No disponible')}")
                st.markdown(f"**Salario:** {formatear_valor_monetario(salario) if salario else 'No disponible'}")
                st.markdown(f"**Bonificación:** {formatear_valor_monetario(bonificacion) if bonificacion else 'No disponible'}")

            # Consultar datos de la empresa en RUES y mostrarlos
            nit_empresa = datos_carta.get('nit_de_la_empresa')
            if nit_empresa and nit_empresa != 'No disponible':
                st.markdown("### 🏢 Datos en RUES")
                datos_rues = consultar_empresa_por_nit(nit_empresa)
                if 'error' in datos_rues:
                    st.warning(f"No se pudo consultar RUES: {datos_rues['error']}")
                else:
                    st.markdown(f"**Nombre:** {datos_rues.get('nombre', 'No disponible')}")
                    st.markdown(f"**NIT:** {datos_rues.get('identificacion', 'No disponible')}")
                    st.markdown(f"**Matrícula:** {datos_rues.get('matricula', 'No disponible')}")
                    st.markdown(f"**Estado:** {datos_rues.get('estado', 'No disponible')}")
                    st.markdown(f"**Cámara de Comercio:** {datos_rues.get('camara', 'No disponible')}")
                    st.markdown(f"**Categoría:** {datos_rues.get('categoria', 'No disponible')}")
    # Comparación de documentos
    if len(documentos_clasificados["carta laboral"]) > 0 or len(documentos_clasificados["colilla de pago"]) > 0 or len(documentos_clasificados["extracto bancario"]) > 0:
        st.markdown("## 🔄 Comparación de Documentos")
        
        # Realizar todas las comparaciones posibles
        resultados_comparaciones = []
        
        # Si tenemos los tres tipos de documentos, hacer comparaciones triples
        if (documentos_clasificados["carta laboral"] and 
            documentos_clasificados["colilla de pago"] and 
            documentos_clasificados["extracto bancario"]):
            
            carta = documentos_clasificados["carta laboral"][0]
            extracto = documentos_clasificados["extracto bancario"][0]
            
            for colilla in documentos_clasificados["colilla de pago"]:
                # Comparar colilla con carta
                resultado_colilla_carta = comparar_documentos(
                    modelo,
                    colilla["texto"],
                    carta["texto"]
                )
                
                # Comparar colilla con extracto
                resultado_colilla_extracto = comparar_documentos(
                    modelo,
                    colilla["texto"],
                    extracto["texto"]
                )
                
                # Función auxiliar para obtener valores de forma segura
                def obtener_valor_seguro(resultado, tipo_doc, campo):
                    try:
                        if isinstance(resultado, dict):
                            # Primero intentar obtener del documento directamente
                            if tipo_doc == "extracto_bancario":
                                if "datos_documento" in resultado:
                                    datos = resultado["datos_documento"]
                                    if campo == "nombre":
                                        return datos.get("nombre_titular", "N/A")
                                    elif campo == "cuenta":
                                        return datos.get("numero_cuenta", "N/A")
                                    elif campo == "salario":
                                        return str(datos.get("promedio_ingresos", "N/A"))
                                    elif campo == "tipo_ingreso":
                                        return datos.get("tipo_ingreso", "N/A")
                            elif tipo_doc == "colilla_pago":
                                if "datos_documento" in resultado:
                                    datos = resultado["datos_documento"]
                                    if campo == "nombre":
                                        return datos.get("nombre_empleado", "N/A")
                                    elif campo == "salario":
                                        # Usar directamente el campo salario que ya incluye el total
                                        return str(datos.get("salario", "N/A"))
                                    elif campo == "empresa":
                                        return datos.get("empresa", "N/A")
                            
                            # Si no se encuentra en datos_documento, intentar en no_coincide
                            if "no_coincide" in resultado:
                                if campo in resultado["no_coincide"]:
                                    if tipo_doc in resultado["no_coincide"][campo]:
                                        valor = resultado["no_coincide"][campo][tipo_doc]
                                        if valor is not None and valor != "":
                                            return valor
                            
                            # Si aún no se encuentra, intentar en valores
                            if "valores" in resultado:
                                if tipo_doc in resultado["valores"]:
                                    if campo in resultado["valores"][tipo_doc]:
                                        valor = resultado["valores"][tipo_doc][campo]
                                        if valor is not None and valor != "":
                                            return valor
                        return "N/A"
                    except Exception as e:
                        print(f"Error al obtener valor para {tipo_doc} - {campo}: {str(e)}")
                        return "N/A"
                
                # Calcular porcentaje promedio considerando los tres documentos
                porcentaje_colilla_carta = float(resultado_colilla_carta.get('porcentaje', '0%').strip('%'))
                porcentaje_colilla_extracto = float(resultado_colilla_extracto.get('porcentaje', '0%').strip('%'))
                porcentaje_carta_extracto = float(comparar_documentos(modelo, carta["texto"], extracto["texto"]).get('porcentaje', '0%').strip('%'))
                
                # Calcular el promedio de los tres porcentajes
                porcentaje_promedio = (porcentaje_colilla_carta + porcentaje_colilla_extracto + porcentaje_carta_extracto) / 3
                
                # Combinar resultados
                resultado_combinado = {
                    "tipo": "Comparación Triple",
                    "resultado": {
                        "porcentaje": f"{porcentaje_promedio:.2f}%",
                        "explicacion": f"Comparación de datos del extracto bancario:\n" +
                                     f"- Nombre del titular: {extracto['datos_documento'].get('nombre_titular', 'N/A')}\n" +
                                     f"- Promedio de ingresos: {extracto['datos_documento'].get('promedio_ingresos', 'N/A')}\n" +
                                     f"vs\n" +
                                     f"- Nombre en carta laboral: {obtener_valor_seguro(resultado_colilla_carta, 'carta_laboral', 'nombre')}\n" +
                                     f"- Salario en carta laboral: {obtener_valor_seguro(resultado_colilla_carta, 'carta_laboral', 'salario')}\n" +
                                     f"- Nombre en colilla: {obtener_valor_seguro(resultado_colilla_carta, 'colilla_pago', 'nombre')}\n" +
                                     f"- Salario en colilla: {obtener_valor_seguro(resultado_colilla_carta, 'colilla_pago', 'salario')}",
                        "datos_extracto": extracto.get("datos_documento", {}),
                        "no_coincide": {
                            "nombre": {
                                "carta_laboral": obtener_valor_seguro(resultado_colilla_carta, "carta_laboral", "nombre"),
                                "colilla_pago": obtener_valor_seguro(resultado_colilla_carta, "colilla_pago", "nombre"),
                                "extracto_bancario": extracto["datos_documento"].get("nombre_titular", "N/A")
                            },
                            "salario": {
                                "carta_laboral": obtener_valor_seguro(resultado_colilla_carta, "carta_laboral", "salario"),
                                "colilla_pago": obtener_valor_seguro(resultado_colilla_carta, "colilla_pago", "salario"),
                                "extracto_bancario": str(extracto["datos_documento"].get("promedio_ingresos", "N/A"))
                            }
                        }
                    }
                }
                resultados_comparaciones.append(resultado_combinado)
        
        # Si solo tenemos dos tipos de documentos, hacer comparaciones dobles
        else:
            # Comparar carta laboral con colillas
            if documentos_clasificados["carta laboral"] and documentos_clasificados["colilla de pago"]:
                for colilla in documentos_clasificados["colilla de pago"]:
                    resultado = comparar_documentos(
                        modelo,
                        colilla["texto"],
                        documentos_clasificados["carta laboral"][0]["texto"]
                    )
                    resultados_comparaciones.append({
                        "tipo": "Carta Laboral vs Colilla",
                        "resultado": resultado
                    })
            
            # Comparar carta laboral con extractos
            if documentos_clasificados["carta laboral"] and documentos_clasificados["extracto bancario"]:
                for extracto in documentos_clasificados["extracto bancario"]:
                    resultado = comparar_documentos(
                        modelo,
                        extracto["texto"],
                        documentos_clasificados["carta laboral"][0]["texto"]
                    )
                    resultados_comparaciones.append({
                        "tipo": "Carta Laboral vs Extracto",
                        "resultado": resultado
                    })
            
            # Comparar colillas con extractos
            if documentos_clasificados["colilla de pago"] and documentos_clasificados["extracto bancario"]:
                for colilla in documentos_clasificados["colilla de pago"]:
                    for extracto in documentos_clasificados["extracto bancario"]:
                        resultado = comparar_documentos(
                            modelo,
                            colilla["texto"],
                            extracto["texto"]
                        )
                        resultados_comparaciones.append({
                            "tipo": "Colilla vs Extracto",
                            "resultado": resultado
                        })
        
        # Mostrar resultados de las comparaciones
        if resultados_comparaciones:
            for comparacion in resultados_comparaciones:
                st.markdown(f"### 📊 {comparacion['tipo']}")
                resultado = comparacion['resultado']
                
                # Crear dos columnas para el layout
                col_izq, col_der = st.columns(2)
                
                with col_izq:
                    # Mostrar porcentaje y explicaciones
                    st.markdown("#### 📈 Resumen de Coincidencias")
                    st.markdown(f"<div class='porcentaje-promedio'>Porcentaje Promedio: {resultado['porcentaje']}</div>", unsafe_allow_html=True)
                    
                    st.markdown("#### 📝 Explicación Detallada")
                    st.markdown(f"<div class='resumen-comparacion'>{resultado['explicacion']}</div>", unsafe_allow_html=True)
                
                with col_der:
                    # Mostrar análisis detallado en una tabla
                    st.markdown("#### 🔍 Análisis Detallado")
                    if "no_coincide" in resultado:
                        # Crear una lista para almacenar los datos de la tabla
                        tabla_data = []
                        
                        # Agregar encabezados
                        headers = ["Campo"]
                        if "extracto_bancario" in resultado["no_coincide"]["nombre"]:
                            headers.append("Extracto Bancario")
                        if "colilla_pago" in resultado["no_coincide"]["nombre"]:
                            headers.append("Colilla de Pago")
                        if "carta_laboral" in resultado["no_coincide"]["nombre"]:
                            headers.append("Carta Laboral")
                        
                        # Agregar filas para cada campo
                        for campo in ["nombre", "empresa", "salario", "cuenta", "tipo_ingreso"]:
                            if campo in resultado["no_coincide"]:
                                row = [campo.title()]
                                if "extracto_bancario" in resultado["no_coincide"][campo]:
                                    row.append(resultado["no_coincide"][campo]["extracto_bancario"])
                                if "colilla_pago" in resultado["no_coincide"][campo]:
                                    row.append(resultado["no_coincide"][campo]["colilla_pago"])
                                if "carta_laboral" in resultado["no_coincide"][campo]:
                                    row.append(resultado["no_coincide"][campo]["carta_laboral"])
                                tabla_data.append(row)
                        
                        # Crear y mostrar la tabla
                        if tabla_data:
                            df = pd.DataFrame(tabla_data, columns=headers)
                            st.markdown(df.to_html(classes='tabla-personalizada', index=False), unsafe_allow_html=True)
                
                st.markdown("---")

    # Generar reporte PDF
    if resultados_comparaciones:
        pdf_bytes = generar_pdf_report(documentos_clasificados, resultados_comparaciones)
        
        # Botón para descargar el reporte
        st.download_button(
            label="📥 Descargar Reporte PDF",
            data=pdf_bytes,
            file_name="reporte_analisis.pdf",
                mime="application/pdf"
            )

from services.pipeline import preprocesamiento    
from services.pipeline import cargar_datos_desde_bd

if st.button("Consultar probabilidad"):
    with st.spinner("Ejecutando análisis..."):
        df = cargar_datos_desde_bd()
        df = df[df['SOLICITUD'] == int(st.session_state['id_solicitud'])]
        resultado = preprocesamiento.transform(df)  # Aquí llamas tu pipeline importado
        st.success("✅ Pipeline ejecutado correctamente.")

        # Mostrar resultados si quieres
        st.write("Este cliente tiene una probabilidad de fraude del: " + str(resultado[0]))
   

