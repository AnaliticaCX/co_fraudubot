"""
Utilidades para el análisis y gestión de logs de Gemini LLM.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import pandas as pd
from .gemini_logger import gemini_logger

def get_recent_logs(hours: int = 24, operation: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Obtiene logs recientes de las últimas N horas.
    
    Args:
        hours: Número de horas hacia atrás
        operation: Filtrar por operación específica
        
    Returns:
        Lista de logs recientes
    """
    end_date = datetime.now().isoformat()
    start_date = (datetime.now() - timedelta(hours=hours)).isoformat()
    
    return gemini_logger.get_logs(
        operation=operation,
        start_date=start_date,
        end_date=end_date,
        limit=1000
    )

def get_performance_summary(days: int = 7) -> Dict[str, Any]:
    """
    Obtiene un resumen de rendimiento de los últimos N días.
    
    Args:
        days: Número de días a analizar
        
    Returns:
        Diccionario con métricas de rendimiento
    """
    end_date = datetime.now().isoformat()
    start_date = (datetime.now() - timedelta(days=days)).isoformat()
    
    logs = gemini_logger.get_logs(
        start_date=start_date,
        end_date=end_date,
        limit=10000
    )
    
    if not logs:
        return {
            "total_requests": 0,
            "success_rate": 0,
            "average_response_time": 0,
            "operations_breakdown": {},
            "error_count": 0
        }
    
    # Calcular métricas
    total_requests = len(logs)
    successful_requests = len([log for log in logs if not log.get('error_message')])
    error_count = total_requests - successful_requests
    success_rate = (successful_requests / total_requests) * 100 if total_requests > 0 else 0
    
    execution_times = [log.get('execution_time', 0) for log in logs]
    avg_response_time = sum(execution_times) / len(execution_times) if execution_times else 0
    
    # Desglose por operaciones
    operations = {}
    for log in logs:
        op = log.get('operation', 'unknown')
        if op not in operations:
            operations[op] = {
                'count': 0,
                'success_count': 0,
                'avg_time': 0,
                'times': []
            }
        
        operations[op]['count'] += 1
        operations[op]['times'].append(log.get('execution_time', 0))
        
        if not log.get('error_message'):
            operations[op]['success_count'] += 1
    
    # Calcular promedios por operación
    for op in operations:
        times = operations[op]['times']
        operations[op]['avg_time'] = sum(times) / len(times) if times else 0
        operations[op]['success_rate'] = (operations[op]['success_count'] / operations[op]['count']) * 100
        del operations[op]['times']  # Limpiar datos temporales
    
    return {
        "total_requests": total_requests,
        "success_rate": success_rate,
        "average_response_time": avg_response_time,
        "operations_breakdown": operations,
        "error_count": error_count,
        "period_days": days
    }

def export_logs_analysis(output_file: str, days: int = 30) -> bool:
    """
    Exporta un análisis completo de logs a un archivo Excel.
    
    Args:
        output_file: Archivo de salida (.xlsx)
        days: Número de días a analizar
        
    Returns:
        True si la exportación fue exitosa
    """
    try:
        end_date = datetime.now().isoformat()
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        logs = gemini_logger.get_logs(
            start_date=start_date,
            end_date=end_date,
            limit=10000
        )
        
        if not logs:
            return False
        
        # Convertir a DataFrame
        df = pd.DataFrame(logs)
        
        # Crear Excel con múltiples hojas
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Hoja principal con todos los logs
            df.to_excel(writer, sheet_name='All_Logs', index=False)
            
            # Hoja con resumen por operación
            operation_summary = df.groupby('operation').agg({
                'execution_time': ['count', 'mean', 'min', 'max'],
                'error_message': lambda x: x.notna().sum()
            }).round(3)
            operation_summary.to_excel(writer, sheet_name='Operation_Summary')
            
            # Hoja con errores
            error_logs = df[df['error_message'].notna()]
            if not error_logs.empty:
                error_logs.to_excel(writer, sheet_name='Errors', index=False)
            
            # Hoja con métricas diarias
            df['date'] = pd.to_datetime(df['timestamp']).dt.date
            daily_metrics = df.groupby('date').agg({
                'execution_time': ['count', 'mean'],
                'error_message': lambda x: x.notna().sum()
            }).round(3)
            daily_metrics.to_excel(writer, sheet_name='Daily_Metrics')
        
        return True
        
    except Exception as e:
        print(f"Error al exportar análisis: {e}")
        return False

def get_error_analysis(limit: int = 100) -> Dict[str, Any]:
    """
    Analiza los errores más comunes en los logs.
    
    Args:
        limit: Número máximo de errores a analizar
        
    Returns:
        Diccionario con análisis de errores
    """
    error_logs = gemini_logger.get_error_logs(limit=limit)
    
    if not error_logs:
        return {
            "total_errors": 0,
            "error_types": {},
            "most_common_errors": [],
            "operations_with_errors": {}
        }
    
    # Analizar tipos de errores
    error_types = {}
    operations_with_errors = {}
    
    for log in error_logs:
        error_msg = log.get('error_message', 'Unknown error')
        operation = log.get('operation', 'unknown')
        
        # Contar tipos de errores
        if error_msg not in error_types:
            error_types[error_msg] = 0
        error_types[error_msg] += 1
        
        # Contar errores por operación
        if operation not in operations_with_errors:
            operations_with_errors[operation] = 0
        operations_with_errors[operation] += 1
    
    # Obtener errores más comunes
    most_common_errors = sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "total_errors": len(error_logs),
        "error_types": error_types,
        "most_common_errors": most_common_errors,
        "operations_with_errors": operations_with_errors
    }

def get_usage_trends(days: int = 30) -> Dict[str, Any]:
    """
    Analiza las tendencias de uso de Gemini.
    
    Args:
        days: Número de días a analizar
        
    Returns:
        Diccionario con tendencias de uso
    """
    end_date = datetime.now().isoformat()
    start_date = (datetime.now() - timedelta(days=days)).isoformat()
    
    logs = gemini_logger.get_logs(
        start_date=start_date,
        end_date=end_date,
        limit=10000
    )
    
    if not logs:
        return {
            "daily_usage": {},
            "hourly_pattern": {},
            "operation_trends": {},
            "response_time_trends": {}
        }
    
    # Convertir a DataFrame para análisis
    df = pd.DataFrame(logs)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date
    df['hour'] = df['timestamp'].dt.hour
    
    # Uso diario
    daily_usage = df.groupby('date').size().to_dict()
    
    # Patrón horario
    hourly_pattern = df.groupby('hour').size().to_dict()
    
    # Tendencias por operación
    operation_trends = df.groupby(['date', 'operation']).size().unstack(fill_value=0).to_dict()
    
    # Tendencias de tiempo de respuesta
    response_time_trends = df.groupby('date')['execution_time'].mean().to_dict()
    
    return {
        "daily_usage": daily_usage,
        "hourly_pattern": hourly_pattern,
        "operation_trends": operation_trends,
        "response_time_trends": response_time_trends
    }

def cleanup_old_logs(days: int = 30) -> int:
    """
    Limpia logs antiguos y retorna el número de logs eliminados.
    
    Args:
        days: Número de días a mantener
        
    Returns:
        Número de logs eliminados
    """
    return gemini_logger.clear_old_logs(days=days)

def get_log_statistics() -> Dict[str, Any]:
    """
    Obtiene estadísticas generales del sistema de logging.
    
    Returns:
        Diccionario con estadísticas
    """
    stats = gemini_logger.get_statistics()
    performance = gemini_logger.get_performance_metrics()
    
    return {
        "basic_stats": stats,
        "performance_metrics": performance,
        "recent_activity": get_recent_logs(hours=1),
        "error_summary": get_error_analysis(limit=50)
    } 