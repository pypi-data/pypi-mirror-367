# Очистка кеша лицензий

## Быстрое решение

Если у вас постоянно создаются папки `data.migrated.*`, выполните следующие шаги:

### 1. Удалите существующие папки

```bash
# Windows (PowerShell)
Remove-Item -Recurse -Force data.migrated*

# Linux/macOS
rm -rf data.migrated*
```

### 2. Запустите скрипт очистки (опционально)

```bash
python cleanup_migrated_data.py
```

### 3. Проверьте .gitignore

Убедитесь, что в файле `.gitignore` есть следующие строки:

```gitignore
# License cache and migrated data directories
data.migrated*
.license_cache.json
.license_config.json
data/
```

## Что изменилось

- **Кеш лицензий** теперь сохраняется в системной временной директории
- **Папки `data.migrated.*`** больше не создаются
- **Файлы кеша** скрыты от системы контроля версий

## Где теперь хранится кеш

### Windows

- `%TEMP%\offers-check-marketplaces\.license_cache.json`
- `%USERPROFILE%\.offers-check-cache\.license_cache.json` (fallback)

### macOS/Linux

- `/tmp/offers-check-marketplaces/.license_cache.json`
- `~/.offers-check-cache/.license_cache.json` (fallback)

## Если проблема повторяется

1. Проверьте, что используется обновленная версия кода
2. Убедитесь, что у системы есть права на запись в временную директорию
3. При необходимости установите переменную окружения `OFFERS_CHECK_DATA_DIR`

## Дополнительная помощь

Если проблема не решается, обратитесь к документации в `docs/implementation/LICENSE_CACHE_OPTIMIZATION.md`
