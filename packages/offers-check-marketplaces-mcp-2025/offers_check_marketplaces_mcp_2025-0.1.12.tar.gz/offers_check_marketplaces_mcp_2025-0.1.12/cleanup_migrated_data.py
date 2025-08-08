#!/usr/bin/env python3
"""
Скрипт для очистки папок data.migrated.* созданных при миграции данных.
Эти папки создаются автоматически при каждом запуске системы проверки лицензий.
"""

import os
import shutil
from pathlib import Path
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def cleanup_migrated_directories():
    """Удаляет все папки data.migrated.* в текущей директории."""
    current_dir = Path('.')
    migrated_dirs = []
    
    # Находим все папки data.migrated.*
    for item in current_dir.iterdir():
        if item.is_dir() and item.name.startswith('data.migrated'):
            migrated_dirs.append(item)
    
    if not migrated_dirs:
        logger.info("Папки data.migrated.* не найдены")
        return
    
    logger.info(f"Найдено {len(migrated_dirs)} папок для удаления:")
    for dir_path in migrated_dirs:
        logger.info(f"  - {dir_path}")
    
    # Запрашиваем подтверждение
    try:
        response = input("\nУдалить эти папки? (y/N): ").strip().lower()
        if response not in ['y', 'yes', 'да']:
            logger.info("Операция отменена")
            return
    except KeyboardInterrupt:
        logger.info("\nОперация отменена")
        return
    
    # Удаляем папки
    deleted_count = 0
    for dir_path in migrated_dirs:
        try:
            shutil.rmtree(dir_path)
            logger.info(f"✓ Удалена: {dir_path}")
            deleted_count += 1
        except Exception as e:
            logger.error(f"✗ Ошибка при удалении {dir_path}: {e}")
    
    logger.info(f"\nУспешно удалено {deleted_count} из {len(migrated_dirs)} папок")
    
    if deleted_count > 0:
        logger.info("Рекомендации:")
        logger.info("1. Папки data.migrated.* больше не будут создаваться")
        logger.info("2. Кеш лицензий теперь сохраняется в системной временной директории")
        logger.info("3. Добавлены правила в .gitignore для игнорирования подобных файлов")

def cleanup_license_cache_files():
    """Удаляет старые файлы кеша лицензий из текущей директории."""
    cache_files = [
        Path('.license_cache.json'),
        Path('.license_config.json'),
        Path('data/.license_cache.json'),
        Path('data/.license_config.json')
    ]
    
    deleted_files = []
    for cache_file in cache_files:
        if cache_file.exists():
            try:
                cache_file.unlink()
                deleted_files.append(cache_file)
                logger.info(f"✓ Удален файл кеша: {cache_file}")
            except Exception as e:
                logger.error(f"✗ Ошибка при удалении {cache_file}: {e}")
    
    if deleted_files:
        logger.info(f"Удалено {len(deleted_files)} файлов кеша лицензий")
    else:
        logger.info("Файлы кеша лицензий не найдены")

if __name__ == "__main__":
    logger.info("=== ОЧИСТКА МИГРИРОВАННЫХ ДАННЫХ ===")
    logger.info("Этот скрипт удалит папки data.migrated.* и старые файлы кеша лицензий")
    logger.info("")
    
    cleanup_migrated_directories()
    logger.info("")
    cleanup_license_cache_files()
    
    logger.info("")
    logger.info("=== ОЧИСТКА ЗАВЕРШЕНА ===")