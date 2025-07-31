import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path
import hashlib
import time
from dataclasses import dataclass, asdict
from enum import Enum

class LogLevel(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    DEBUG = "DEBUG"

@dataclass
class GeminiLogEntry:
    """Estructura para almacenar información de logs de Gemini"""
    timestamp: str
    operation: str
    prompt: str
    response: str
    model_used: str
    execution_time: float
    tokens_used: Optional[int] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None

class GeminiLogger:
    """
    Sistema de logging para respuestas de Gemini LLM.
    
    Características:
    - Logging de requests y responses
    - Métricas de rendimiento
    - Manejo de errores
    - Rotación de logs
    - Exportación de logs
    - Análisis de uso
    """
    
    def __init__(self, log_dir: str = "logs/gemini", max_log_size_mb: int = 10, backup_count: int = 5):
        """
        Inicializa el logger de Gemini.
        
        Args:
            log_dir: Directorio donde se guardarán los logs
            max_log_size_mb: Tamaño máximo del archivo de log en MB
            backup_count: Número de archivos de backup a mantener
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar logging básico
        self.setup_logging()
        
        # Configuración de rotación
        self.max_log_size = max_log_size_mb * 1024 * 1024  # Convertir a bytes
        self.backup_count = backup_count
        
        # Cache para logs en memoria
        self.log_cache: List[GeminiLogEntry] = []
        self.max_cache_size = 100
        
        # Estadísticas
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_execution_time": 0.0,
            "average_execution_time": 0.0
        }
    
    def setup_logging(self):
        """Configura el sistema de logging básico"""
        log_file = self.log_dir / "gemini_operations.log"
        
        # Configurar formato del log
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Handler para archivo
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # Configurar logger
        self.logger = logging.getLogger('GeminiLogger')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def log_request(self, 
                    operation: str, 
                    prompt: str, 
                    response: str, 
                    model_used: str = "gemini-1.5-flash-002",
                    execution_time: float = 0.0,
                    tokens_used: Optional[int] = None,
                    error_message: Optional[str] = None,
                    metadata: Optional[Dict[str, Any]] = None,
                    session_id: Optional[str] = None,
                    user_id: Optional[str] = None) -> str:
        """
        Registra una interacción con Gemini.
        
        Args:
            operation: Tipo de operación (clasificar_documento, extraer_datos, etc.)
            prompt: Prompt enviado a Gemini
            response: Respuesta recibida de Gemini
            model_used: Modelo de Gemini utilizado
            execution_time: Tiempo de ejecución en segundos
            tokens_used: Número de tokens utilizados
            error_message: Mensaje de error si ocurrió alguno
            metadata: Metadatos adicionales
            session_id: ID de la sesión
            user_id: ID del usuario
            
        Returns:
            ID único del log entry
        """
        # Calcular tokens si no se pasan
        if tokens_used is None and hasattr(self, "modelo") and hasattr(self.modelo, "count_tokens"):
            try:
                tokens_used = self.modelo.count_tokens(prompt)
            except Exception as e:
                error_message = error_message or f"Error al contar tokens: {str(e)}"
                tokens_used = None

        # Crear entrada de log
        log_entry = GeminiLogEntry(
            timestamp=datetime.now().isoformat(),
            operation=operation,
            prompt=prompt,
            response=response,
            model_used=model_used,
            execution_time=execution_time,
            tokens_used=tokens_used,
            error_message=error_message,
            metadata=metadata or {},
            session_id=session_id,
            user_id=user_id
        )
        
        # Generar ID único
        log_id = self._generate_log_id(log_entry)
        
        # Actualizar estadísticas
        self._update_stats(log_entry)
        
        # Guardar en cache
        self._add_to_cache(log_entry)
        
        # Guardar en archivo JSON
        self._save_to_json(log_entry)
        
        # Log básico
        log_level = logging.ERROR if error_message else logging.INFO
        self.logger.log(log_level, f"Operation: {operation} | Time: {execution_time:.2f}s | Success: {error_message is None}")
        
        return log_id
    
    def _generate_log_id(self, log_entry: GeminiLogEntry) -> str:
        """Genera un ID único para el log entry"""
        content = f"{log_entry.timestamp}{log_entry.operation}{log_entry.prompt[:100]}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _update_stats(self, log_entry: GeminiLogEntry):
        """Actualiza las estadísticas de uso"""
        self.stats["total_requests"] += 1
        self.stats["total_execution_time"] += log_entry.execution_time
        
        if log_entry.error_message:
            self.stats["failed_requests"] += 1
        else:
            self.stats["successful_requests"] += 1
        
        # Calcular tiempo promedio
        if self.stats["total_requests"] > 0:
            self.stats["average_execution_time"] = (
                self.stats["total_execution_time"] / self.stats["total_requests"]
            )
    
    def _add_to_cache(self, log_entry: GeminiLogEntry):
        """Añade el log entry al cache en memoria"""
        self.log_cache.append(log_entry)
        
        # Mantener tamaño del cache
        if len(self.log_cache) > self.max_cache_size:
            self.log_cache.pop(0)
    
    def _save_to_json(self, log_entry: GeminiLogEntry):
        """Guarda el log entry en archivo JSON"""
        json_file = self.log_dir / "gemini_logs.json"
        
        # Crear o cargar logs existentes
        if json_file.exists():
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                logs = []
        else:
            logs = []
        
        # Añadir nuevo log
        logs.append(asdict(log_entry))
        
        # Guardar
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    
    def get_logs(self, 
                 operation: Optional[str] = None,
                 start_date: Optional[str] = None,
                 end_date: Optional[str] = None,
                 limit: int = 100) -> List[Dict[str, Any]]:
        """
        Obtiene logs filtrados.
        
        Args:
            operation: Filtrar por operación
            start_date: Fecha de inicio (ISO format)
            end_date: Fecha de fin (ISO format)
            limit: Límite de resultados
            
        Returns:
            Lista de logs filtrados
        """
        json_file = self.log_dir / "gemini_logs.json"
        
        if not json_file.exists():
            return []
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
        
        # Aplicar filtros
        filtered_logs = []
        
        for log in logs:
            # Filtro por operación
            if operation and log.get('operation') != operation:
                continue
            
            # Filtro por fecha
            if start_date and log.get('timestamp', '') < start_date:
                continue
            
            if end_date and log.get('timestamp', '') > end_date:
                continue
            
            filtered_logs.append(log)
        
        # Aplicar límite y ordenar por timestamp
        filtered_logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return filtered_logs[:limit]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de uso"""
        return self.stats.copy()
    
    def export_logs(self, 
                   output_file: str,
                   format: str = "json",
                   operation: Optional[str] = None,
                   start_date: Optional[str] = None,
                   end_date: Optional[str] = None) -> bool:
        """
        Exporta logs a un archivo.
        
        Args:
            output_file: Archivo de salida
            format: Formato de exportación (json, csv)
            operation: Filtrar por operación
            start_date: Fecha de inicio
            end_date: Fecha de fin
            
        Returns:
            True si la exportación fue exitosa
        """
        try:
            logs = self.get_logs(operation, start_date, end_date, limit=10000)
            
            if format.lower() == "json":
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(logs, f, indent=2, ensure_ascii=False)
            
            elif format.lower() == "csv":
                import csv
                if logs:
                    with open(output_file, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=logs[0].keys())
                        writer.writeheader()
                        writer.writerows(logs)
            
            self.logger.info(f"Logs exportados exitosamente a {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al exportar logs: {e}")
            return False
    
    def clear_old_logs(self, days: int = 30) -> int:
        """
        Elimina logs más antiguos que el número de días especificado.
        
        Args:
            days: Número de días a mantener
            
        Returns:
            Número de logs eliminados
        """
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        json_file = self.log_dir / "gemini_logs.json"
        
        if not json_file.exists():
            return 0
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            original_count = len(logs)
            logs = [log for log in logs if log.get('timestamp', '') >= cutoff_date]
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
            
            deleted_count = original_count - len(logs)
            self.logger.info(f"Eliminados {deleted_count} logs antiguos")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Error al limpiar logs antiguos: {e}")
            return 0
    
    def get_error_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Obtiene logs de errores"""
        json_file = self.log_dir / "gemini_logs.json"
        
        if not json_file.exists():
            return []
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            error_logs = [log for log in logs if log.get('error_message')]
            error_logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            return error_logs[:limit]
            
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas de rendimiento"""
        logs = self.get_logs(limit=1000)
        
        if not logs:
            return {}
        
        execution_times = [log.get('execution_time', 0) for log in logs]
        
        return {
            "total_requests": len(logs),
            "average_execution_time": sum(execution_times) / len(execution_times),
            "min_execution_time": min(execution_times),
            "max_execution_time": max(execution_times),
            "success_rate": len([log for log in logs if not log.get('error_message')]) / len(logs) * 100
        }

# Instancia global del logger
gemini_logger = GeminiLogger()

# Decorador para logging automático
def log_gemini_operation(operation_name: str):
    """
    Decorador para logging automático de operaciones de Gemini.
    
    Args:
        operation_name: Nombre de la operación a loggear
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            error_message = None
            response = None
            
            try:
                # Ejecutar la función
                response = func(*args, **kwargs)
                return response
                
            except Exception as e:
                error_message = str(e)
                raise
                
            finally:
                # Loggear la operación
                execution_time = time.time() - start_time
                
                # Extraer prompt y response de los argumentos
                prompt = ""
                if args and isinstance(args[0], str):
                    prompt = args[0]
                elif 'texto' in kwargs:
                    prompt = kwargs['texto']
                elif 'prompt' in kwargs:
                    prompt = kwargs['prompt']
                
                if response is None:
                    response = ""
                
                gemini_logger.log_request(
                    operation=operation_name,
                    prompt=prompt,
                    response=str(response),
                    execution_time=execution_time,
                    error_message=error_message
                )
        
        return wrapper
    return decorator 