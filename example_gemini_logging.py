#!/usr/bin/env python3
"""
Ejemplo de uso del sistema de logging de Gemini LLM.

Este script demuestra cómo usar el sistema de logging para rastrear
las interacciones con Gemini y analizar el rendimiento.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from libreria.gemini_logger import gemini_logger
from libreria.gemini_log_utils import (
    get_recent_logs, 
    get_performance_summary, 
    get_error_analysis,
    export_logs_analysis,
    get_usage_trends
)
from libreria.germini_service import GeminiService

def example_basic_logging():
    """Ejemplo básico de logging manual"""
    print("=== Ejemplo de Logging Básico ===")
    
    # Log manual de una operación
    log_id = gemini_logger.log_request(
        operation="ejemplo_manual",
        prompt="Este es un prompt de ejemplo",
        response="Esta es una respuesta de ejemplo",
        execution_time=1.5,
        metadata={"ejemplo": True, "usuario": "demo"}
    )
    
    print(f"Log creado con ID: {log_id}")
    print()

def example_service_integration():
    """Ejemplo de integración con GeminiService"""
    print("=== Ejemplo de Integración con GeminiService ===")
    
    # Nota: Necesitas una API key válida para esto
    try:
        # Inicializar servicio (reemplaza con tu API key)
        api_key = "TU_API_KEY_AQUI"  # Reemplaza con tu API key real
        gemini_service = GeminiService(api_key)
        
        # Ejemplo de clasificación de documento
        texto_ejemplo = """
        CERTIFICADO LABORAL
        
        Por medio del presente se certifica que el señor Juan Pérez
        identificado con cédula de ciudadanía No. 12345678, labora en
        nuestra empresa desde el 15 de enero de 2020 en el cargo de
        Ingeniero de Sistemas con un salario mensual de $3,500,000.
        
        Esta certificación se expide a solicitud del interesado.
        """
        
        print("Clasificando documento...")
        tipo_documento = gemini_service.clasificar_documento(texto_ejemplo)
        print(f"Tipo de documento detectado: {tipo_documento}")
        
    except Exception as e:
        print(f"Error al usar GeminiService: {e}")
        print("(Esto es normal si no tienes una API key configurada)")
    
    print()

def example_log_analysis():
    """Ejemplo de análisis de logs"""
    print("=== Ejemplo de Análisis de Logs ===")
    
    # Obtener logs recientes
    recent_logs = get_recent_logs(hours=24)
    print(f"Logs en las últimas 24 horas: {len(recent_logs)}")
    
    # Obtener resumen de rendimiento
    performance = get_performance_summary(days=7)
    print(f"Resumen de rendimiento (7 días):")
    print(f"  - Total de requests: {performance['total_requests']}")
    print(f"  - Tasa de éxito: {performance['success_rate']:.1f}%")
    print(f"  - Tiempo promedio de respuesta: {performance['average_response_time']:.2f}s")
    
    # Análisis de errores
    error_analysis = get_error_analysis(limit=10)
    print(f"Análisis de errores:")
    print(f"  - Total de errores: {error_analysis['total_errors']}")
    
    if error_analysis['most_common_errors']:
        print("  - Errores más comunes:")
        for error, count in error_analysis['most_common_errors'][:3]:
            print(f"    * {error}: {count} veces")
    
    print()

def example_export_logs():
    """Ejemplo de exportación de logs"""
    print("=== Ejemplo de Exportación de Logs ===")
    
    # Exportar análisis a Excel
    output_file = "gemini_logs_analysis.xlsx"
    success = export_logs_analysis(output_file, days=30)
    
    if success:
        print(f"Análisis exportado exitosamente a: {output_file}")
        print("El archivo contiene:")
        print("  - All_Logs: Todos los logs")
        print("  - Operation_Summary: Resumen por operación")
        print("  - Errors: Logs con errores")
        print("  - Daily_Metrics: Métricas diarias")
    else:
        print("No se pudieron exportar los logs (posiblemente no hay datos)")
    
    print()

def example_usage_trends():
    """Ejemplo de análisis de tendencias de uso"""
    print("=== Ejemplo de Análisis de Tendencias ===")
    
    trends = get_usage_trends(days=7)
    
    print("Tendencias de uso (7 días):")
    print(f"  - Uso diario: {len(trends['daily_usage'])} días con actividad")
    print(f"  - Patrón horario: {len(trends['hourly_pattern'])} horas con actividad")
    
    if trends['daily_usage']:
        max_day = max(trends['daily_usage'].items(), key=lambda x: x[1])
        print(f"  - Día más activo: {max_day[0]} con {max_day[1]} requests")
    
    print()

def example_log_management():
    """Ejemplo de gestión de logs"""
    print("=== Ejemplo de Gestión de Logs ===")
    
    # Obtener estadísticas generales
    stats = gemini_logger.get_statistics()
    print("Estadísticas del sistema de logging:")
    print(f"  - Total de requests: {stats['total_requests']}")
    print(f"  - Requests exitosos: {stats['successful_requests']}")
    print(f"  - Requests fallidos: {stats['failed_requests']}")
    print(f"  - Tiempo promedio: {stats['average_execution_time']:.2f}s")
    
    # Limpiar logs antiguos (comentado para seguridad)
    # deleted_count = cleanup_old_logs(days=30)
    # print(f"Logs eliminados (más de 30 días): {deleted_count}")
    
    print()

def main():
    """Función principal que ejecuta todos los ejemplos"""
    print("🚀 Sistema de Logging de Gemini LLM - Ejemplos de Uso")
    print("=" * 60)
    
    # Ejecutar ejemplos
    example_basic_logging()
    example_service_integration()
    example_log_analysis()
    example_export_logs()
    example_usage_trends()
    example_log_management()
    
    print("✅ Todos los ejemplos completados.")
    print("\n📁 Los logs se guardan en: logs/gemini/")
    print("📊 Archivos generados:")
    print("  - gemini_operations.log: Logs básicos")
    print("  - gemini_logs.json: Logs detallados en JSON")
    print("  - gemini_logs_analysis.xlsx: Análisis exportado")

if __name__ == "__main__":
    main() 