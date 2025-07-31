# Sistema de Logging de Gemini LLM

Este sistema proporciona un logging completo y detallado de todas las interacciones con el modelo Gemini LLM en la aplicación Fraudubot.

## 📁 Archivos del Sistema

- `gemini_logger.py` - Sistema principal de logging
- `gemini_log_utils.py` - Utilidades para análisis de logs
- `example_gemini_logging.py` - Ejemplos de uso

## 🚀 Características Principales

### ✅ Logging Automático
- **Decoradores**: Usa `@log_gemini_operation()` para logging automático
- **Integración**: Automáticamente integrado con `GeminiService` y `ModeloIA`
- **Métricas**: Tiempo de ejecución, tokens utilizados, errores

### 📊 Análisis de Datos
- **Estadísticas**: Requests totales, tasa de éxito, tiempo promedio
- **Filtros**: Por operación, fecha, errores
- **Exportación**: Excel con múltiples hojas de análisis

### 🔧 Gestión de Logs
- **Rotación**: Limpieza automática de logs antiguos
- **Cache**: Almacenamiento en memoria para acceso rápido
- **Backup**: Múltiples archivos de respaldo

## 📋 Estructura de Logs

Cada entrada de log contiene:

```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "operation": "clasificar_documento",
  "prompt": "Prompt enviado a Gemini",
  "response": "Respuesta de Gemini",
  "model_used": "gemini-1.5-flash-002",
  "execution_time": 1.25,
  "tokens_used": 150,
  "error_message": null,
  "metadata": {
    "texto_original": "Texto procesado...",
    "json_parsing_success": true
  },
  "session_id": "session_123",
  "user_id": "user_456"
}
```

## 🛠️ Uso Básico

### 1. Logging Manual

```python
from libreria.gemini_logger import gemini_logger

# Log manual
log_id = gemini_logger.log_request(
    operation="mi_operacion",
    prompt="Mi prompt",
    response="Respuesta de Gemini",
    execution_time=1.5,
    metadata={"datos_adicionales": "valor"}
)
```

### 2. Logging Automático con Decorador

```python
from libreria.gemini_logger import log_gemini_operation

@log_gemini_operation("mi_funcion")
def mi_funcion_con_gemini(texto):
    # Tu código aquí
    response = gemini_service.procesar(texto)
    return response
```

### 3. Análisis de Logs

```python
from libreria.gemini_log_utils import get_recent_logs, get_performance_summary

# Logs recientes
logs = get_recent_logs(hours=24, operation="clasificar_documento")

# Resumen de rendimiento
performance = get_performance_summary(days=7)
print(f"Tasa de éxito: {performance['success_rate']:.1f}%")
```

## 📈 Funciones de Análisis

### Obtener Logs Filtrados
```python
# Logs de las últimas 24 horas
logs = get_recent_logs(hours=24)

# Logs de una operación específica
logs = get_recent_logs(operation="extraer_datos_carta_laboral")

# Logs por rango de fechas
logs = gemini_logger.get_logs(
    start_date="2024-01-01T00:00:00",
    end_date="2024-01-31T23:59:59"
)
```

### Análisis de Rendimiento
```python
# Resumen de 7 días
performance = get_performance_summary(days=7)

# Métricas incluyen:
# - total_requests: Total de requests
# - success_rate: Tasa de éxito (%)
# - average_response_time: Tiempo promedio (s)
# - operations_breakdown: Desglose por operación
# - error_count: Número de errores
```

### Análisis de Errores
```python
# Errores más comunes
error_analysis = get_error_analysis(limit=50)

# Incluye:
# - total_errors: Total de errores
# - error_types: Tipos de errores
# - most_common_errors: Errores más frecuentes
# - operations_with_errors: Operaciones con errores
```

### Tendencias de Uso
```python
# Análisis de tendencias
trends = get_usage_trends(days=30)

# Incluye:
# - daily_usage: Uso diario
# - hourly_pattern: Patrón horario
# - operation_trends: Tendencias por operación
# - response_time_trends: Tendencias de tiempo de respuesta
```

## 📊 Exportación de Datos

### Exportar a Excel
```python
# Exportar análisis completo
success = export_logs_analysis("mi_analisis.xlsx", days=30)

# El archivo Excel contiene:
# - All_Logs: Todos los logs
# - Operation_Summary: Resumen por operación
# - Errors: Logs con errores
# - Daily_Metrics: Métricas diarias
```

### Exportar a JSON/CSV
```python
# Exportar logs filtrados
gemini_logger.export_logs(
    output_file="logs_export.json",
    format="json",
    operation="clasificar_documento",
    start_date="2024-01-01T00:00:00"
)
```

## 🔧 Gestión de Logs

### Limpiar Logs Antiguos
```python
# Eliminar logs de más de 30 días
deleted_count = cleanup_old_logs(days=30)
print(f"Eliminados {deleted_count} logs antiguos")
```

### Obtener Estadísticas
```python
# Estadísticas generales
stats = gemini_logger.get_statistics()
print(f"Total requests: {stats['total_requests']}")

# Métricas de rendimiento
metrics = gemini_logger.get_performance_metrics()
print(f"Tiempo promedio: {metrics['average_execution_time']:.2f}s")
```

## 📁 Estructura de Archivos

```
logs/gemini/
├── gemini_operations.log    # Logs básicos
├── gemini_logs.json        # Logs detallados
└── gemini_logs_analysis.xlsx # Análisis exportado
```

## ⚙️ Configuración

### Configuración del Logger
```python
# Configuración personalizada
logger = GeminiLogger(
    log_dir="mi_directorio_logs",
    max_log_size_mb=20,
    backup_count=10
)
```

### Configuración de Cache
```python
# El cache se configura automáticamente
# Tamaño máximo: 100 entradas
# Se limpia automáticamente cuando se excede
```

## 🚨 Manejo de Errores

El sistema maneja automáticamente:
- **Errores de API**: Timeouts, rate limits, etc.
- **Errores de parsing**: JSON inválido, respuestas malformadas
- **Errores de archivo**: Problemas de escritura/lectura
- **Errores de memoria**: Cache overflow

## 📝 Ejemplos Prácticos

### Ejecutar Ejemplos
```bash
python example_gemini_logging.py
```

### Integración con Streamlit
```python
# En tu aplicación Streamlit
import streamlit as st
from libreria.gemini_log_utils import get_performance_summary

# Mostrar métricas en tiempo real
if st.button("Ver Métricas"):
    performance = get_performance_summary(days=7)
    st.metric("Tasa de Éxito", f"{performance['success_rate']:.1f}%")
    st.metric("Tiempo Promedio", f"{performance['average_response_time']:.2f}s")
```

### Monitoreo en Tiempo Real
```python
# Verificar logs recientes
recent_logs = get_recent_logs(hours=1)
if recent_logs:
    print(f"Actividad reciente: {len(recent_logs)} requests")
    
    # Verificar errores
    errors = [log for log in recent_logs if log.get('error_message')]
    if errors:
        print(f"⚠️ Errores detectados: {len(errors)}")
```

## 🔍 Troubleshooting

### Problemas Comunes

1. **No se crean logs**
   - Verificar permisos de escritura en el directorio
   - Verificar que el directorio `logs/gemini/` existe

2. **Logs muy grandes**
   - Configurar rotación automática
   - Usar `cleanup_old_logs()` regularmente

3. **Rendimiento lento**
   - Reducir tamaño del cache
   - Limpiar logs antiguos
   - Usar filtros en consultas

### Debugging
```python
# Habilitar logging detallado
import logging
logging.getLogger('GeminiLogger').setLevel(logging.DEBUG)

# Verificar estado del logger
stats = gemini_logger.get_statistics()
print(f"Estado del logger: {stats}")
```

## 📚 Referencias

- [Google Generative AI Python SDK](https://ai.google.dev/tutorials/python_quickstart)
- [Python Logging](https://docs.python.org/3/library/logging.html)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

## 🤝 Contribución

Para contribuir al sistema de logging:

1. Mantener compatibilidad con la API existente
2. Añadir tests para nuevas funcionalidades
3. Documentar cambios en este README
4. Seguir las convenciones de código existentes

---

**Nota**: Este sistema está diseñado para ser no-intrusivo y de alto rendimiento. Los logs se guardan de forma asíncrona para no afectar el rendimiento de la aplicación principal. 