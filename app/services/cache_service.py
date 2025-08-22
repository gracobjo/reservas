from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import json
import hashlib
import threading
import time

class CacheService:
    """Servicio de cache en memoria para métricas y datos frecuentes"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._locks: Dict[str, threading.Lock] = {}
        self._cleanup_thread = None
        self._running = False
        self._start_cleanup_thread()
    
    def _start_cleanup_thread(self):
        """Iniciar thread de limpieza automática del cache"""
        if not self._running:
            self._running = True
            self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
            self._cleanup_thread.start()
    
    def _cleanup_loop(self):
        """Loop de limpieza automática del cache"""
        while self._running:
            try:
                self._cleanup_expired()
                time.sleep(60)  # Limpiar cada minuto
            except Exception as e:
                print(f"Error en limpieza de cache: {e}")
                time.sleep(300)  # Esperar 5 minutos si hay error
    
    def _cleanup_expired(self):
        """Limpiar entradas expiradas del cache"""
        now = datetime.now()
        expired_keys = []
        
        for key, data in self._cache.items():
            if 'expires_at' in data and data['expires_at'] < now:
                expired_keys.append(key)
        
        for key in expired_keys:
            self._cache.pop(key, None)
            self._locks.pop(key, None)
    
    def _generate_key(self, prefix: str, **kwargs) -> str:
        """Generar clave única para el cache"""
        # Ordenar kwargs para consistencia
        sorted_kwargs = sorted(kwargs.items())
        key_string = f"{prefix}:{json.dumps(sorted_kwargs, sort_keys=True)}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, prefix: str, **kwargs) -> Optional[Any]:
        """Obtener valor del cache"""
        key = self._generate_key(prefix, **kwargs)
        
        if key in self._cache:
            data = self._cache[key]
            if 'expires_at' not in data or data['expires_at'] > datetime.now():
                return data['value']
            else:
                # Expiró, remover
                self._cache.pop(key, None)
                self._locks.pop(key, None)
        
        return None
    
    def set(self, prefix: str, value: Any, ttl_seconds: int = 300, **kwargs) -> str:
        """Establecer valor en el cache con TTL"""
        key = self._generate_key(prefix, **kwargs)
        
        # Crear lock si no existe
        if key not in self._locks:
            self._locks[key] = threading.Lock()
        
        with self._locks[key]:
            self._cache[key] = {
                'value': value,
                'created_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(seconds=ttl_seconds),
                'ttl': ttl_seconds,
                'access_count': 0
            }
        
        return key
    
    def get_or_set(self, prefix: str, default_func, ttl_seconds: int = 300, **kwargs) -> Any:
        """Obtener del cache o establecer usando función por defecto"""
        key = self._generate_key(prefix, **kwargs)
        
        # Intentar obtener del cache
        cached_value = self.get(prefix, **kwargs)
        if cached_value is not None:
            # Incrementar contador de accesos
            if key in self._cache:
                self._cache[key]['access_count'] += 1
            return cached_value
        
        # Crear lock si no existe
        if key not in self._locks:
            self._locks[key] = threading.Lock()
        
        with self._locks[key]:
            # Verificar nuevamente (double-checked locking)
            cached_value = self.get(prefix, **kwargs)
            if cached_value is not None:
                return cached_value
            
            # Generar valor por defecto
            try:
                value = default_func()
                self.set(prefix, value, ttl_seconds, **kwargs)
                return value
            except Exception as e:
                print(f"Error generando valor por defecto para cache: {e}")
                return None
    
    def invalidate(self, prefix: str, **kwargs) -> bool:
        """Invalidar entrada específica del cache"""
        key = self._generate_key(prefix, **kwargs)
        
        if key in self._cache:
            self._cache.pop(key, None)
            self._locks.pop(key, None)
            return True
        
        return False
    
    def invalidate_pattern(self, prefix: str) -> int:
        """Invalidar todas las entradas que coincidan con un prefijo"""
        keys_to_remove = []
        
        for key in self._cache.keys():
            if key.startswith(prefix):
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            self._cache.pop(key, None)
            self._locks.pop(key, None)
        
        return len(keys_to_remove)
    
    def clear(self):
        """Limpiar todo el cache"""
        self._cache.clear()
        self._locks.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del cache"""
        now = datetime.now()
        total_entries = len(self._cache)
        expired_entries = 0
        total_access_count = 0
        memory_usage = 0
        
        for data in self._cache.values():
            if 'expires_at' in data and data['expires_at'] < now:
                expired_entries += 1
            
            if 'access_count' in data:
                total_access_count += data['access_count']
            
            # Estimación simple del uso de memoria
            memory_usage += len(str(data))
        
        return {
            'total_entries': total_entries,
            'expired_entries': expired_entries,
            'active_entries': total_entries - expired_entries,
            'total_access_count': total_access_count,
            'estimated_memory_bytes': memory_usage,
            'locks_count': len(self._locks),
            'timestamp': now.isoformat()
        }
    
    def get_entry_info(self, prefix: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Obtener información detallada de una entrada específica"""
        key = self._generate_key(prefix, **kwargs)
        
        if key in self._cache:
            data = self._cache[key]
            now = datetime.now()
            
            return {
                'key': key,
                'value_type': type(data['value']).__name__,
                'created_at': data['created_at'].isoformat(),
                'expires_at': data['expires_at'].isoformat() if 'expires_at' in data else None,
                'ttl_seconds': data.get('ttl', 0),
                'access_count': data.get('access_count', 0),
                'is_expired': 'expires_at' in data and data['expires_at'] < now,
                'time_until_expiry': (data['expires_at'] - now).total_seconds() if 'expires_at' in data and data['expires_at'] > now else 0
            }
        
        return None

# Instancia global del cache
cache_service = CacheService()

class CacheDecorator:
    """Decorador para cachear métodos de servicios"""
    
    def __init__(self, prefix: str, ttl_seconds: int = 300):
        self.prefix = prefix
        self.ttl_seconds = ttl_seconds
    
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            # Filtrar argumentos que no son serializables
            cache_kwargs = {}
            for key, value in kwargs.items():
                if isinstance(value, (int, float, str, bool)):
                    cache_kwargs[key] = value
            
            # Intentar obtener del cache
            cached_result = cache_service.get(self.prefix, **cache_kwargs)
            if cached_result is not None:
                return cached_result
            
            # Ejecutar función y cachear resultado
            result = func(*args, **kwargs)
            cache_service.set(self.prefix, result, self.ttl_seconds, **cache_kwargs)
            
            return result
        
        return wrapper

# Decoradores predefinidos para casos comunes
cache_metricas_tiempo_real = CacheDecorator("metricas_tiempo_real", 60)  # 1 minuto
cache_estadisticas_periodo = CacheDecorator("estadisticas_periodo", 300)  # 5 minutos
cache_predicciones = CacheDecorator("predicciones", 1800)  # 30 minutos
cache_listado_reservas = CacheDecorator("listado_reservas", 120)  # 2 minutos

