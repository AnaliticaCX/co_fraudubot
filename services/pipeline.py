import pandas as pd
import numpy as np

def cargar_datos_desde_bd(query="SELECT * FROM TBL_IA_SOLICITUDES"):
        import sys
        sys.path.append('libreria')  # Agregamos la carpeta 'libreria' al path

        from conector import obtener_conexion  # Ahora sí podrás importarlo
        try:
            conn = obtener_conexion()
            if conn:
                cursor = conn.cursor()
                cursor.execute(query)

                columnas = [col[0] for col in cursor.description]
                datos = cursor.fetchall()

                df = pd.DataFrame(datos, columns=columnas)

                cursor.close()
                conn.close()
                return df
            else:
                print(" No se pudo establecer la conexión a la base de datos.")
                return None

        except Exception as e:
            print(f" Error al ejecutar la consulta: {e}")
            return df



    #---- Filtrar por el cliente de interes

def buscar_solicitud(df):
        ##id_solicitud  = 2421080
        return df[df['SOLICITUD'] == 2421080]


def convertir_campos_numericos(df):

        columnas_a_convertir = [
            'ENDEUDAMIENTO_CF_TOTAL',
            'TOTALENDEUDAMIENTO',
            'GASTOS_PREAPROB_SIMU',
            'EGRESOS_TOTAL',
            'INGRESOS_TOTAL',
            'VALIDADORDC_PROM_INGRESOS'
        ]
        
        for col in columnas_a_convertir:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            else:
                print(f"⚠️ La columna '{col}' no existe en el DataFrame.")
        
        return df


def transformar_variables_credito(df):

        # Conteo negaciones por motivos específicos
        df['conteo_negadoIDVISION'] = np.where(
            (df['MOTIVO_SOL_NEGADA'] == 'Negación IDVISIÓN') | 
            (df['MOTIVO_SOL_NEGADA'] == 'Alerta en Sagrilaft'),
            1, 0
        )
        
        df['MOTIVO_NEGACION_ANTERIOR'] = np.where(~df['ESTADO_SOLICITUD'].isin(['Desembolsado','Negada']),df['MOTIVO_SOL_NEGADA'],'Na')

        # ENDEUDAMIENTO_AJUSTADO
        df['ENDEUDAMIENTO_AJUSTADO'] = (
            np.maximum(df['ENDEUDAMIENTO_CF_TOTAL'], df['TOTALENDEUDAMIENTO']) + 
            df.get('ENDEUDAMIENTO_CF_TOTAL_TARJETAS', 0)
        ).fillna(0)
        
        
        df['SIMOCUP2'] = np.where((df['SIMOCUP']=='APLICACION')| (df['SIMOCUP']=='INDEP'),'INDEP',
                        np.where((df['SIMOCUP']=='EMPLEADO') | (df['SIMOCUP']=='FUERAR'),'EMPLEADO','NA'))
        
        df['TIPO_SUBTIPO_CLIENTE'] = np.where(df['SIMOCUP2']=='EMPLEADO',df['SIMOCUP2']+'_'+df['PRESTACIONES_SOCIALES'].astype(str),
                                                np.where(df['SIMOCUP2']=='INDEP','INDEP','NA'))
        
        df['producer_docs'] = 'canva'
        df['nitidez_docs_min'] = 100
        df['max_dias_docs'] = 30

        # Rellenar columnas con 0 si hay NaN
        columnas_fillna = [
            'CONTEO_TELEFONO_RECONOCER',
            'CONTEO_EMAIL_RECONOCER',
            'PERSONAS_CARGO',
            'CANT_MORA30_ULT12MESES_HISTORICO',
            'CANT_MORA60_ULT12MESES_HISTORICO',
            'CANT_MORA90_ULT12MESES_HISTORICO',
            'CANT_MORA120_ULT12MESES_HISTORICO',
            'COINCIDE_DIRECCION'
        ]
        
        df['COINCIDE_CEL_RECONOCER'] = 1
        df['COINCIDE_EMAIL_RECONOCER'] = 1
        df['COINCIDE_DEPARTAMENTO'] = 1
        df['ZONA_COBERTURA_ALTO_RIESGO'] = 'No'
        df['CANAL_ATENCION'] = 'Dealer' 
        df['ZONA_DEALER'] = 'ZONA BOGOTA'

        for col in columnas_fillna:
            if col in df.columns:
                df[col] = df[col].fillna(0)
            else:
                print(f"⚠️ La columna '{col}' no existe en el DataFrame.")

        # EGRESOS e INGRESOS consolidados
        df['EGRESOS_CONSOLIDADO'] = np.maximum(df['GASTOS_PREAPROB_SIMU'], df['EGRESOS_TOTAL'])
        df['INGRESOS_CONSOLIDADO'] = np.minimum(df['INGRESOS_TOTAL'], df['VALIDADORDC_PROM_INGRESOS'])

        return df


def clasificar_motivo_negacion_anterior_exactos(df):
        motivos_validos = [
            "Negado por Evaluación de Scoring",
            "Negado por Políticas de Crédito",
            "Deudor Ubicador no cumple políticas",
            "No tiene documento de identificación o mal estado, permiso temporal, cedula de extranjería vencida.",
            "Alerta en la información de la actividad económica",
            "Zona de alto riesgo",
            "Cliente Negado en Menos de 30 días",
            "Deudor Requerido no cumple políticas",
            "Área de cobertura.",
            "Cliente no contestó en el horario indicado",
            "Cliente no tiene actividad económica",
            "No cumple políticas de Datacredito",
            "Moto y crédito serán para un tercero",
            "Negado por cobertura/zona de alto riesgo.",
            "Cliente no tiene número de celular propio.",
            "Deudor Pago Compartido no cumple políticas",
            "Cliente no tiene perfil Crediorbe - Revisar asesoría",
            "Dirección errada y no fue posible contactar al titular para su visita",
            "Fraude en documentos",
            "Suplantación de identidad"
        ]
        
        df["MOTIVO_NEGACION_ANTERIOR"] = df["MOTIVO_NEGACION_ANTERIOR"].where(
            df["MOTIVO_NEGACION_ANTERIOR"].isin(motivos_validos),
            other='Na'
        )
        
        return df


    #Funcion diferencia de meses 

def calcular_diferencia_meses(df):
        df['DIFERENCIA_meses_mail'] = (
            (df['SOLFECHAINICIO'].dt.year - df['ACTULIZACION_MAIL'].dt.year) * 12 +
            (df['SOLFECHAINICIO'].dt.month - df['ACTULIZACION_MAIL'].dt.month)
        )

        df['DIFERENCIA_meses_tel'] = (
            (df['SOLFECHAINICIO'].dt.year - df['ACTUALIZACION_TEL'].dt.year) * 12 +
            (df['SOLFECHAINICIO'].dt.month - df['ACTUALIZACION_TEL'].dt.month)
        )

        return df


def convertir_a_smlv(df, smmlv=1423500):
        df = df.copy()  # Evita modificar el original si no deseas efectos colaterales
        df['SMMLV'] = smmlv
        
        df['INGRESOS_CONSOLIDADO_smlv'] = round(df['INGRESOS_CONSOLIDADO'] / df['SMMLV'], 0)
        df['EGRESOS_CONSOLIDADO_smlv'] = round(df['EGRESOS_CONSOLIDADO'] / df['SMMLV'], 0)
        df['ENDEUDAMIENTO_SMLV'] = round(df['ENDEUDAMIENTO_AJUSTADO'] / df['SMMLV'], 0)
        
        return df



def imputar_diferencias_meses(df):
        df["DIFERENCIA_meses_mail"] = df["DIFERENCIA_meses_mail"].fillna(-1)
        df["DIFERENCIA_meses_tel"] = df["DIFERENCIA_meses_tel"].fillna(-1)
        df['ENDEUDAMIENTO_AJUSTADO'] = df['ENDEUDAMIENTO_AJUSTADO'].fillna(df['ENDEUDAMIENTO_AJUSTADO'].median())
        df['EGRESOS_CONSOLIDADO'] = df['EGRESOS_CONSOLIDADO'].fillna(df['EGRESOS_CONSOLIDADO'].median())
        df['MOTIVO_NEGACION_ANTERIOR'] = df['MOTIVO_NEGACION_ANTERIOR'].fillna('Na')
        return df


def obtener_variables_predictoras(df):
        columnas = [
            'COINCIDE_CEL_RECONOCER',
            'COINCIDE_EMAIL_RECONOCER',
            'CONTEO_TELEFONO_BASEFRAUDE',
            'OTRAS_SOLICITUDES',
            'CONTEO_TELEFONO_RECONOCER',
            'CONTEO_EMAIL_RECONOCER',
            'CANT_MORA30_ULT12MESES_HISTORICO',
            'CANT_MORA120_ULT12MESES_HISTORICO',
            'RESULTADO_SCORE',
            'PERSONAS_CARGO',
            'COINCIDE_DIRECCION',
            'COINCIDE_DEPARTAMENTO',
            'ZONA_COBERTURA_ALTO_RIESGO',
            'CANAL_ATENCION',
            'ZONA_DEALER',
            'MOTIVO_NEGACION_ANTERIOR',
            'DIFERENCIA_meses_mail',
            'DIFERENCIA_meses_tel',
            # 'INGRESOS_CONSOLIDADO_smlv',
            # 'EGRESOS_CONSOLIDADO_smlv',
            # 'ENDEUDAMIENTO_SMLV',
            'TIPO_SUBTIPO_CLIENTE',
            'producer_docs',
            'nitidez_docs_min',
            'max_dias_docs',
            'conteo_negadoIDVISION'
        ]
        
        return df[columnas].copy()


def construccion_indicadores(df):
            
            df_modelo = pd.DataFrame()
        
            df_modelo['COINCIDE_CEL_RECONOCER'] = df['COINCIDE_CEL_RECONOCER']
            df_modelo['COINCIDE_EMAIL_RECONOCER'] = df['COINCIDE_EMAIL_RECONOCER']
            df_modelo['COINCIDE_DIRECCION'] = df['COINCIDE_DIRECCION']
            df_modelo['COINCIDE_DEPARTAMENTO']= df['COINCIDE_DEPARTAMENTO']
            df_modelo['TIPO_SUBTIPO_CLIENTE_EMPLEADO_0'] = np.where(df['TIPO_SUBTIPO_CLIENTE'] == 'EMPLEADO_0',1,0)
            df_modelo['TIPO_SUBTIPO_CLIENTE_EMPLEADO_1'] = np.where(df['TIPO_SUBTIPO_CLIENTE'] == 'EMPLEADO_1',1,0)
            df_modelo['TIPO_SUBTIPO_CLIENTE_INDEP'] = np.where(df['TIPO_SUBTIPO_CLIENTE'] == 'INDEP',1,0)
            df_modelo['ZONA_COBERTURA_ALTO_RIESGO_No'] = np.where(df['ZONA_COBERTURA_ALTO_RIESGO'] == 'No',1,0)
            df_modelo['ZONA_COBERTURA_ALTO_RIESGO_Zona_Alto_Riesgo'] = np.where(df['ZONA_COBERTURA_ALTO_RIESGO'] == 'Zona_Alto_Riesgo',1,0)
            df_modelo['CANAL_ATENCION_Dealer'] = np.where(df['CANAL_ATENCION'] == 'Dealer',1,0)
            df_modelo['CANAL_ATENCION_Online']= np.where(df['CANAL_ATENCION'] == 'Online',1,0)
            df_modelo['ZONA_DEALER_ZONA ANTIOQUIA'] = np.where(df['ZONA_DEALER'] == 'ZONA ANTIOQUIA',1,0)
            df_modelo['ZONA_DEALER_ZONA BOGOTA'] = np.where(df['ZONA_DEALER'] == 'ZONA BOGOTA',1,0)
            df_modelo['ZONA_DEALER_ZONA CENTRO'] = np.where(df['ZONA_DEALER'] == 'ZONA CENTRO',1,0)
            df_modelo['ZONA_DEALER_ZONA COSTA'] = np.where(df['ZONA_DEALER'] == 'ZONA COSTA',1,0)
            df_modelo['ZONA_DEALER_ZONA EJE CAFETERO'] = np.where(df['ZONA_DEALER'] == 'ZONA EJE CAFETERO',1,0)
            df_modelo['ZONA_DEALER_ZONA ORIENTE'] = np.where(df['ZONA_DEALER'] == 'ZONA ORIENTE',1,0)
            df_modelo['ZONA_DEALER_ZONA SUROCCIDENTE'] = np.where(df['ZONA_DEALER'] == 'ZONA SUROCCIDENTE',1,0)
            
            df_modelo['MOTIVO_NEGACION_ANTERIOR_Alerta en la información de la actividad económica'] = np.where(df['MOTIVO_NEGACION_ANTERIOR'] == 'Alerta en la información de la actividad económica',1,0)
            df_modelo['MOTIVO_NEGACION_ANTERIOR_Cliente Negado en Menos de 30 días'] = np.where(df['MOTIVO_NEGACION_ANTERIOR'] == 'Cliente Negado en Menos de 30 días',1,0)
            df_modelo['MOTIVO_NEGACION_ANTERIOR_Cliente no contestó en el horario indicado'] = np.where(df['MOTIVO_NEGACION_ANTERIOR'] == 'Cliente no contestó en el horario indicado',1,0)
            df_modelo['MOTIVO_NEGACION_ANTERIOR_Cliente no tiene actividad económica'] = np.where(df['MOTIVO_NEGACION_ANTERIOR'] == 'Cliente no tiene actividad económica',1,0)
            df_modelo['MOTIVO_NEGACION_ANTERIOR_Cliente no tiene número de celular propio.'] = np.where(df['MOTIVO_NEGACION_ANTERIOR'] == 'Cliente no tiene número de celular propio.',1,0)
            df_modelo['MOTIVO_NEGACION_ANTERIOR_Cliente no tiene perfil Crediorbe - Revisar asesoría'] = np.where(df['MOTIVO_NEGACION_ANTERIOR'] == 'Cliente no tiene perfil Crediorbe - Revisar asesoría',1,0)
            df_modelo['MOTIVO_NEGACION_ANTERIOR_Deudor Pago Compartido no cumple políticas'] = np.where(df['MOTIVO_NEGACION_ANTERIOR'] == 'Deudor Pago Compartido no cumple políticas',1,0)
            df_modelo['MOTIVO_NEGACION_ANTERIOR_Deudor Requerido no cumple políticas'] = np.where(df['MOTIVO_NEGACION_ANTERIOR'] == 'Deudor Requerido no cumple políticas',1,0)
            df_modelo['MOTIVO_NEGACION_ANTERIOR_Deudor Ubicador no cumple políticas'] = np.where(df['MOTIVO_NEGACION_ANTERIOR'] == 'Deudor Ubicador no cumple políticas',1,0)
            df_modelo['MOTIVO_NEGACION_ANTERIOR_Dirección errada y no fue posible contactar al titular para su visita'] = np.where(df['MOTIVO_NEGACION_ANTERIOR'] == 'Dirección errada y no fue posible contactar al titular para su visita',1,0)
            df_modelo['MOTIVO_NEGACION_ANTERIOR_Fraude en documentos'] = np.where(df['MOTIVO_NEGACION_ANTERIOR'] == 'Fraude en documentos',1,0)
            df_modelo['MOTIVO_NEGACION_ANTERIOR_Moto y crédito serán para un tercero'] = np.where(df['MOTIVO_NEGACION_ANTERIOR'] == 'Moto y crédito serán para un tercero',1,0)
            df_modelo['MOTIVO_NEGACION_ANTERIOR_Na'] = np.where(df['MOTIVO_NEGACION_ANTERIOR'] == 'Na',1,0)
            df_modelo['MOTIVO_NEGACION_ANTERIOR_Negado por Evaluación de Scoring'] = np.where(df['MOTIVO_NEGACION_ANTERIOR'] == 'Negado por Evaluación de Scoring',1,0)
            df_modelo['MOTIVO_NEGACION_ANTERIOR_Negado por Políticas de Crédito'] = np.where(df['MOTIVO_NEGACION_ANTERIOR'] == 'Negado por Políticas de Crédito',1,0)
            df_modelo['MOTIVO_NEGACION_ANTERIOR_Negado por cobertura/zona de alto riesgo.'] = np.where(df['MOTIVO_NEGACION_ANTERIOR'] == 'Negado por cobertura/zona de alto riesgo.',1,0)
            df_modelo['MOTIVO_NEGACION_ANTERIOR_No cumple políticas de Datacredito'] = np.where(df['MOTIVO_NEGACION_ANTERIOR'] == 'No cumple políticas de Datacredito',1,0)
            df_modelo['MOTIVO_NEGACION_ANTERIOR_No tiene documento de identificación o mal estado, permiso temporal, cedula de extranjería vencida.'] = np.where(df['MOTIVO_NEGACION_ANTERIOR'] == 'No tiene documento de identificación o mal estado, permiso temporal, cedula de extranjería vencida.',1,0)
            df_modelo['MOTIVO_NEGACION_ANTERIOR_Suplantación de identidad'] = np.where(df['MOTIVO_NEGACION_ANTERIOR'] == 'Suplantación_de_identidad',1,0)
            df_modelo['MOTIVO_NEGACION_ANTERIOR_Zona de alto riesgo'] = np.where(df['MOTIVO_NEGACION_ANTERIOR'] == 'Zona_de_alto_riesgo',1,0)
            df_modelo['MOTIVO_NEGACION_ANTERIOR_Área de cobertura.'] = np.where(df['MOTIVO_NEGACION_ANTERIOR'] == 'Área_de_cobertura.',1,0)
            
            df_modelo['producer_docs_canva'] = np.where(df['producer_docs'] == 'canva',1,0)
            df_modelo['producer_docs_epson']= np.where(df['producer_docs'] == 'epson',1,0)
            df_modelo['producer_docs_ghostscript'] = np.where(df['producer_docs'] == 'ghostscript',1,0) 
            df_modelo['producer_docs_ilovepdf'] = np.where(df['producer_docs'] == 'ilovepdf',1,0)  
            df_modelo['producer_docs_intsig'] = np.where(df['producer_docs'] == 'intsig',1,0)   
            df_modelo['producer_docs_itext'] = np.where(df['producer_docs'] == 'itext',1,0)  
            df_modelo['producer_docs_microsoft_print'] = np.where(df['producer_docs'] == 'microsoft_print',1,0)   
            df_modelo['producer_docs_microsoft_word'] = np.where(df['producer_docs'] == 'microsoft_word',1,0)  
            df_modelo['producer_docs_otros'] = np.where(df['producer_docs'] == 'otros',1,0)
            df_modelo['producer_docs_pdfium'] = np.where(df['producer_docs'] == 'pdfium',1,0) 
            df_modelo['producer_docs_quartz'] = np.where(df['producer_docs'] == 'quartz',1,0) 
            df_modelo['producer_docs_skia'] = np.where(df['producer_docs'] == 'skia',1,0) 
                    
            df_modelo['CONTEO_TELEFONO_BASEFRAUDE'] = df['CONTEO_TELEFONO_BASEFRAUDE']
            df_modelo['OTRAS_SOLICITUDES'] = df['OTRAS_SOLICITUDES']
            df_modelo['CONTEO_TELEFONO_RECONOCER'] = df['CONTEO_TELEFONO_RECONOCER']
            df_modelo['CONTEO_EMAIL_RECONOCER'] = df['CONTEO_EMAIL_RECONOCER']
            df_modelo['CANT_MORA30_ULT12MESES_HISTORICO'] = df['CANT_MORA30_ULT12MESES_HISTORICO']
            df_modelo['CANT_MORA120_ULT12MESES_HISTORICO'] = df['CANT_MORA120_ULT12MESES_HISTORICO']       
            df_modelo['RESULTADO_SCORE'] = df['RESULTADO_SCORE']
            df_modelo['PERSONAS_CARGO'] = df['PERSONAS_CARGO']
            df_modelo['DIFERENCIA_meses_mail'] = df['DIFERENCIA_meses_mail']
            df_modelo['DIFERENCIA_meses_tel'] = df['DIFERENCIA_meses_tel']
            df_modelo['nitidez_docs_min'] = df['nitidez_docs_min']
            df_modelo['max_dias_docs'] = df['max_dias_docs']
            df_modelo['conteo_negadoIDVISION'] = df['conteo_negadoIDVISION']
            
            return df_modelo
        
        
import joblib
def predecir_con_dos_modelos(df_procesado):
        
        modelo1 = joblib.load('/Users/zulybercampos/Documents/co_fraudubot/Modelos_Entrenados/model_RF_27072025.pkl')
        modelo2 = joblib.load('/Users/zulybercampos/Documents/co_fraudubot/Modelos_Entrenados/model_RLR_27072025.pkl')
        peso_modelo1 = 0.4
        peso_modelo2 = 0.6
        
        # Verificar que los pesos sumen 1
        if not np.isclose(peso_modelo1 + peso_modelo2, 1.0):
            raise ValueError("Los pesos de los modelos deben sumar 1.")
        
        # Predecir probabilidades con ambos modelos (probabilidad clase 1)
        proba1 = modelo1.predict_proba(df_procesado)[:, 1]
        proba2 = modelo2.predict_proba(df_procesado)[:, 1]
        
        # Calcular probabilidad ponderada
        probabilidad_ponderada = (peso_modelo1 * proba1) + (peso_modelo2 * proba2)
        
        return probabilidad_ponderada

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer

##df = cargar_datos_desde_bd()

preprocesamiento = Pipeline([
        ('buscar_solicitud', FunctionTransformer(buscar_solicitud)),
        ('convertir_campos_numericos', FunctionTransformer(convertir_campos_numericos)),
        ('transformar_variables_credito', FunctionTransformer(transformar_variables_credito)),
        ('clasificar_motivo_negacion_anterior_exactos', FunctionTransformer(clasificar_motivo_negacion_anterior_exactos)),
        ('calcular_diferencia_meses', FunctionTransformer(calcular_diferencia_meses)),
        ('convertir_a_smlv', FunctionTransformer(convertir_a_smlv)),
        ('imputar_diferencias_meses', FunctionTransformer(imputar_diferencias_meses)),
        ('obtener_variables_predictoras', FunctionTransformer(obtener_variables_predictoras)),
        ('construccion_indicadores', FunctionTransformer(construccion_indicadores)),
        ('predecir_con_dos_modelos', FunctionTransformer(predecir_con_dos_modelos))
    ])

    ##df_procesado = preprocesamiento.transform(df)