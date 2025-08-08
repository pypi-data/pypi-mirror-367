"""
MCP Сервер для автоматизации поиска товаров и сравнения цен на маркетплейсах.

Этот сервер предоставляет инструменты для:
- Получения информации о товарах из базы данных
- Сохранения найденных цен с маркетплейсов
- Генерации статистики по обработанным товарам
- Работы с Excel файлами (парсинг, экспорт, трансформация)
- Управления лицензиями

Основные функции:
- get_product_details: получение детальной информации о товаре
- get_product_list: список всех товаров в базе данных
- save_product_prices: сохранение найденных цен
- get_statistics: статистика по обработанным товарам
- parse_excel_and_save_to_database: загрузка товаров из Excel
- Excel инструменты для обработки данных

Поддерживаемые маркетплейсы:
- komus.ru (Комус)
- vseinstrumenti.ru (ВсеИнструменты)
- ozon.ru (Озон)
- wildberries.ru (Wildberries)
- officemag.ru (Офисмаг)
- yandex_market (Яндекс.Маркет)
"""

import os
import sys
import anyio
import click
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Mount
from mcp.server.fastmcp import FastMCP

APP_ID = "offers-check-marketplaces"
mcp = FastMCP(APP_ID)

# Minimal Starlette app for SSE
starlette_app = Starlette(routes=[Mount("/", app=mcp.sse_app())])

# Пример инструмента для тестирования
@mcp.tool()
def test_connection() -> dict:
    """Тестирование подключения к MCP серверу"""
    return {
        "status": "success",
        "message": "MCP сервер offers-check-marketplaces работает корректно",
        "app_id": APP_ID,
        "available_tools": [
            "get_product_details",
            "get_product_list", 
            "save_product_prices",
            "get_statistics",
            "parse_excel_and_save_to_database",
            "parse_excel_file",
            "get_excel_info",
            "export_to_excel",
            "filter_excel_data",
            "transform_excel_data",
            "check_license_status",
            "set_license_key"
        ]
    }

# Ресурс с информацией о системе
@mcp.resource("system://info")
def get_system_info() -> str:
    """Получение информации о системе сравнения цен"""
    return """
    MCP Сервер: offers-check-marketplaces
    Назначение: Автоматизация поиска товаров и сравнения цен на маркетплейсах
    
    Основные возможности:
    - Управление базой данных товаров
    - Поиск и сохранение цен с маркетплейсов
    - Обработка Excel файлов
    - Генерация статистики и отчетов
    - Лицензионное управление
    
    Поддерживаемые форматы данных:
    - Excel файлы (.xlsx)
    - JSON структуры
    - SQLite база данных
    
    Интеграция с маркетплейсами через MCP Playwright для получения актуальных цен.
    """

# Runners
async def run_stdio():
    print("🚀 Запуск MCP сервера offers-check-marketplaces в режиме STDIO")
    print(f"📋 ID приложения: {APP_ID}")
    print(f"🐍 Версия Python: {sys.version}")
    print(f"📁 Рабочая директория: {os.getcwd()}")
    print(f"🔧 Переменные окружения:")
    for key in ['HOST', 'PORT', 'DEBUG']:
        value = os.getenv(key, 'не установлено')
        print(f"   {key}: {value}")
    print("📡 Ожидание подключения через STDIO...")
    print("💡 Доступные инструменты:")
    print("   - get_product_details: информация о товаре")
    print("   - get_product_list: список всех товаров")
    print("   - save_product_prices: сохранение цен")
    print("   - get_statistics: статистика обработки")
    print("   - parse_excel_and_save_to_database: загрузка из Excel")
    print("   - Excel инструменты для обработки данных")
    await mcp.run_stdio_async()

def run_sse(host: str, port: int):
    print("🚀 Запуск MCP сервера offers-check-marketplaces в режиме SSE")
    print(f"📋 ID приложения: {APP_ID}")
    print(f"🐍 Версия Python: {sys.version}")
    print(f"📁 Рабочая директория: {os.getcwd()}")
    print(f"🌐 Хост: {host}")
    print(f"🔌 Порт: {port}")
    print(f"🔗 URL сервера: http://{host}:{port}")
    print(f"🔧 Переменные окружения:")
    for key in ['HOST', 'PORT', 'DEBUG']:
        value = os.getenv(key, 'не установлено')
        print(f"   {key}: {value}")
    print("💡 Система автоматизации поиска цен на маркетплейсах готова к работе!")
    print("📊 Поддерживаемые маркетплейсы: Комус, ВсеИнструменты, Озон, Wildberries, Офисмаг")
    print("⚡ Запуск Uvicorn сервера...")
    uvicorn.run(starlette_app, host=host, port=port)

# CLI
@click.command()
@click.option("--sse", is_flag=True, help="Запуск как SSE сервер (иначе stdio).")
@click.option("--host", default=lambda: os.getenv("HOST", "0.0.0.0"),
              show_default=True, help="Хост для SSE режима")
@click.option("--port", type=int, default=lambda: int(os.getenv("PORT", 8000)),
              show_default=True, help="Порт для SSE режима")
def main(sse: bool, host: str, port: int):
    print("=" * 70)
    print("🏪 MCP СЕРВЕР СРАВНЕНИЯ ЦЕН НА МАРКЕТПЛЕЙСАХ")
    print("=" * 70)
    print(f"🚀 Режим запуска: {'SSE (Server-Sent Events)' if sse else 'STDIO'}")
    print(f"⏰ Время запуска: {os.getenv('TZ', 'системное время')}")
    print(f"💻 Платформа: {sys.platform}")
    print(f"🏠 Домашняя директория: {os.path.expanduser('~')}")
    print(f"📦 Приложение: {APP_ID}")
    print("=" * 70)
    print("🎯 НАЗНАЧЕНИЕ:")
    print("   • Автоматизация поиска товаров на маркетплейсах")
    print("   • Сравнение цен между различными источниками")
    print("   • Обработка Excel файлов с товарами")
    print("   • Генерация статистики и отчетов")
    print("=" * 70)
    print("🛒 ПОДДЕРЖИВАЕМЫЕ МАРКЕТПЛЕЙСЫ:")
    print("   • komus.ru (Комус)")
    print("   • vseinstrumenti.ru (ВсеИнструменты)")
    print("   • ozon.ru (Озон)")
    print("   • wildberries.ru (Wildberries)")
    print("   • officemag.ru (Офисмаг)")
    print("   • yandex_market (Яндекс.Маркет)")
    print("=" * 70)
    
    if sse:
        run_sse(host, port)
    else:
        anyio.run(run_stdio)

if __name__ == "__main__":
    main()
