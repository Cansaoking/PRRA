"""
Módulo para limpieza de cache y archivos temporales
"""
import os
import shutil
from pathlib import Path
from typing import List


class CacheManager:
    """Gestiona la limpieza de cache y archivos temporales"""
    
    @staticmethod
    def get_cache_directories() -> List[Path]:
        """
        Retorna lista de directorios de cache que pueden ser limpiados
        
        Returns:
            Lista de rutas Path a directorios de cache
        """
        home = Path.home()
        cache_dirs = []
        
        # Cache de HuggingFace (modelos de transformers)
        hf_cache = home / '.cache' / 'huggingface'
        if hf_cache.exists():
            cache_dirs.append(hf_cache)
        
        # Cache de Torch
        torch_cache = home / '.cache' / 'torch'
        if torch_cache.exists():
            cache_dirs.append(torch_cache)
        
        return cache_dirs
    
    @staticmethod
    def get_pycache_directories(base_path: Path) -> List[Path]:
        """
        Encuentra todos los directorios __pycache__ en la aplicación
        
        Args:
            base_path: Ruta base de la aplicación
            
        Returns:
            Lista de rutas Path a directorios __pycache__
        """
        pycache_dirs = []
        
        if base_path.exists():
            for root, dirs, files in os.walk(base_path):
                if '__pycache__' in dirs:
                    pycache_dirs.append(Path(root) / '__pycache__')
        
        return pycache_dirs
    
    @staticmethod
    def calculate_cache_size(directories: List[Path]) -> int:
        """
        Calcula el tamaño total de los directorios de cache
        
        Args:
            directories: Lista de directorios a calcular
            
        Returns:
            Tamaño total en bytes
        """
        total_size = 0
        
        for directory in directories:
            if directory.exists():
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        try:
                            file_path = Path(root) / file
                            total_size += file_path.stat().st_size
                        except (OSError, FileNotFoundError):
                            continue
        
        return total_size
    
    @staticmethod
    def format_size(size_bytes: int) -> str:
        """
        Formatea el tamaño en bytes a formato legible
        
        Args:
            size_bytes: Tamaño en bytes
            
        Returns:
            String formateado (e.g., "1.5 GB", "245 MB")
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    @staticmethod
    def clean_cache(
        clean_models: bool = True,
        clean_pycache: bool = True,
        base_path: Path = None
    ) -> dict:
        """
        Limpia los archivos de cache
        
        Args:
            clean_models: Si limpiar cache de modelos (HuggingFace, Torch)
            clean_pycache: Si limpiar archivos __pycache__
            base_path: Ruta base de la aplicación para limpiar __pycache__
            
        Returns:
            Diccionario con información de la limpieza
        """
        results = {
            'success': True,
            'errors': [],
            'cleaned': [],
            'size_freed': 0
        }
        
        # Limpiar cache de modelos
        if clean_models:
            cache_dirs = CacheManager.get_cache_directories()
            for cache_dir in cache_dirs:
                try:
                    # Calcular tamaño antes de borrar
                    size_before = CacheManager.calculate_cache_size([cache_dir])
                    
                    # Eliminar directorio
                    shutil.rmtree(cache_dir)
                    
                    results['cleaned'].append(str(cache_dir))
                    results['size_freed'] += size_before
                    
                except Exception as e:
                    results['errors'].append(f"Error cleaning {cache_dir}: {str(e)}")
                    results['success'] = False
        
        # Limpiar __pycache__
        if clean_pycache and base_path:
            pycache_dirs = CacheManager.get_pycache_directories(base_path)
            for pycache_dir in pycache_dirs:
                try:
                    # Calcular tamaño antes de borrar
                    size_before = CacheManager.calculate_cache_size([pycache_dir])
                    
                    # Eliminar directorio
                    shutil.rmtree(pycache_dir)
                    
                    results['cleaned'].append(str(pycache_dir))
                    results['size_freed'] += size_before
                    
                except Exception as e:
                    results['errors'].append(f"Error cleaning {pycache_dir}: {str(e)}")
                    # No marcar como fallo total si solo falla __pycache__
        
        return results
    
    @staticmethod
    def get_cache_info(base_path: Path = None) -> dict:
        """
        Obtiene información sobre el cache actual
        
        Args:
            base_path: Ruta base de la aplicación
            
        Returns:
            Diccionario con información del cache
        """
        info = {
            'model_cache': [],
            'pycache': [],
            'total_size': 0
        }
        
        # Información de cache de modelos
        cache_dirs = CacheManager.get_cache_directories()
        for cache_dir in cache_dirs:
            size = CacheManager.calculate_cache_size([cache_dir])
            info['model_cache'].append({
                'path': str(cache_dir),
                'size': size,
                'size_str': CacheManager.format_size(size)
            })
            info['total_size'] += size
        
        # Información de __pycache__
        if base_path:
            pycache_dirs = CacheManager.get_pycache_directories(base_path)
            for pycache_dir in pycache_dirs:
                size = CacheManager.calculate_cache_size([pycache_dir])
                info['pycache'].append({
                    'path': str(pycache_dir),
                    'size': size,
                    'size_str': CacheManager.format_size(size)
                })
                info['total_size'] += size
        
        info['total_size_str'] = CacheManager.format_size(info['total_size'])
        
        return info
