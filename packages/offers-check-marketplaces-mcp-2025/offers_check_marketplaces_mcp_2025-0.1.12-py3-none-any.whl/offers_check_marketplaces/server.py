"""
MCP Сервер для автоматизации поиска товаров и сравнения цен на маркетплейсах.

Этот модуль реализует MCP (Model Context Protocol) сервер, который предоставляет
инструменты для автоматизации поиска товаров и сравнения цен на различных
российских маркетплейсах.

Основные возможности:
- Управление базой данных товаров (SQLite)
- Поиск и сохранение цен с маркетплейсов
- Обработка Excel файлов с товарами
- Генерация статистики и аналитики
- Лицензионное управление
- Интеграция с MCP Playwright для веб-скрапинга

Поддерживаемые маркетплейсы:
- komus.ru (Комус) - офисные товары и канцелярия
- vseinstrumenti.ru (ВсеИнструменты) - инструменты и оборудование
- ozon.ru (Озон) - универсальный маркетплейс
- wildberries.ru (Wildberries) - товары широкого потребления
- officemag.ru (Офисмаг) - офисные принадлежности
- yandex_market (Яндекс.Маркет) - агрегатор товаров

Доступные MCP инструменты:
- get_product_details: получение детальной информации о товаре
- get_product_list: список всех товаров с пагинацией
- save_product_prices: сохранение найденных цен (поддерживает 5 форматов)
- get_statistics: комплексная статистика по обработанным товарам
- parse_excel_and_save_to_database: загрузка товаров из Excel
- parse_excel_file: парсинг Excel файлов
- get_excel_info: информация о структуре Excel файлов
- export_to_excel: экспорт данных в Excel с форматированием
- filter_excel_data: фильтрация данных по критериям
- transform_excel_data: трансформация данных по правилам
- check_license_status: проверка статуса лицензии
- set_license_key: установка лицензионного ключа

Архитектура:
- Асинхронная обработка с использованием asyncio
- Модульная структура с разделением ответственности
- Комплексная обработка ошибок с восстановлением
- Логирование всех операций
- Валидация входных данных
- Поддержка пагинации для больших объемов данных

Форматы данных для save_product_prices:
1. Основной формат (рекомендуется):
   {"marketplaces": {"komus.ru": {"price": "1250 руб", "availability": "в наличии", "url": "..."}}}
2. Массив результатов:
   {"results": [{"marketplace": "ozon.ru", "price": 890.5, "currency": "RUB", ...}]}
3. Массив найденных предложений:
   {"found_offers": [{"marketplace": "officemag.ru", "price": 567.0, ...}]}
4. Одиночный результат:
   {"marketplace": "komus.ru", "price": 1250.0, "currency": "RUB", ...}
5. Прямой массив:
   [{"marketplace": "vseinstrumenti.ru", "price": 1320.0, ...}]

Использование:
- STDIO режим: для интеграции с MCP клиентами (Kiro, Cursor)
- SSE режим: для веб-интеграции и отладки
- Поддержка переменных окружения для конфигурации
- Автоматическая инициализация всех компонентов системы

Примеры вызовов:
- offers-check-marketplaces (STDIO режим)
- offers-check-marketplaces --sse --host 0.0.0.0 --port 8000 (SSE режим)

Лицензирование:
Система требует действительный лицензионный ключ для работы.
Ключ можно установить через переменную окружения LICENSE_KEY или
с помощью инструмента set_license_key.

Автор: Система автоматизации поиска цен на маркетплейсах
Версия: 1.0.0
"""

import os
import sys
import anyio
import click
import uvicorn
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any
from starlette.applications import Starlette
from starlette.routing import Mount
from mcp.server.fastmcp import FastMCP, Context

from .data_processor import DataProcessor
from .database_manager import DatabaseManager
from .search_engine import SearchEngine
from .statistics import StatisticsGenerator
from .marketplace_client import MarketplaceClient
from .marketplace_config import get_marketplace_config, get_all_marketplaces
from .license_manager import LicenseManager, check_license
from .excel_tools import ExcelTools
from .user_data_manager import UserDataManager
from .error_handling import (
    handle_errors,
    ErrorCategory,
    ErrorSeverity,
    create_user_friendly_error,
    get_error_summary,
    log_recovery_attempt
)

# Настройка логирования для отслеживания всех операций системы
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Идентификатор MCP приложения - используется для регистрации в MCP клиентах
APP_ID = "offers-check-marketplaces"

# Создание экземпляра FastMCP сервера для обработки MCP протокола
mcp = FastMCP(APP_ID)

# Глобальные экземпляры компонентов системы
# Инициализируются при запуске сервера и используются всеми MCP инструментами
user_data_manager: Optional[UserDataManager] = None      # Управление пользовательскими данными и директориями
data_processor: Optional[DataProcessor] = None           # Обработка Excel данных и преобразования
database_manager: Optional[DatabaseManager] = None       # Управление SQLite базой данных товаров и цен
search_engine: Optional[SearchEngine] = None             # Координация поиска на маркетплейсах
statistics_generator: Optional[StatisticsGenerator] = None # Генерация аналитики и статистики
marketplace_client: Optional[MarketplaceClient] = None   # Клиент для взаимодействия с маркетплейсами
excel_tools: Optional[ExcelTools] = None                 # Инструменты для работы с Excel файлами

async def initialize_components():
    """
    Инициализирует все компоненты системы.
    
    Создает экземпляры всех основных компонентов и настраивает
    их взаимодействие. Также инициализирует базу данных.
    """
    global user_data_manager, data_processor, database_manager, search_engine, statistics_generator, marketplace_client, excel_tools
    
    try:
        logger.info("Инициализация компонентов системы...")
        
        # Проверка лицензии перед инициализацией
        logger.info("Проверка лицензионного ключа...")
        is_valid, license_info = check_license()
        
        if not is_valid:
            error_msg = f"Недействительная лицензия: {license_info.get('message', 'Неизвестная ошибка')}"
            logger.error(error_msg)
            logger.error("Программа будет завершена из-за недействительной лицензии")
            print(f"ОШИБКА: {error_msg}")
            print("Программа завершена. Проверьте лицензионный ключ.")
            sys.exit(1)
        
        logger.info("Лицензия действительна, продолжаем инициализацию...")
        
        # Инициализация менеджера пользовательских данных
        logger.info("Инициализация менеджера пользовательских данных...")
        user_data_manager = UserDataManager()
        user_data_manager.initialize_directories()
        
        # Инициализация компонентов
        logger.info("Инициализация обработчика данных...")
        data_processor = DataProcessor()
        
        logger.info("Инициализация менеджера базы данных...")
        database_manager = DatabaseManager(user_data_manager)
        await database_manager.init_database()
        
        logger.info("Инициализация клиента маркетплейсов...")
        marketplace_client = MarketplaceClient()
        
        logger.info("Инициализация поискового движка...")
        search_engine = SearchEngine()
        
        logger.info("Инициализация генератора статистики...")
        statistics_generator = StatisticsGenerator(database_manager)
        
        logger.info("Инициализация Excel инструментов...")
        excel_tools = ExcelTools()
        
        logger.info("Все компоненты успешно инициализированы")
        
    except Exception as e:
        logger.error(f"Ошибка при инициализации компонентов: {e}")
        raise

# Минимальное Starlette приложение для SSE режима
# Используется для веб-интеграции и отладки MCP сервера через HTTP
starlette_app = Starlette(routes=[Mount("/", app=mcp.sse_app())])

# System prompt for AI agent
# ВАЖНО: Этот промт содержит критически важные инструкции для ИИ-агента
# о том, как правильно получать цены с маркетплейсов. НЕ УДАЛЯЙТЕ предупреждения
# о необходимости переходить на страницы товаров, а не брать цены из поисковой выдачи!
SYSTEM_PROMPT = """
# MCP Сервер "offers-check-marketplaces"

Вы работаете с MCP сервером offers-check-marketplaces, который автоматизирует поиск товаров 
и сравнение цен на различных маркетплейсах. Этот сервер является координирующим центром для 
анализа рыночных цен и генерации комплексных отчетов.

## КРИТИЧЕСКИ ВАЖНО: ПРАВИЛА ПОЛУЧЕНИЯ ЦЕН

⚠️ **ОБЯЗАТЕЛЬНОЕ ТРЕБОВАНИЕ**: Цены ДОЛЖНЫ быть получены ТОЛЬКО с официальных страниц товаров на маркетплейсах, НЕ из поисковой выдачи!

### ЗАПРЕЩЕНО:
-  Брать цены из результатов поиска Google/Yandex
-  Использовать цены из поисковых сниппетов
-  Полагаться на агрегаторы цен
-  Использовать кэшированные данные поисковых систем

### ОБЯЗАТЕЛЬНО:
-  Переходить на конкретную страницу товара на маркетплейсе
-  Анализировать HTML-структуру страницы товара
-  Извлекать цену непосредственно со страницы товара
-  Проверять актуальность и доступность товара
-  Учитывать скидки, акции и специальные предложения
-  Проверять соответствие найденного товара искомому

### АЛГОРИТМ ПОИСКА ЦЕН:

1. **Поиск товара на маркетплейсе**:
   - Используйте внутренний поиск маркетплейса
   - Найдите наиболее подходящий товар по названию/артикулу
   - Убедитесь в соответствии характеристик

2. **Переход на страницу товара**:
   - Обязательно перейдите на страницу конкретного товара
   - НЕ используйте цены из результатов поиска на сайте
   - Дождитесь полной загрузки страницы

3. **Извлечение цены**:
   - Найдите актуальную цену на странице товара
   - Учтите возможные скидки и акции
   - Проверьте наличие товара в продаже
   - Зафиксируйте валюту цены

4. **Валидация данных**:
   - Убедитесь, что найденный товар соответствует искомому
   - Проверьте разумность цены (не должна кардинально отличаться от ожидаемой)
   - Сохраните URL страницы товара для верификации

### ТЕХНИЧЕСКИЕ ТРЕБОВАНИЯ:

- Используйте MCP Playwright для навигации по сайтам
- Обрабатывайте динамический контент (JavaScript)
- Учитывайте антибот-защиту сайтов
- Соблюдайте задержки между запросами
- Сохраняйте скриншоты страниц для отладки

## ДОСТУПНЫЕ ИНСТРУМЕНТЫ

### 1. get_product_details(product_code: float)
Получение детальной информации о товаре по коду из базы данных.
- **Принимает**: код товара (число)
- **Возвращает**: полную информацию о товаре, текущие цены, процентные дельты
- **Особенности**:
  - Включает категорию, единицу измерения, приоритетные источники
  - Показывает сравнение цен между маркетплейсами
  - Рассчитывает процентные дельты между ценами
  - Определяет минимальные и максимальные цены

**Пример использования**:
```
get_product_details(195385.0)
```

**Пример ответа**:
```json
{
  "status": "success",
  "product": {
    "code": 195385.0,
    "model_name": "Полотно техническое БЯЗЬ ОТБЕЛЕННАЯ ГОСТ, рулон 1,5х50 м",
    "category": "Хозтовары и посуда",
    "unit": "м",
    "priority_1_source": "Комус",
    "priority_2_source": "ВсеИнструменты"
  },
  "prices": [
    {
      "marketplace": "komus.ru",
      "price": 1250.0,
      "currency": "RUB",
      "availability": "в наличии",
      "product_url": "https://www.komus.ru/product/12345",
      "scraped_at": "2023-07-21T15:30:45"
    },
    {
      "marketplace": "vseinstrumenti.ru",
      "price": 1320.0,
      "currency": "RUB",
      "availability": "в наличии",
      "product_url": "https://www.vseinstrumenti.ru/product/67890",
      "scraped_at": "2023-07-21T15:30:50"
    }
  ],
  "price_analysis": {
    "min_price": {
      "value": 1250.0,
      "marketplace": "komus.ru"
    },
    "max_price": {
      "value": 1320.0,
      "marketplace": "vseinstrumenti.ru"
    },
    "delta_percent": 5.6
  }
}
```

### 2. get_product_list()
Получение списка всех SKU товаров из базы данных.
- **Принимает**: ничего
- **Возвращает**: список всех товаров с их SKU и базовой информацией
- **Особенности**:
  - Возвращает все товары из базы данных
  - Включает SKU, название модели, категорию и единицу измерения
  - Полезно для получения полного списка доступных товаров
  - Можно использовать для последующего поиска конкретных товаров

**Пример использования**:
```
get_product_list()
```

**Пример ответа**:
```json
{
  "status": "success",
  "products": [
    {
      "sku": 195385.0,
      "model_name": "Полотно техническое БЯЗЬ ОТБЕЛЕННАЯ ГОСТ, рулон 1,5х50 м",
      "category": "Хозтовары и посуда",
      "unit": "м"
    },
    {
      "sku": 195386.0,
      "model_name": "Бумага офисная А4 80г/м2",
      "category": "Канцелярские товары",
      "unit": "пачка"
    }
  ],
  "total_count": 150,
  "timestamp": "2023-07-21T16:45:30"
}
```

### 3. get_statistics()
Получение статистики по всем обработанным товарам.
- **Принимает**: ничего
- **Возвращает**: комплексную статистику по обработанным товарам
- **Особенности**:
  - Общее количество обработанных товаров
  - Количество товаров с успешными совпадениями цен
  - Средние процентные дельты цен
  - Разбивка по категориям товаров
  - Информация о покрытии маркетплейсов

**Пример использования**:
```
get_statistics()
```

**Пример ответа**:
```json
{
  "status": "success",
  "statistics": {
    "total_products": 150,
    "products_with_prices": 132,
    "average_delta_percent": 7.8,
    "category_breakdown": {
      "Хозтовары и посуда": 45,
      "Канцелярские товары": 38,
      "Офисная техника": 27,
      "Мебель": 22,
      "Прочее": 18
    },
    "marketplace_coverage": {
      "komus.ru": 128,
      "vseinstrumenti.ru": 95,
      "ozon.ru": 112,
      "wildberries.ru": 87,
      "officemag.ru": 76
    }
  },
  "timestamp": "2023-07-21T16:45:30"
}
```

## ПОДДЕРЖИВАЕМЫЕ МАРКЕТПЛЕЙСЫ

### ОСНОВНЫЕ МАРКЕТПЛЕЙСЫ:

1. **komus.ru** (Комус) - офисные товары и канцелярия
   - URL поиска: `https://www.komus.ru/search/?q={query}`
   - Селектор цены: `.price-current, .product-price`
   - Особенности: требует переход на страницу товара

2. **vseinstrumenti.ru** (ВсеИнструменты) - инструменты и оборудование
   - URL поиска: `https://www.vseinstrumenti.ru/search/?what={query}`
   - Селектор цены: `.ui-price-current, .product-buy__price`
   - Особенности: динамическая загрузка цен

3. **ozon.ru** (Озон) - универсальный маркетплейс
   - URL поиска: `https://www.ozon.ru/search/?text={query}`
   - Селектор цены: `[data-widget="webPrice"], .price-current`
   - Особенности: сильная антибот-защита, требует осторожности

4. **wildberries.ru** (Wildberries) - товары широкого потребления
   - URL поиска: `https://www.wildberries.ru/catalog/0/search.aspx?search={query}`
   - Селектор цены: `.price-block__final-price, .product-page__price`
   - Особенности: цены могут различаться по регионам

5. **officemag.ru** (Офисмаг) - офисные принадлежности
   - URL поиска: `https://www.officemag.ru/search/?q={query}`
   - Селектор цены: `.price, .product-price__current`
   - Особенности: простая структура, надежный парсинг

### ВАЖНЫЕ ТЕХНИЧЕСКИЕ ДЕТАЛИ:

- **Обязательно используйте User-Agent**: `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36`
- **Соблюдайте задержки**: минимум 2-3 секунды между запросами
- **Проверяйте капчи**: при обнаружении - сообщайте об ошибке
- **Сохраняйте cookies**: для корректной работы с сессиями

### ДЕТАЛЬНЫЕ ИНСТРУКЦИИ ПО МАРКЕТПЛЕЙСАМ:

#### KOMUS.RU - Пошаговый алгоритм:
```
1. Открыть https://www.komus.ru
2. Найти поисковую строку (обычно в шапке сайта)
3. Ввести название товара
4. Дождаться результатов поиска
5. Кликнуть на ПЕРВЫЙ подходящий товар
6. На странице товара найти цену (селекторы: .price-current, .product-price)
7. Проверить наличие товара
8. Сохранить URL страницы товара
```

#### VSEINSTRUMENTI.RU - Пошаговый алгоритм:
```
1. Открыть https://www.vseinstrumenti.ru
2. Использовать поиск в шапке сайта
3. Ввести название товара
4. Выбрать наиболее подходящий товар из результатов
5. Перейти на страницу товара
6. Дождаться загрузки цены (может подгружаться динамически)
7. Извлечь цену (.ui-price-current, .product-buy__price)
8. Проверить доступность для заказа
```

#### OZON.RU - Особые требования:
```
 ВНИМАНИЕ: Сильная антибот-защита!
1. Открыть https://www.ozon.ru
2. Подождать 3-5 секунд для загрузки
3. Найти поисковую строку
4. Медленно ввести запрос (имитация человека)
5. Подождать результаты поиска
6. Осторожно кликнуть на товар
7. Дождаться полной загрузки страницы товара
8. Извлечь цену ([data-widget="webPrice"], .price-current)
```

#### WILDBERRIES.RU - Региональные особенности:
```
1. Открыть https://www.wildberries.ru
2. Проверить регион (может влиять на цену)
3. Использовать поиск
4. Выбрать товар из результатов
5. Перейти на карточку товара
6. Учесть возможные скидки и акции
7. Извлечь финальную цену (.price-block__final-price)
```

#### OFFICEMAG.RU - Простой алгоритм:
```
1. Открыть https://www.officemag.ru
2. Использовать поиск
3. Выбрать товар
4. Перейти на страницу товара
5. Извлечь цену (.price, .product-price__current)
6. Проверить наличие на складе
```

Пользователь может дополнить список промтами, правилами и контекстом в чате.

## РАБОЧИЙ ПРОЦЕСС

### Этап 1: Подготовка данных
- Система читает входной Excel файл `Таблица на вход.xlsx`
- Данные парсятся в JSON формат с сохранением структуры полей
- Информация сохраняется в SQLite базу данных для эффективных запросов

### Этап 2: Поиск товаров НА МАРКЕТПЛЕЙСАХ
 **КРИТИЧЕСКИ ВАЖНО**: Поиск цен ТОЛЬКО на официальных сайтах маркетплейсов!

**Алгоритм поиска для каждого товара:**

1. **Определение приоритетных источников** из Excel файла
2. **Переход на маркетплейс** через MCP Playwright:
   ```
   - Открыть главную страницу маркетплейса
   - Использовать внутренний поиск сайта
   - НЕ использовать Google/Yandex поиск!
   ```

3. **Поиск товара на сайте маркетплейса**:
   ```
   - Ввести название товара в поисковую строку сайта
   - Найти наиболее подходящий товар в результатах
   - Проверить соответствие характеристик
   ```

4. **Переход на страницу товара**:
   ```
   - ОБЯЗАТЕЛЬНО кликнуть на товар из результатов поиска
   - Дождаться полной загрузки страницы товара
   - НЕ брать цену из результатов поиска!
   ```

5. **Извлечение точной цены**:
   ```
   - Найти актуальную цену на странице товара
   - Учесть скидки и акции
   - Проверить наличие товара
   - Сохранить URL страницы товара
   ```

6. **Валидация и сохранение**:
   ```
   - Проверить разумность цены
   - Убедиться в соответствии товара
   - Сохранить результат в базу данных
   ```

### Этап 3: Анализ и детализация
- Используйте `get_product_details` для получения подробной информации
- Система рассчитывает процентные дельты между ценами
- Определяются минимальные и максимальные цены по источникам
- Проверяется качество найденных данных

### Этап 4: Статистика и отчеты
- `get_statistics` предоставляет общую аналитику
- Генерируется выходной Excel файл `data/Таблица на выход (отработанная).xlsx`
- Файл содержит исходные данные плюс найденные цены и расчеты
- Включаются ссылки на страницы товаров для верификации

## ПРИМЕРЫ ПРАВИЛЬНОГО И НЕПРАВИЛЬНОГО ПОИСКА

###  НЕПРАВИЛЬНО - НЕ ДЕЛАЙТЕ ТАК:
```
1. Поиск в Google: "Полотно техническое БЯЗЬ site:komus.ru"
2. Использование цены из поисковой выдачи: "1250 руб."
3. Переход по ссылке из Google без проверки актуальности
4. Использование агрегаторов цен типа Яндекс.Маркет
```

###  ПРАВИЛЬНО - ДЕЛАЙТЕ ТАК:
```
1. Переход на komus.ru
2. Использование поиска на сайте: поиск "Полотно техническое БЯЗЬ"
3. Клик на конкретный товар из результатов поиска
4. Извлечение цены со страницы товара: "1250,00 ₽"
5. Сохранение URL страницы товара для верификации
```

### ПРИМЕР ПРАВИЛЬНОГО АЛГОРИТМА:
```python
# Псевдокод правильного поиска
1. browser.navigate("https://www.komus.ru")
2. search_input = browser.find_element("input[name='q']")
3. search_input.type("Полотно техническое БЯЗЬ ОТБЕЛЕННАЯ")
4. search_input.press("Enter")
5. # Ждем результаты поиска
6. first_product = browser.find_element(".product-item:first-child a")
7. product_url = first_product.get_attribute("href")
8. browser.navigate(product_url)  # ПЕРЕХОДИМ НА СТРАНИЦУ ТОВАРА!
9. # Ждем загрузки страницы товара
10. price = browser.find_element(".price-current").text
11. availability = browser.find_element(".availability").text
12. # Сохраняем данные
```

## ОСОБЕННОСТИ АРХИТЕКТУРЫ

- **Координирующая роль**: Сервер не выполняет веб-скрапинг напрямую, а координирует работу через MCP Playwright
- **Асинхронная обработка**: Поддержка параллельного поиска на нескольких маркетплейсах
- **Обработка ошибок**: Graceful degradation при недоступности отдельных маркетплейсов
- **Rate limiting**: Соблюдение ограничений скорости для каждого маркетплейса
- **Качество данных**: Обязательная проверка соответствия найденного товара искомому
- **Трассировка**: Сохранение URL страниц товаров для последующей верификации

## ФОРМАТЫ ДАННЫХ

### Входной Excel
Содержит поля с символами переноса строк:
- "Код\nмодели" - уникальный код товара
- "model_name" - название модели товара
- "Категория" - категория товара
- "Единица измерения" - единица измерения товара
- "Приоритет \n1 Источники" - первичный источник поиска
- "Приоритет \n2 Источники" - вторичный источник поиска
- "Цена позиции\nМП c НДС" - пустое поле для заполнения
- "Цена позиции\nB2C c НДС" - пустое поле для заполнения
- "Дельта в процентах" - пустое поле для заполнения
- "Ссылка на источник" - пустое поле для заполнения
- "Цена 2 позиции\nB2C c НДС" - пустое поле для заполнения

### Выходной Excel
Дополняется заполненными полями:
- "Цена позиции\nМП c НДС" - цена на маркетплейсе
- "Цена позиции\nB2C c НДС" - B2C цена
- "Дельта в процентах" - процентная разница цен
- "Ссылка на источник" - URL товара на маркетплейсе
- "Цена 2 позиции\nB2C c НДС" - цена на втором маркетплейсе

## КОНТРОЛЬ КАЧЕСТВА ДАННЫХ

### ОБЯЗАТЕЛЬНЫЕ ПРОВЕРКИ ПЕРЕД СОХРАНЕНИЕМ ЦЕНЫ:

1. **Проверка соответствия товара**:
   - Название товара должно содержать ключевые слова из исходного запроса
   - Категория товара должна примерно соответствовать ожидаемой
   - Единица измерения должна совпадать (шт, м, кг и т.д.)

2. **Проверка разумности цены**:
   - Цена не должна быть нулевой или отрицательной
   - Цена не должна кардинально отличаться от ожидаемой (более чем в 10 раз)
   - Проверить валюту (должна быть RUB для российских маркетплейсов)

3. **Проверка доступности товара**:
   - Товар должен быть в наличии или доступен для заказа
   - Не сохранять цены товаров "нет в наличии" или "снят с производства"

4. **Проверка актуальности данных**:
   - URL страницы товара должен быть рабочим
   - Страница должна содержать актуальную информацию
   - Цена должна быть текущей, а не архивной

### ПРИМЕРЫ ПРАВИЛЬНЫХ И НЕПРАВИЛЬНЫХ ДАННЫХ:

#### ✅ ПРАВИЛЬНО:
```json
{
  "marketplace": "komus.ru",
  "price": 1250.0,
  "currency": "RUB",
  "availability": "в наличии",
  "product_url": "https://www.komus.ru/catalog/office/paper/12345",
  "product_match_confidence": "high"
}
```

####  НЕПРАВИЛЬНО:
```json
{
  "marketplace": "komus.ru",
  "price": 0.0,  // Нулевая цена
  "currency": "USD",  // Неправильная валюта
  "availability": "нет в наличии",  // Товар недоступен
  "product_url": "https://google.com/search?q=...",  // Ссылка на поиск
  "product_match_confidence": "low"  // Низкое соответствие
}
```

## РЕКОМЕНДУЕМАЯ ПОСЛЕДОВАТЕЛЬНОСТЬ ДЕЙСТВИЙ

1. Получите детальную информацию о товарах через `get_product_details`
2. Проанализируйте статистику через `get_statistics`
3. Для поиска новых цен используйте MCP Playwright с соблюдением всех правил
4. Сохраняйте найденные цены через `save_product_prices` только после проверки качества
5. При необходимости, повторите поиск для других товаров

## ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ

### Пример 1: Получение детальной информации о товаре
```
get_product_details(195385.0)
```

### Пример 2: Получение общей статистики
```
get_statistics()
```

## EXCEL ИНСТРУМЕНТЫ

### 1. parse_excel_file(file_path: str, sheet_name: Optional[str] = None, header_row: int = 0, max_rows: Optional[int] = None)
Парсинг Excel файла и возврат структурированных данных.
- **Принимает**: путь к файлу, название листа (опционально), номер строки заголовков, максимальное количество строк
- **Возвращает**: структурированные данные из Excel файла
- **Особенности**:
  - Поддержка различных листов Excel файла
  - Автоматическое определение заголовков
  - Обработка различных типов данных
  - Возможность ограничения количества читаемых строк

**Пример использования**:
```
parse_excel_file("data/input.xlsx", sheet_name="Данные", header_row=0, max_rows=100)
```

### 2. get_excel_info(file_path: str)
Получение информации о структуре Excel файла без полного чтения данных.
- **Принимает**: путь к Excel файлу
- **Возвращает**: информацию о листах, заголовках, размерах
- **Особенности**:
  - Быстрое получение метаданных файла
  - Информация о всех листах в файле
  - Определение заголовков и размеров данных

**Пример использования**:
```
get_excel_info("data/input.xlsx")
```

### 3. export_to_excel(data: List[Dict], file_path: str, sheet_name: str = "Data", include_index: bool = False, auto_adjust_columns: bool = True, apply_formatting: bool = True)
Экспорт данных в Excel файл с форматированием.
- **Принимает**: данные для экспорта, путь к файлу, настройки форматирования
- **Возвращает**: результат экспорта
- **Особенности**:
  - Автоматическое форматирование таблиц
  - Подгонка ширины колонок
  - Применение стилей к заголовкам
  - Настраиваемые параметры экспорта

**Пример использования**:
```
export_to_excel(data, "data/output.xlsx", sheet_name="Результаты", apply_formatting=True)
```

### 4. filter_excel_data(data: List[Dict], filters: Dict)
Фильтрация данных Excel по заданным критериям.
- **Принимает**: данные для фильтрации, критерии фильтрации
- **Возвращает**: отфильтрованные данные
- **Особенности**:
  - Поддержка сложных критериев фильтрации
  - Числовые и текстовые фильтры
  - Множественные условия фильтрации

**Пример использования**:
```
filter_excel_data(data, {"Категория": "Хозтовары", "Цена": {"greater_than": 1000}})
```

### 5. transform_excel_data(data: List[Dict], transformations: Dict)
Трансформация данных Excel согласно заданным правилам.
- **Принимает**: данные для трансформации, правила трансформации
- **Возвращает**: трансформированные данные
- **Особенности**:
  - Преобразование типов данных
  - Строковые операции (замена, изменение регистра)
  - Математические операции с числами
  - Настраиваемые правила трансформации

**Пример использования**:
```
transform_excel_data(data, {"model_name": {"to_upper": true}, "price": {"multiply": 1.2}})
```

### 6. parse_excel_and_save_to_database(file_path: str, sheet_name: Optional[str] = None, header_row: int = 0, start_row: Optional[int] = None, max_rows: Optional[int] = None)
**УЛУЧШЕННЫЙ ИНСТРУМЕНТ** - Парсинг Excel файла и автоматическое сохранение товаров в базу данных с поддержкой диапазонов.
- **Принимает**: путь к файлу, название листа (опционально), номер строки заголовков, начальная строка данных, максимальное количество строк
- **Возвращает**: результат парсинга и сохранения в БД
- **Особенности**:
  - Автоматически парсит Excel файл с товарами
  - **НОВОЕ**: Поддержка чтения определенного диапазона строк (start_row, max_rows)
  - **НОВОЕ**: Возможность загружать большие файлы частями
  - Сохраняет новые товары в базу данных SQLite
  - Обновляет существующие товары при совпадении кода
  - Поддерживает стандартный формат Excel с полями: "Код\nмодели", "model_name", "Категория", "Единица измерения", "Приоритет \n1 Источники", "Приоритет \n2 Источники"
  - Обрабатывает ошибки и предоставляет детальную статистику
  - Возвращает информацию о созданных и обновленных товарах

**Примеры использования**:
```
# Загрузить все товары
parse_excel_and_save_to_database("data/Таблица на вход.xlsx", sheet_name="Лист1", header_row=0)

# Загрузить товары с 151 по 300 строку
parse_excel_and_save_to_database("data/Таблица на вход.xlsx", sheet_name="Лист1", header_row=0, start_row=150, max_rows=150)

# Загрузить следующие 100 товаров начиная с 301 строки
parse_excel_and_save_to_database("data/Таблица на вход.xlsx", sheet_name="Лист1", header_row=0, start_row=300, max_rows=100)
```

**Пример ответа**:
```json
{
  "status": "success",
  "message": "Успешно обработано 150 товаров из Excel файла",
  "file_path": "data/Таблица на вход.xlsx",
  "start_row": 150,
  "rows_requested": 150,
  "total_rows_parsed": 150,
  "products_created": 120,
  "products_updated": 30,
  "total_processed": 150,
  "products_saved": [
    {
      "code": 195385.0,
      "model_name": "Полотно техническое БЯЗЬ ОТБЕЛЕННАЯ ГОСТ",
      "action": "created",
      "id": 1
    }
  ],
  "parse_info": {
    "sheet_name": "Лист1",
    "columns": ["Код\nмодели", "model_name", "Категория"],
    "available_sheets": ["Лист1", "Лист2"],
    "data_range": "строки 150-299"
  },
  "timestamp": "2023-07-21T15:30:45"
}
```

## РАБОЧИЙ ПРОЦЕСС С EXCEL

### БЫСТРЫЙ СПОСОБ (РЕКОМЕНДУЕТСЯ)
**Для загрузки товаров из Excel в базу данных:**
1. Используйте `parse_excel_and_save_to_database` для одновременного парсинга и сохранения
2. Функция автоматически создаст новые товары и обновит существующие
3. Получите детальную статистику по обработанным товарам

### ПОШАГОВЫЙ СПОСОБ (ДЛЯ СЛОЖНОЙ ОБРАБОТКИ)

#### Этап 1: Анализ структуры файла
- Используйте `get_excel_info` для получения информации о структуре Excel файла
- Определите листы, заголовки и размеры данных

#### Этап 2: Парсинг данных
- Используйте `parse_excel_file` для чтения данных из Excel файла
- Настройте параметры чтения (лист, заголовки, количество строк)

#### Этап 3: Обработка данных
- Применяйте `filter_excel_data` для фильтрации данных по критериям
- Используйте `transform_excel_data` для преобразования данных

#### Этап 4: Экспорт результатов
- Экспортируйте обработанные данные с помощью `export_to_excel`
- Настройте форматирование и стили для лучшего представления

### ИНТЕГРАЦИЯ С ОСНОВНОЙ СИСТЕМОЙ
После загрузки товаров в базу данных через `parse_excel_and_save_to_database`:
1. Используйте `get_product_list` для получения списка всех товаров
2. Сохраняйте найденные цены через `save_product_prices`
3. Получайте статистику через `get_statistics`

Используйте инструменты последовательно для полного анализа товаров и генерации отчетов.

---
## РЕЗЮМЕ КЛЮЧЕВЫХ ТРЕБОВАНИЙ:

 **КРИТИЧЕСКИ ВАЖНО**: 
- НЕ брать цены из Google/Yandex поиска
- ОБЯЗАТЕЛЬНО переходить на страницы товаров на маркетплейсах
- Проверять соответствие найденного товара искомому
- Сохранять URL страниц товаров для верификации

 **ТЕХНИЧЕСКИЕ ТРЕБОВАНИЯ**:
- Использовать MCP Playwright для навигации
- Соблюдать задержки между запросами (2-3 сек)
- Обрабатывать антибот-защиту
- Проверять качество данных перед сохранением

 **РЕЗУЛЬТАТ**: Точные, актуальные цены с официальных страниц товаров маркетплейсов
---
"""

@mcp.prompt("system")
def get_system_prompt() -> str:
    """Get system prompt for AI agent"""
    return SYSTEM_PROMPT

# MCP Tools implementations

@handle_errors(
    category=ErrorCategory.DATABASE,
    severity=ErrorSeverity.MEDIUM,
    component="mcp_server",
    recovery_action="Возврат пользовательского сообщения об ошибке"
)
@mcp.tool()
async def get_product_details(product_code: float, ctx: Context = None) -> dict:
    """
    Get detailed information about a product including price comparison
    
    Args:
        product_code: Unique product code from the database
        ctx: MCP context object
        
    Returns:
        Dictionary with detailed product information and price data
    """
    from .error_handling import (
        create_user_friendly_error,
        ValidationError,
        error_handler,
        ErrorCategory,
        ErrorSeverity,
        log_recovery_attempt
    )
    
    logger.info(f"Запрос на получение информации о товаре с кодом: {product_code}")
    
    try:
        # Валидация входных данных
        if not isinstance(product_code, (int, float)):
            error = ValidationError("Код товара должен быть числом", field="product_code", value=product_code)
            return create_user_friendly_error(error, "получение информации о товаре")
        
        # Проверяем инициализацию компонентов
        if database_manager is None:
            logger.error("Менеджер базы данных не инициализирован")
            return {
                "status": "error",
                "message": "Внутренняя ошибка: менеджер базы данных не инициализирован",
                "error_code": "COMPONENT_NOT_INITIALIZED",
                "user_message": "Система временно недоступна, попробуйте позже",
                "recoverable": True,
                "retry_suggested": True
            }
        
        # Получаем информацию о продукте из базы данных
        product = await database_manager.get_product_by_code(product_code)
        
        if not product:
            logger.warning(f"Продукт с кодом {product_code} не найден в базе данных")
            log_recovery_attempt(
                component="server",
                action=f"Продукт с кодом {product_code} не найден",
                success=False
            )
            return {
                "status": "not_found",
                "message": f"Продукт с кодом {product_code} не найден",
                "error_code": "PRODUCT_NOT_FOUND",
                "user_message": "Товар с указанным кодом не найден в базе данных",
                "recoverable": False,
                "retry_suggested": False
            }
        
        # Получаем цены продукта с разных маркетплейсов
        prices = await database_manager.get_product_prices(product["id"])
        
        # Если цены не найдены, возвращаем только информацию о продукте
        if not prices:
            logger.info(f"Для продукта с кодом {product_code} не найдены цены")
            log_recovery_attempt(
                component="server",
                action="Возврат информации о товаре без цен",
                success=True
            )
            return {
                "status": "success",
                "product": {
                    "code": product["code"],
                    "model_name": product["model_name"],
                    "category": product["category"],
                    "unit": product["unit"],
                    "priority_1_source": product["priority_1_source"],
                    "priority_2_source": product["priority_2_source"]
                },
                "prices": [],
                "price_analysis": {
                    "min_price": None,
                    "max_price": None,
                    "delta_percent": None
                },
                "message": "Для данного продукта не найдены цены на маркетплейсах"
            }
        
        # Анализируем цены для расчета минимальной, максимальной и дельты
        valid_prices = [p for p in prices if p["price"] is not None and p["price"] > 0]
        
        price_analysis = {
            "min_price": None,
            "max_price": None,
            "delta_percent": None
        }
        
        if valid_prices:
            # Находим минимальную цену
            min_price_item = min(valid_prices, key=lambda x: x["price"])
            price_analysis["min_price"] = {
                "value": min_price_item["price"],
                "marketplace": min_price_item["marketplace"]
            }
            
            # Находим максимальную цену
            max_price_item = max(valid_prices, key=lambda x: x["price"])
            price_analysis["max_price"] = {
                "value": max_price_item["price"],
                "marketplace": max_price_item["marketplace"]
            }
            
            # Рассчитываем процентную дельту между мин и макс ценами
            if min_price_item["price"] > 0:
                delta = ((max_price_item["price"] - min_price_item["price"]) / min_price_item["price"]) * 100
                price_analysis["delta_percent"] = round(delta, 2)
        
        # Формируем итоговый ответ
        response = {
            "status": "success",
            "product": {
                "code": product["code"],
                "model_name": product["model_name"],
                "category": product["category"],
                "unit": product["unit"],
                "priority_1_source": product["priority_1_source"],
                "priority_2_source": product["priority_2_source"]
            },
            "prices": prices,
            "price_analysis": price_analysis
        }
        
        logger.info(f"Успешно получена информация о товаре с кодом {product_code}")
        log_recovery_attempt(
            component="server",
            action=f"Успешное получение информации о товаре {product_code}",
            success=True
        )
        return response
        
    except Exception as e:
        error_handler.log_error(
            error=e,
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
            component="server",
            details={"tool": "get_product_details", "product_code": product_code},
            recovery_action="Возврат пользовательского сообщения об ошибке"
        )
        return create_user_friendly_error(e, "получение информации о товаре")

@handle_errors(
    category=ErrorCategory.DATABASE,
    severity=ErrorSeverity.MEDIUM,
    component="mcp_server",
    recovery_action="Возврат пользовательского сообщения об ошибке"
)
@mcp.tool()
async def get_product_list(offset: int = 0, limit: int = 150, filter_status: str = "all", ctx: Context = None) -> dict:
    """
    Get list of all product SKUs from the database with pagination support
    
    Args:
        offset: Starting position (0-based index) for pagination
        limit: Maximum number of products to return (default: 150, if None, returns all from offset)
        filter_status: Filter by processing status ("all", "processed", "not_processed")
        ctx: MCP context object
        
    Returns:
        Dictionary with list of product codes (SKUs) and basic info with pagination info
        Each product includes processing status (processed/not_processed)
        
    Usage Examples:
        - Get first 150 products (recommended): offset=0, limit=150
        - Get products 151-300: offset=150, limit=150
        - Get products 301-450: offset=300, limit=150
        - Get all products from position 100: offset=99, limit=None
        - Get all products: offset=0, limit=None
        - Get only processed products: filter_status="processed"
        - Get only unprocessed products: filter_status="not_processed"
        
    Recommendation: Use limit=150 for optimal performance and memory usage
    """
    from .error_handling import (
        create_user_friendly_error,
        error_handler,
        ErrorCategory,
        ErrorSeverity,
        log_recovery_attempt
    )
    
    logger.info("Запрос на получение списка SKU товаров")
    
    try:
        # Проверяем инициализацию компонентов
        if database_manager is None:
            logger.error("Менеджер базы данных не инициализирован")
            return {
                "status": "error",
                "message": "Внутренняя ошибка: менеджер базы данных не инициализирован",
                "error_code": "COMPONENT_NOT_INITIALIZED",
                "user_message": "Система временно недоступна, попробуйте позже",
                "recoverable": True,
                "retry_suggested": True
            }
        
        # Получаем все продукты из базы данных
        products = await database_manager.get_all_products()
        
        if not products:
            logger.info("В базе данных нет товаров")
            return {
                "status": "no_data",
                "message": "В базе данных нет товаров",
                "user_message": "База данных пока не содержит товаров",
                "products": [],
                "total_count": 0,
                "recoverable": True,
                "retry_suggested": False
            }
        
        # Формируем список SKU с базовой информацией и статусом обработки
        product_list = []
        for product in products:
            # Проверяем, есть ли у товара цены (обработан ли он)
            has_prices = await database_manager.has_product_prices(product["id"])
            
            product_info = {
                "sku": product["code"],
                "model_name": product["model_name"],
                "category": product["category"],
                "unit": product["unit"],
                "processed": has_prices,
                "status": "processed" if has_prices else "not_processed"
            }
            
            # Применяем фильтр по статусу обработки
            if filter_status == "all":
                product_list.append(product_info)
            elif filter_status == "processed" and has_prices:
                product_list.append(product_info)
            elif filter_status == "not_processed" and not has_prices:
                product_list.append(product_info)
        
        total_count = len(product_list)
        
        # Применяем пагинацию
        if offset < 0:
            offset = 0
        
        if offset >= total_count:
            logger.info(f"Offset {offset} превышает общее количество товаров {total_count}")
            return {
                "status": "success",
                "products": [],
                "total_count": total_count,
                "offset": offset,
                "limit": limit,
                "filter_status": filter_status,
                "returned_count": 0,
                "has_more": False,
                "timestamp": datetime.now().isoformat()
            }
        
        # Применяем срез для пагинации
        if limit is None:
            paginated_products = product_list[offset:]
        else:
            if limit <= 0:
                limit = 150  # Рекомендуемое значение по умолчанию
            paginated_products = product_list[offset:offset + limit]
        
        returned_count = len(paginated_products)
        has_more = (offset + returned_count) < total_count
        
        logger.info(f"Получен список из {returned_count} товаров (offset: {offset}, limit: {limit}, total: {total_count})")
        
        log_recovery_attempt(
            component="server",
            action=f"Успешное получение списка {returned_count} товаров с пагинацией",
            success=True
        )
        
        return {
            "status": "success",
            "products": paginated_products,
            "total_count": total_count,
            "offset": offset,
            "limit": limit,
            "filter_status": filter_status,
            "returned_count": returned_count,
            "has_more": has_more,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        error_handler.log_error(
            error=e,
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
            component="server",
            details={"tool": "get_product_list"},
            recovery_action="Возврат пользовательского сообщения об ошибке"
        )
        return create_user_friendly_error(e, "получение списка товаров")

@handle_errors(
    category=ErrorCategory.SYSTEM,
    severity=ErrorSeverity.MEDIUM,
    component="mcp_server",
    recovery_action="Возврат пользовательского сообщения об ошибке"
)
@mcp.tool()
async def get_statistics(ctx: Context = None) -> dict:
    """
    Get statistics about processed products and price comparisons
    
    Args:
        ctx: MCP context object
        
    Returns:
        Dictionary with comprehensive statistics about the processed data
    """
    from .error_handling import (
        create_user_friendly_error,
        error_handler,
        ErrorCategory,
        ErrorSeverity,
        log_recovery_attempt
    )
    
    logger.info("Запрос на получение статистики")
    
    try:
        # Проверяем инициализацию компонентов
        if statistics_generator is None:
            logger.error("Генератор статистики не инициализирован")
            return {
                "status": "error",
                "message": "Внутренняя ошибка: генератор статистики не инициализирован",
                "error_code": "COMPONENT_NOT_INITIALIZED",
                "user_message": "Система временно недоступна, попробуйте позже",
                "recoverable": True,
                "retry_suggested": True
            }
        
        if database_manager is None:
            logger.error("Менеджер базы данных не инициализирован")
            return {
                "status": "error",
                "message": "Внутренняя ошибка: менеджер базы данных не инициализирован",
                "error_code": "COMPONENT_NOT_INITIALIZED",
                "user_message": "Система временно недоступна, попробуйте позже",
                "recoverable": True,
                "retry_suggested": True
            }
        
        # Генерируем полную статистику через StatisticsGenerator
        logger.info("Генерация статистики через StatisticsGenerator...")
        full_statistics = await statistics_generator.generate_full_statistics()
        
        # Проверяем, что статистика получена
        if not full_statistics:
            logger.warning("Не удалось получить статистику")
            log_recovery_attempt(
                component="server",
                action="Возврат пустой статистики",
                success=True
            )
            return {
                "status": "no_data",
                "message": "Нет данных для генерации статистики",
                "user_message": "В базе данных пока нет обработанных товаров для анализа",
                "statistics": {
                    "total_products": 0,
                    "products_with_prices": 0,
                    "average_delta_percent": 0.0,
                    "category_breakdown": {},
                    "marketplace_coverage": {}
                },
                "timestamp": datetime.now().isoformat(),
                "recoverable": True,
                "retry_suggested": False
            }
        
        # Формируем ответ в соответствии с требованиями
        response = {
            "status": "success",
            "statistics": {
                "total_products": full_statistics.total_products,
                "products_with_prices": full_statistics.products_with_prices,
                "average_delta_percent": round(full_statistics.average_delta_percent, 2),
                "category_breakdown": full_statistics.category_breakdown,
                "marketplace_coverage": full_statistics.marketplace_coverage
            },
            "timestamp": full_statistics.processing_timestamp.isoformat() if hasattr(full_statistics, 'processing_timestamp') and full_statistics.processing_timestamp else datetime.now().isoformat()
        }
        
        # Логируем успешное получение статистики
        logger.info(
            f"Статистика успешно получена: {full_statistics.total_products} товаров, "
            f"{full_statistics.products_with_prices} с ценами, "
            f"средняя дельта: {full_statistics.average_delta_percent:.2f}%"
        )
        
        log_recovery_attempt(
            component="server",
            action=f"Успешная генерация статистики для {full_statistics.total_products} товаров",
            success=True
        )
        
        return response
        
    except Exception as e:
        error_handler.log_error(
            error=e,
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.HIGH,
            component="server",
            details={"tool": "get_statistics"},
            recovery_action="Возврат пользовательского сообщения об ошибке"
        )
        return create_user_friendly_error(e, "получение статистики")

@handle_errors(
    category=ErrorCategory.DATABASE,
    severity=ErrorSeverity.MEDIUM,
    component="mcp_server",
    recovery_action="Возврат пользовательского сообщения об ошибке"
)
@mcp.tool()
async def save_product_prices(product_code: float, search_results: dict, ctx: Context = None) -> dict:
    """
    Save found prices for a specific product to the database
    
    Args:
        product_code: Unique product code from the database
        search_results: Dictionary with search results. Supports multiple formats:
            
            Format 1 - Results array:
            {
                "results": [
                    {
                        "marketplace": "ozon",
                        "price": 299.0,
                        "currency": "RUB",
                        "availability": "В наличии",
                        "product_url": "https://...",
                        "rating": 4.5,
                        "reviews_count": 100,
                        "product_found": true
                    }
                ]
            }
            
            Format 2 - Found offers array:
            {
                "found_offers": [
                    {
                        "marketplace": "wildberries",
                        "price": 280.0,
                        "currency": "RUB",
                        "availability": "В наличии"
                    }
                ]
            }
            
            Format 3 - Single product (direct fields):
            {
                "marketplace": "yandex_market",
                "price": 320.0,
                "currency": "RUB",
                "availability": "В наличии",
                "product_url": "https://..."
            }
            
            Format 4 - Array in root:
            [
                {
                    "marketplace": "ozon",
                    "price": 299.0,
                    "currency": "RUB"
                }
            ]
            
            Format 5 - Marketplaces object (recommended):
            {
                "marketplaces": {
                    "ozon": {
                        "price": "299 руб",
                        "availability": "В наличии",
                        "url": "https://...",
                        "rating": 4.5,
                        "reviews_count": 100
                    },
                    "wildberries": {
                        "price": "от 280 руб",
                        "availability": "В наличии"
                    }
                }
            }
            
            Required fields for each offer:
            - marketplace: string (marketplace name)
            - price: number or string with price (e.g., "299 руб", "от 280 руб")
            
            Optional fields:
            - currency: string (default: "RUB")
            - availability: string
            - product_url: string
            - rating: number
            - reviews_count: number
            - product_found: boolean (auto-set to true if price exists)
            
        ctx: MCP context object
        
    Returns:
        Dictionary with save operation results:
        {
            "status": "success" | "error" | "not_found" | "no_data",
            "message": "Description of the result",
            "saved_count": number,
            "total_results": number,
            "saved_prices": [...],
            "errors": [...] (if any)
        }
    """
    from .error_handling import (
        create_user_friendly_error,
        ValidationError,
        error_handler,
        ErrorCategory,
        ErrorSeverity,
        log_recovery_attempt
    )
    
    logger.info(f"Запрос на сохранение цен для товара с кодом: {product_code}")
    logger.debug(f"Получены данные: {search_results}")
    
    try:
        # Валидация входных данных
        if not isinstance(product_code, (int, float)):
            error = ValidationError("Код товара должен быть числом", field="product_code", value=product_code)
            return create_user_friendly_error(error, "сохранение цен товара")
        
        if not search_results or not isinstance(search_results, dict):
            error = ValidationError("Результаты поиска должны быть словарем", field="search_results", value=search_results)
            return create_user_friendly_error(error, "сохранение цен товара")
        
        # Проверяем инициализацию компонентов
        if database_manager is None:
            logger.error("Менеджер базы данных не инициализирован")
            return {
                "status": "error",
                "message": "Внутренняя ошибка: менеджер базы данных не инициализирован",
                "error_code": "COMPONENT_NOT_INITIALIZED",
                "user_message": "Система временно недоступна, попробуйте позже",
                "recoverable": True,
                "retry_suggested": True
            }
        
        # Получаем продукт из базы данных
        product = await database_manager.get_product_by_code(product_code)
        if not product:
            logger.warning(f"Продукт с кодом {product_code} не найден в базе данных")
            return {
                "status": "not_found",
                "message": f"Продукт с кодом {product_code} не найден",
                "error_code": "PRODUCT_NOT_FOUND",
                "user_message": "Товар с указанным кодом не найден в базе данных",
                "recoverable": False,
                "retry_suggested": False
            }
        
        # Нормализуем входные данные - поддерживаем различные форматы
        results = []
        
        # Формат 1: {"results": [...]}
        if "results" in search_results and isinstance(search_results["results"], list):
            results = search_results["results"]
            logger.debug(f"Обнаружен формат 1: results array с {len(results)} элементами")
        
        # Формат 2: {"found_offers": [...]}
        elif "found_offers" in search_results and isinstance(search_results["found_offers"], list):
            results = search_results["found_offers"]
            logger.debug(f"Обнаружен формат 2: found_offers array с {len(results)} элементами")
            # Нормализуем структуру для found_offers
            for result in results:
                if "product_found" not in result:
                    result["product_found"] = True  # Если цена есть, значит товар найден
        
        # Формат 3: Прямые поля в корне (один товар)
        elif "marketplace" in search_results and "price" in search_results:
            results = [search_results]
            search_results["product_found"] = True
            logger.debug("Обнаружен формат 3: прямые поля в корне")
        
        # Формат 4: Массив в корне
        elif isinstance(search_results, list):
            results = search_results
            logger.debug(f"Обнаружен формат 4: массив в корне с {len(results)} элементами")
            # Нормализуем структуру
            for result in results:
                if "product_found" not in result:
                    result["product_found"] = True
        
        # Формат 5: Поддержка формата с marketplaces (основной формат системы)
        elif "marketplaces" in search_results and isinstance(search_results["marketplaces"], dict):
            results = []
            marketplaces = search_results["marketplaces"]
            logger.debug(f"Обнаружен формат 5: marketplaces с {len(marketplaces)} маркетплейсами")
            
            for marketplace_name, marketplace_data in marketplaces.items():
                if isinstance(marketplace_data, dict) and "price" in marketplace_data:
                    # Преобразуем цену из строки в число
                    price_str = marketplace_data.get("price", "")
                    price_value = None
                    
                    if price_str:
                        # Извлекаем числовое значение из строки типа "299 руб" или "от 280 руб"
                        import re
                        price_match = re.search(r'(\d+(?:\.\d+)?)', str(price_str))
                        if price_match:
                            price_value = float(price_match.group(1))
                    
                    if price_value and price_value > 0:
                        result_item = {
                            "marketplace": marketplace_name,
                            "price": price_value,
                            "currency": "RUB",
                            "availability": marketplace_data.get("availability", "Неизвестно"),
                            "product_url": marketplace_data.get("url"),
                            "rating": marketplace_data.get("rating"),
                            "reviews_count": marketplace_data.get("reviews_count"),
                            "product_found": True
                        }
                        results.append(result_item)
                        logger.debug(f"Добавлен результат для {marketplace_name}: {price_value} руб")
                    else:
                        logger.debug(f"Пропущен {marketplace_name}: некорректная цена '{price_str}'")
        
        
        # Проверяем, что у нас есть данные для сохранения
        if not results:
            logger.warning(f"Нет результатов поиска для сохранения")
            logger.debug(f"Структура полученных данных: {list(search_results.keys())}")
            logger.debug(f"Полные данные: {search_results}")
            
            # Дополнительная диагностика
            diagnostic_info = {
                "received_keys": list(search_results.keys()),
                "has_marketplaces": "marketplaces" in search_results,
                "has_results": "results" in search_results,
                "has_found_offers": "found_offers" in search_results,
                "is_list": isinstance(search_results, list),
                "has_direct_fields": "marketplace" in search_results and "price" in search_results
            }
            
            if "marketplaces" in search_results:
                marketplaces = search_results["marketplaces"]
                diagnostic_info["marketplaces_type"] = type(marketplaces).__name__
                if isinstance(marketplaces, dict):
                    diagnostic_info["marketplaces_keys"] = list(marketplaces.keys())
                    diagnostic_info["marketplaces_count"] = len(marketplaces)
                    # Проверяем каждый маркетплейс
                    for mp_name, mp_data in marketplaces.items():
                        diagnostic_info[f"{mp_name}_has_price"] = "price" in mp_data if isinstance(mp_data, dict) else False
                        if isinstance(mp_data, dict) and "price" in mp_data:
                            diagnostic_info[f"{mp_name}_price_value"] = mp_data["price"]
            
            return {
                "status": "no_data",
                "message": "Нет результатов поиска для сохранения",
                "user_message": "Результаты поиска пусты, нечего сохранять",
                "diagnostic_info": diagnostic_info,
                "recoverable": True,
                "retry_suggested": False
            }
        
        # Сохраняем цены для каждого маркетплейса
        saved_count = 0
        errors = []
        saved_prices = []
        
        for i, result in enumerate(results):
            logger.debug(f"Обработка результата {i+1}: {result}")
            
            # Проверяем наличие цены (гибко)
            price = result.get("price")
            if not price:
                logger.debug(f"Результат {i+1}: отсутствует цена, ключи: {list(result.keys())}")
                errors.append(f"Результат {i+1}: отсутствует поле 'price'")
                continue
                
            # Проверяем, что товар найден (если поле есть)
            if "product_found" in result and not result.get("product_found"):
                logger.debug(f"Результат {i+1}: товар не найден (product_found=False)")
                errors.append(f"Результат {i+1}: товар не найден на маркетплейсе")
                continue
                
            try:
                # Проверяем, что цена может быть преобразована в число
                try:
                    price_float = float(price)
                    if price_float <= 0:
                        raise ValueError(f"Цена должна быть положительным числом, получено: {price_float}")
                except (ValueError, TypeError) as e:
                    error_msg = f"Результат {i+1}: некорректная цена '{price}': {e}"
                    errors.append(error_msg)
                    logger.warning(error_msg)
                    continue
                
                price_data = {
                    "marketplace": result.get("marketplace", "unknown"),
                    "price": price_float,
                    "currency": result.get("currency", "RUB"),
                    "availability": result.get("availability", "Неизвестно"),
                    "product_url": result.get("product_url") or result.get("url")
                }
                
                logger.debug(f"Попытка сохранения цены: {price_data}")
                await database_manager.save_price(product["id"], price_data)
                saved_count += 1
                saved_prices.append({
                    "marketplace": price_data["marketplace"],
                    "price": price_data["price"],
                    "currency": price_data["currency"],
                    "availability": price_data["availability"]
                })
                logger.info(f"Сохранена цена для {price_data['marketplace']}: {price_data['price']} {price_data['currency']}")
                
            except Exception as price_error:
                error_msg = f"Ошибка сохранения цены для {result.get('marketplace', 'unknown')}: {price_error}"
                errors.append(error_msg)
                logger.error(error_msg)
                logger.debug(f"Детали ошибки: результат={result}, ошибка={type(price_error).__name__}: {price_error}")
        
        # Формируем ответ
        if saved_count > 0:
            logger.info(f"Успешно сохранено {saved_count} цен для товара {product_code}")
            log_recovery_attempt(
                component="server",
                action=f"Сохранение {saved_count} цен для товара {product_code}",
                success=True
            )
            
            response = {
                "status": "success",
                "message": f"Сохранено {saved_count} цен для товара {product_code}",
                "product_code": product_code,
                "product_name": product["model_name"],
                "saved_prices": saved_count,
                "total_results": len(results),
                "prices_saved": saved_prices,
                "timestamp": datetime.now().isoformat()
            }
            
            if errors:
                response["warnings"] = errors
                
            return response
        else:
            logger.warning(f"Не удалось сохранить ни одной цены для товара {product_code}")
            return {
                "status": "no_data",
                "message": "Не удалось сохранить ни одной цены",
                "user_message": "В результатах поиска нет валидных цен для сохранения",
                "product_code": product_code,
                "total_results": len(results),
                "errors": errors,
                "recoverable": True,
                "retry_suggested": True
            }
        
    except Exception as e:
        error_handler.log_error(
            error=e,
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
            component="server",
            details={"tool": "save_product_prices", "product_code": product_code},
            recovery_action="Возврат пользовательского сообщения об ошибке"
        )
        return create_user_friendly_error(e, "сохранение цен товара")


@handle_errors(
    category=ErrorCategory.SYSTEM,
    severity=ErrorSeverity.LOW,
    component="mcp_server",
    recovery_action="Возврат информации о лицензии"
)
@mcp.tool()
async def check_license_status(ctx: Context = None) -> dict:
    """
    Check the current license status and information
    
    Args:
        ctx: MCP context object
        
    Returns:
        Dictionary with license status and information
    """
    from .error_handling import (
        create_user_friendly_error,
        error_handler,
        ErrorCategory,
        ErrorSeverity,
        log_recovery_attempt
    )
    
    logger.info("Запрос на проверку статуса лицензии")
    
    try:
        # Создаем экземпляр менеджера лицензий
        license_manager = LicenseManager()
        
        # Получаем информацию о лицензии
        license_info = license_manager.get_license_info()
        
        is_valid = license_info["is_valid"]
        license_data = license_info["license_data"]
        
        if is_valid:
            logger.info("Лицензия действительна")
            log_recovery_attempt(
                component="server",
                action="Успешная проверка лицензии",
                success=True
            )
            
            return {
                "status": "valid",
                "message": "Лицензия действительна",
                "license_key": license_info["license_key"],
                "license_info": {
                    "valid": license_data.get("valid", False),
                    "checked_at": license_data.get("checked_at"),
                    "expires_at": license_data.get("expires_at"),
                    "plan": license_data.get("plan"),
                    "features": license_data.get("features", [])
                },
                "api_url": license_info["api_url"]
            }
        else:
            logger.warning("Лицензия недействительна")
            log_recovery_attempt(
                component="server",
                action="Обнаружена недействительная лицензия",
                success=False
            )
            
            return {
                "status": "invalid",
                "message": "Лицензия недействительна",
                "license_key": license_info["license_key"],
                "error": license_data.get("error", "UNKNOWN_ERROR"),
                "error_message": license_data.get("message", "Неизвестная ошибка"),
                "user_message": license_data.get("user_message", "Лицензия недействительна"),
                "api_url": license_info["api_url"]
            }
            
    except Exception as e:
        error_handler.log_error(
            error=e,
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.MEDIUM,
            component="server",
            details={"tool": "check_license_status"},
            recovery_action="Возврат информации об ошибке проверки лицензии"
        )
        return create_user_friendly_error(e, "проверка статуса лицензии")

@handle_errors(
    category=ErrorCategory.SYSTEM,
    severity=ErrorSeverity.MEDIUM,
    component="mcp_server",
    recovery_action="Возврат результата установки лицензии"
)
@mcp.tool()
async def set_license_key(license_key: str, ctx: Context = None) -> dict:
    """
    Set a new license key for the system
    
    Args:
        license_key: New license key to set
        ctx: MCP context object
        
    Returns:
        Dictionary with result of license key setting
    """
    from .error_handling import (
        create_user_friendly_error,
        ValidationError,
        error_handler,
        ErrorCategory,
        ErrorSeverity,
        log_recovery_attempt
    )
    
    logger.info("Запрос на установку нового лицензионного ключа")
    
    try:
        # Валидация входных данных
        if not license_key or not isinstance(license_key, str) or len(license_key.strip()) == 0:
            error = ValidationError("Необходимо указать непустой лицензионный ключ", field="license_key", value=license_key)
            return create_user_friendly_error(error, "установка лицензионного ключа")
        
        license_key = license_key.strip()
        
        # Создаем экземпляр менеджера лицензий
        license_manager = LicenseManager()
        
        # Устанавливаем новый ключ
        success = license_manager.set_license_key(license_key, save_to_config=True)
        
        if success:
            logger.info("Новый лицензионный ключ успешно установлен")
            log_recovery_attempt(
                component="server",
                action="Успешная установка нового лицензионного ключа",
                success=True
            )
            
            # Получаем информацию о новой лицензии
            license_info = license_manager.get_license_info()
            
            return {
                "status": "success",
                "message": "Лицензионный ключ успешно установлен и проверен",
                "license_key": license_key,
                "license_info": license_info["license_data"],
                "saved_to_config": True
            }
        else:
            logger.error("Не удалось установить новый лицензионный ключ")
            log_recovery_attempt(
                component="server",
                action="Неудачная установка лицензионного ключа",
                success=False
            )
            
            return {
                "status": "error",
                "message": "Лицензионный ключ недействителен",
                "error_code": "INVALID_LICENSE_KEY",
                "user_message": "Указанный лицензионный ключ недействителен",
                "license_key": license_key,
                "recoverable": True,
                "retry_suggested": True
            }
            
    except Exception as e:
        error_handler.log_error(
            error=e,
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.HIGH,
            component="server",
            details={"tool": "set_license_key", "license_key": license_key[:8] + "..." if license_key else "None"},
            recovery_action="Возврат пользовательского сообщения об ошибке"
        )
        return create_user_friendly_error(e, "установка лицензионного ключа")

# Excel Tools MCP Functions

@handle_errors(
    category=ErrorCategory.PARSING,
    severity=ErrorSeverity.MEDIUM,
    component="mcp_server",
    recovery_action="Возврат пользовательского сообщения об ошибке"
)
@mcp.tool()
async def parse_excel_file(file_path: str, sheet_name: Optional[str] = None, 
                          header_row: int = 0, max_rows: Optional[int] = None, 
                          ctx: Context = None) -> dict:
    """
    Parse Excel file and return structured data
    
    Args:
        file_path: Path to Excel file
        sheet_name: Sheet name (if None, uses first sheet)
        header_row: Header row number (0-based)
        max_rows: Maximum number of rows to read
        ctx: MCP context object
        
    Returns:
        Dictionary with parsed Excel data
    """
    from .error_handling import (
        create_user_friendly_error,
        ValidationError,
        error_handler,
        ErrorCategory,
        ErrorSeverity,
        log_recovery_attempt
    )
    
    logger.info(f"Запрос на парсинг Excel файла: {file_path}")
    
    try:
        # Валидация входных данных
        if not file_path or not isinstance(file_path, str):
            error = ValidationError("Необходимо указать путь к Excel файлу", field="file_path", value=file_path)
            return create_user_friendly_error(error, "парсинг Excel файла")
        
        if header_row < 0:
            error = ValidationError("Номер строки заголовков не может быть отрицательным", field="header_row", value=header_row)
            return create_user_friendly_error(error, "парсинг Excel файла")
        
        if max_rows is not None and max_rows <= 0:
            error = ValidationError("Максимальное количество строк должно быть положительным", field="max_rows", value=max_rows)
            return create_user_friendly_error(error, "парсинг Excel файла")
        
        # Проверяем инициализацию компонентов
        if excel_tools is None:
            logger.error("Excel инструменты не инициализированы")
            return {
                "status": "error",
                "message": "Внутренняя ошибка: Excel инструменты не инициализированы",
                "error_code": "COMPONENT_NOT_INITIALIZED",
                "user_message": "Система временно недоступна, попробуйте позже",
                "recoverable": True,
                "retry_suggested": True
            }
        
        # Парсим Excel файл
        result = await excel_tools.parse_excel_file(
            file_path=file_path,
            sheet_name=sheet_name,
            header_row=header_row,
            max_rows=max_rows
        )
        
        logger.info(f"Успешно распарсен Excel файл: {result.get('total_rows', 0)} строк")
        
        log_recovery_attempt(
            component="server",
            action=f"Успешный парсинг Excel файла {file_path}",
            success=True
        )
        
        return result
        
    except Exception as e:
        error_handler.log_error(
            error=e,
            category=ErrorCategory.PARSING,
            severity=ErrorSeverity.HIGH,
            component="server",
            details={"tool": "parse_excel_file", "file_path": file_path},
            recovery_action="Возврат пользовательского сообщения об ошибке"
        )
        return create_user_friendly_error(e, "парсинг Excel файла")

@handle_errors(
    category=ErrorCategory.PARSING,
    severity=ErrorSeverity.MEDIUM,
    component="mcp_server",
    recovery_action="Возврат пользовательского сообщения об ошибке"
)
@mcp.tool()
async def get_excel_info(file_path: str, ctx: Context = None) -> dict:
    """
    Get information about Excel file structure without reading all data
    
    Args:
        file_path: Path to Excel file
        ctx: MCP context object
        
    Returns:
        Dictionary with Excel file structure information
    """
    from .error_handling import (
        create_user_friendly_error,
        ValidationError,
        error_handler,
        ErrorCategory,
        ErrorSeverity,
        log_recovery_attempt
    )
    
    logger.info(f"Запрос на получение информации о Excel файле: {file_path}")
    
    try:
        # Валидация входных данных
        if not file_path or not isinstance(file_path, str):
            error = ValidationError("Необходимо указать путь к Excel файлу", field="file_path", value=file_path)
            return create_user_friendly_error(error, "получение информации о Excel файле")
        
        # Проверяем инициализацию компонентов
        if excel_tools is None:
            logger.error("Excel инструменты не инициализированы")
            return {
                "status": "error",
                "message": "Внутренняя ошибка: Excel инструменты не инициализированы",
                "error_code": "COMPONENT_NOT_INITIALIZED",
                "user_message": "Система временно недоступна, попробуйте позже",
                "recoverable": True,
                "retry_suggested": True
            }
        
        # Получаем информацию о файле
        result = await excel_tools.get_excel_info(file_path)
        
        logger.info(f"Получена информация о Excel файле: {result.get('total_sheets', 0)} листов")
        
        log_recovery_attempt(
            component="server",
            action=f"Успешное получение информации о Excel файле {file_path}",
            success=True
        )
        
        return result
        
    except Exception as e:
        error_handler.log_error(
            error=e,
            category=ErrorCategory.PARSING,
            severity=ErrorSeverity.HIGH,
            component="server",
            details={"tool": "get_excel_info", "file_path": file_path},
            recovery_action="Возврат пользовательского сообщения об ошибке"
        )
        return create_user_friendly_error(e, "получение информации о Excel файле")

@handle_errors(
    category=ErrorCategory.PARSING,
    severity=ErrorSeverity.MEDIUM,
    component="mcp_server",
    recovery_action="Возврат пользовательского сообщения об ошибке"
)
@mcp.tool()
async def export_to_excel(file_path: str, sheet_name: str = "Data", 
                         include_index: bool = False, auto_adjust_columns: bool = True, 
                         apply_formatting: bool = True, ctx: Context = None) -> dict:
    """
    Export products with prices from database to Excel file with original structure formatting
    
    Args:
        file_path: Path to save Excel file (Нужно указывать абсолютный путь, чтобы было лучше понятно, где файл)
        sheet_name: Sheet name
        include_index: Whether to include row index
        auto_adjust_columns: Auto-adjust column widths
        apply_formatting: Apply formatting to the file
        ctx: MCP context object
        
    Returns:
        Dictionary with export result
    """
    from .error_handling import (
        create_user_friendly_error,
        ValidationError,
        error_handler,
        ErrorCategory,
        ErrorSeverity,
        log_recovery_attempt
    )
    
    logger.info(f"Запрос на экспорт данных из базы данных в Excel файл: {file_path}")
    
    try:
        # Валидация входных данных
        if not file_path or not isinstance(file_path, str):
            error = ValidationError("Необходимо указать путь для сохранения Excel файла", field="file_path", value=file_path)
            return create_user_friendly_error(error, "экспорт в Excel файл")
        
        if not sheet_name or not isinstance(sheet_name, str):
            error = ValidationError("Название листа должно быть непустой строкой", field="sheet_name", value=sheet_name)
            return create_user_friendly_error(error, "экспорт в Excel файл")
        
        # Проверяем инициализацию компонентов
        if excel_tools is None:
            logger.error("Excel инструменты не инициализированы")
            return {
                "status": "error",
                "message": "Внутренняя ошибка: Excel инструменты не инициализированы",
                "error_code": "COMPONENT_NOT_INITIALIZED",
                "user_message": "Система временно недоступна, попробуйте позже",
                "recoverable": True,
                "retry_suggested": True
            }
        
        if database_manager is None:
            logger.error("Менеджер базы данных не инициализирован")
            return {
                "status": "error",
                "message": "Внутренняя ошибка: Менеджер базы данных не инициализирован",
                "error_code": "COMPONENT_NOT_INITIALIZED",
                "user_message": "Система временно недоступна, попробуйте позже",
                "recoverable": True,
                "retry_suggested": True
            }
        
        # Получаем данные из базы данных
        logger.info("Получение данных продуктов с ценами из базы данных")
        data = await database_manager.get_products_with_prices_for_export()
        
        if not data:
            logger.warning("Нет данных для экспорта в базе данных")
            return {
                "status": "warning",
                "message": "В базе данных нет продуктов для экспорта",
                "user_message": "База данных пуста. Сначала загрузите продукты и получите цены.",
                "rows_exported": 0,
                "file_created": False
            }
        
        # Экспортируем данные
        result = await excel_tools.export_to_excel(
            data=data,
            file_path=file_path,
            sheet_name=sheet_name,
            include_index=include_index,
            auto_adjust_columns=auto_adjust_columns,
            apply_formatting=apply_formatting
        )
        
        logger.info(f"Успешно экспортированы данные в Excel файл: {result.get('rows_exported', 0)} строк")
        
        log_recovery_attempt(
            component="server",
            action=f"Успешный экспорт данных из БД в Excel файл {file_path}",
            success=True
        )
        
        # Добавляем информацию о структуре данных
        result.update({
            "data_source": "database",
            "export_type": "products_with_prices",
            "columns_structure": [
                "Код модели", "model_name", "Категория", "Единица измерения",
                "Приоритет 1 Источники", "Приоритет 2 Источники",
                "Цена позиции МП c НДС", "Цена позиции B2C c НДС",
                "Дельта в процентах", "Ссылка на источник",
                "Цена 2 позиции B2C c НДС", "Ссылка на источник 2",
                "Дополнительно"
            ]
        })
        
        return result
        
    except Exception as e:
        error_handler.log_error(
            error=e,
            category=ErrorCategory.PARSING,
            severity=ErrorSeverity.HIGH,
            component="server",
            details={"tool": "export_to_excel", "file_path": file_path},
            recovery_action="Возврат пользовательского сообщения об ошибке"
        )
        return create_user_friendly_error(e, "экспорт в Excel файл")

@handle_errors(
    category=ErrorCategory.PARSING,
    severity=ErrorSeverity.MEDIUM,
    component="mcp_server",
    recovery_action="Возврат пользовательского сообщения об ошибке"
)
@mcp.tool()
async def filter_excel_data(data: List[Dict[str, Any]], filters: Dict[str, Any], 
                           ctx: Context = None) -> dict:
    """
    Filter Excel data by specified criteria
    
    Args:
        data: Source data to filter
        filters: Dictionary with filter criteria
        ctx: MCP context object
        
    Returns:
        Filtered data
    """
    from .error_handling import (
        create_user_friendly_error,
        ValidationError,
        error_handler,
        ErrorCategory,
        ErrorSeverity,
        log_recovery_attempt
    )
    
    logger.info(f"Запрос на фильтрацию данных по критериям: {filters}")
    
    try:
        # Валидация входных данных
        if not data or not isinstance(data, list):
            error = ValidationError("Данные должны быть списком словарей", field="data", value=type(data).__name__)
            return create_user_friendly_error(error, "фильтрация данных")
        
        if not filters or not isinstance(filters, dict):
            error = ValidationError("Фильтры должны быть словарем", field="filters", value=type(filters).__name__)
            return create_user_friendly_error(error, "фильтрация данных")
        
        # Проверяем инициализацию компонентов
        if excel_tools is None:
            logger.error("Excel инструменты не инициализированы")
            return {
                "status": "error",
                "message": "Внутренняя ошибка: Excel инструменты не инициализированы",
                "error_code": "COMPONENT_NOT_INITIALIZED",
                "user_message": "Система временно недоступна, попробуйте позже",
                "recoverable": True,
                "retry_suggested": True
            }
        
        # Фильтруем данные
        result = await excel_tools.filter_excel_data(data, filters)
        
        logger.info(f"Фильтрация завершена: {result.get('filtered_count', 0)} из {result.get('original_count', 0)} строк")
        
        log_recovery_attempt(
            component="server",
            action=f"Успешная фильтрация данных",
            success=True
        )
        
        return result
        
    except Exception as e:
        error_handler.log_error(
            error=e,
            category=ErrorCategory.PARSING,
            severity=ErrorSeverity.HIGH,
            component="server",
            details={"tool": "filter_excel_data", "filters": filters},
            recovery_action="Возврат пользовательского сообщения об ошибке"
        )
        return create_user_friendly_error(e, "фильтрация данных")

@handle_errors(
    category=ErrorCategory.PARSING,
    severity=ErrorSeverity.MEDIUM,
    component="mcp_server",
    recovery_action="Возврат пользовательского сообщения об ошибке"
)
@mcp.tool()
async def transform_excel_data(data: List[Dict[str, Any]], transformations: Dict[str, Any], 
                              ctx: Context = None) -> dict:
    """
    Transform Excel data according to specified rules
    
    Args:
        data: Source data to transform
        transformations: Dictionary with transformation rules
        ctx: MCP context object
        
    Returns:
        Transformed data
    """
    from .error_handling import (
        create_user_friendly_error,
        ValidationError,
        error_handler,
        ErrorCategory,
        ErrorSeverity,
        log_recovery_attempt
    )
    
    logger.info(f"Запрос на трансформацию данных по правилам: {transformations}")
    
    try:
        # Валидация входных данных
        if not data or not isinstance(data, list):
            error = ValidationError("Данные должны быть списком словарей", field="data", value=type(data).__name__)
            return create_user_friendly_error(error, "трансформация данных")
        
        if not transformations or not isinstance(transformations, dict):
            error = ValidationError("Правила трансформации должны быть словарем", field="transformations", value=type(transformations).__name__)
            return create_user_friendly_error(error, "трансформация данных")
        
        # Проверяем инициализацию компонентов
        if excel_tools is None:
            logger.error("Excel инструменты не инициализированы")
            return {
                "status": "error",
                "message": "Внутренняя ошибка: Excel инструменты не инициализированы",
                "error_code": "COMPONENT_NOT_INITIALIZED",
                "user_message": "Система временно недоступна, попробуйте позже",
                "recoverable": True,
                "retry_suggested": True
            }
        
        # Трансформируем данные
        result = await excel_tools.transform_excel_data(data, transformations)
        
        logger.info(f"Трансформация завершена: {result.get('transformed_count', 0)} строк")
        
        log_recovery_attempt(
            component="server",
            action=f"Успешная трансформация данных",
            success=True
        )
        
        return result
        
    except Exception as e:
        error_handler.log_error(
            error=e,
            category=ErrorCategory.PARSING,
            severity=ErrorSeverity.HIGH,
            component="server",
            details={"tool": "transform_excel_data", "transformations": transformations},
            recovery_action="Возврат пользовательского сообщения об ошибке"
        )
        return create_user_friendly_error(e, "трансформация данных")

@handle_errors(
    category=ErrorCategory.DATABASE,
    severity=ErrorSeverity.HIGH,
    component="mcp_server",
    recovery_action="Возврат пользовательского сообщения об ошибке"
)
@mcp.tool()
async def parse_excel_and_save_to_database(file_path: str, sheet_name: Optional[str] = None, 
                                          header_row: int = 0, start_row: Optional[int] = None,
                                          max_rows: Optional[int] = None,
                                          ctx: Context = None) -> dict:
    """
    Parse Excel file and automatically save products to database
    
    Args:
        file_path: Path to Excel file
        sheet_name: Sheet name (if None, uses first sheet)
        header_row: Header row number (0-based)
        start_row: Starting row number for data reading (0-based, after header). If None, starts from header_row + 1
        max_rows: Maximum number of rows to read from start_row. If None, reads all remaining rows
        ctx: MCP context object
        
    Returns:
        Dictionary with parsing and saving results
    """
    from .error_handling import (
        create_user_friendly_error,
        ValidationError,
        error_handler,
        ErrorCategory,
        ErrorSeverity,
        log_recovery_attempt
    )
    
    logger.info(f"Запрос на парсинг Excel файла и сохранение в БД: {file_path}")
    
    try:
        # Валидация входных данных
        if not file_path or not isinstance(file_path, str):
            error = ValidationError("Необходимо указать путь к Excel файлу", field="file_path", value=file_path)
            return create_user_friendly_error(error, "парсинг и сохранение Excel файла")
        
        if start_row is not None and start_row < 0:
            error = ValidationError("Начальная строка не может быть отрицательной", field="start_row", value=start_row)
            return create_user_friendly_error(error, "парсинг и сохранение Excel файла")
        
        if max_rows is not None and max_rows <= 0:
            error = ValidationError("Количество строк должно быть положительным", field="max_rows", value=max_rows)
            return create_user_friendly_error(error, "парсинг и сохранение Excel файла")
        
        # Проверяем инициализацию компонентов
        if excel_tools is None:
            logger.error("Excel инструменты не инициализированы")
            return {
                "status": "error",
                "message": "Внутренняя ошибка: Excel инструменты не инициализированы",
                "error_code": "COMPONENT_NOT_INITIALIZED",
                "user_message": "Система временно недоступна, попробуйте позже",
                "recoverable": True,
                "retry_suggested": True
            }
        
        if database_manager is None:
            logger.error("Менеджер базы данных не инициализирован")
            return {
                "status": "error",
                "message": "Внутренняя ошибка: менеджер базы данных не инициализирован",
                "error_code": "COMPONENT_NOT_INITIALIZED",
                "user_message": "Система временно недоступна, попробуйте позже",
                "recoverable": True,
                "retry_suggested": True
            }
        
        # Шаг 1: Парсим Excel файл
        logger.info("Шаг 1: Парсинг Excel файла...")
        
        # Определяем параметры для чтения Excel
        if start_row is not None:
            # Если указана начальная строка, нужно пропустить строки до неё
            skip_rows = start_row
            # Читаем заголовки отдельно
            header_result = await excel_tools.parse_excel_file(
                file_path=file_path,
                sheet_name=sheet_name,
                header_row=header_row,
                max_rows=1  # Читаем только заголовки
            )
            
            if header_result.get("status") != "success":
                logger.error(f"Ошибка чтения заголовков Excel файла: {header_result}")
                return {
                    "status": "error",
                    "message": "Ошибка чтения заголовков Excel файла",
                    "parse_result": header_result,
                    "user_message": "Не удалось прочитать заголовки Excel файла",
                    "recoverable": True,
                    "retry_suggested": True
                }
            
            # Теперь читаем данные начиная с указанной строки
            # Нужно использовать более низкоуровневый подход для чтения с определенной строки
            logger.info(f"Чтение данных начиная со строки {start_row}, максимум {max_rows or 'все'} строк")
            
            # Для упрощения, пока используем существующий метод с корректировкой
            total_rows_to_read = (start_row + max_rows) if max_rows else None
            parse_result = await excel_tools.parse_excel_file(
                file_path=file_path,
                sheet_name=sheet_name,
                header_row=header_row,
                max_rows=total_rows_to_read
            )
            
            if parse_result.get("status") == "success":
                # Обрезаем данные до нужного диапазона
                all_data = parse_result.get("data", [])
                if start_row < len(all_data):
                    end_row = start_row + max_rows if max_rows else len(all_data)
                    parse_result["data"] = all_data[start_row:end_row]
                    parse_result["total_rows"] = len(parse_result["data"])
                    logger.info(f"Выбран диапазон строк {start_row}-{min(end_row, len(all_data))}, получено {len(parse_result['data'])} строк")
                else:
                    parse_result["data"] = []
                    parse_result["total_rows"] = 0
                    logger.warning(f"Начальная строка {start_row} превышает количество данных в файле ({len(all_data)})")
        else:
            # Обычное чтение с начала
            parse_result = await excel_tools.parse_excel_file(
                file_path=file_path,
                sheet_name=sheet_name,
                header_row=header_row,
                max_rows=max_rows
            )
        
        if parse_result.get("status") != "success":
            logger.error(f"Ошибка парсинга Excel файла: {parse_result}")
            return {
                "status": "error",
                "message": "Ошибка парсинга Excel файла",
                "parse_result": parse_result,
                "user_message": "Не удалось прочитать Excel файл, проверьте формат и путь к файлу",
                "recoverable": True,
                "retry_suggested": True
            }
        
        data = parse_result.get("data", [])
        if not data:
            logger.warning("Excel файл не содержит данных")
            return {
                "status": "no_data",
                "message": "Excel файл не содержит данных",
                "user_message": "Excel файл пуст или не содержит данных для обработки",
                "parse_result": parse_result,
                "recoverable": False,
                "retry_suggested": False
            }
        
        range_info = f" (строки {start_row}-{start_row + len(data) - 1})" if start_row is not None else ""
        logger.info(f"Успешно распарсено {len(data)} строк из Excel файла{range_info}")
        
        # Шаг 2: Сохраняем товары в базу данных
        logger.info("Шаг 2: Сохранение товаров в базу данных...")
        saved_count = 0
        updated_count = 0
        errors = []
        saved_products = []
        
        for i, row_data in enumerate(data):
            try:
                # Проверяем наличие обязательных полей
                code = row_data.get("Код\nмодели") or row_data.get("code")
                model_name = row_data.get("model_name")
                
                if not code or not model_name:
                    error_msg = f"Строка {i+1}: отсутствуют обязательные поля (код или название модели)"
                    errors.append(error_msg)
                    logger.warning(error_msg)
                    continue
                
                # Проверяем, существует ли товар в базе данных
                existing_product = await database_manager.get_product_by_code(float(code))
                
                if existing_product:
                    # Обновляем существующий товар
                    product_data = {
                        "code": float(code),
                        "model_name": model_name,
                        "category": row_data.get("Категория") or row_data.get("category", ""),
                        "unit": row_data.get("Единица измерения") or row_data.get("unit", ""),
                        "priority_1_source": row_data.get("Приоритет \n1 Источники") or row_data.get("priority_1_source", ""),
                        "priority_2_source": row_data.get("Приоритет \n2 Источники") or row_data.get("priority_2_source", "")
                    }
                    
                    success = await database_manager.update_product(product_data)
                    if success:
                        updated_count += 1
                        saved_products.append({
                            "code": code,
                            "model_name": model_name,
                            "action": "updated"
                        })
                        logger.info(f"Обновлен товар с кодом {code}")
                    else:
                        error_msg = f"Строка {i+1}: не удалось обновить товар с кодом {code}"
                        errors.append(error_msg)
                        logger.warning(error_msg)
                else:
                    # Создаем новый товар
                    try:
                        product_id = await database_manager.save_product(row_data)
                        saved_count += 1
                        saved_products.append({
                            "code": code,
                            "model_name": model_name,
                            "action": "created",
                            "id": product_id
                        })
                        logger.info(f"Создан новый товар с кодом {code}, ID: {product_id}")
                    except Exception as save_error:
                        error_msg = f"Строка {i+1}: ошибка сохранения товара с кодом {code}: {save_error}"
                        errors.append(error_msg)
                        logger.error(error_msg)
                        
            except Exception as row_error:
                error_msg = f"Строка {i+1}: ошибка обработки: {row_error}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        # Формируем итоговый ответ
        total_processed = saved_count + updated_count
        
        if total_processed > 0:
            logger.info(f"Успешно обработано {total_processed} товаров: {saved_count} новых, {updated_count} обновлено")
            log_recovery_attempt(
                component="server",
                action=f"Сохранение {total_processed} товаров из Excel в БД",
                success=True
            )
            
            response = {
                "status": "success",
                "message": f"Успешно обработано {total_processed} товаров из Excel файла",
                "file_path": file_path,
                "start_row": start_row,
                "rows_requested": max_rows,
                "total_rows_parsed": len(data),
                "products_created": saved_count,
                "products_updated": updated_count,
                "total_processed": total_processed,
                "products_saved": saved_products,
                "parse_info": {
                    "sheet_name": parse_result.get("sheet_name"),
                    "columns": parse_result.get("columns"),
                    "available_sheets": parse_result.get("available_sheets"),
                    "data_range": f"строки {start_row}-{start_row + len(data) - 1}" if start_row is not None else "все строки"
                },
                "timestamp": datetime.now().isoformat()
            }
            
            if errors:
                response["warnings"] = errors
                response["errors_count"] = len(errors)
                
            return response
        else:
            logger.warning("Не удалось сохранить ни одного товара")
            return {
                "status": "no_data",
                "message": "Не удалось сохранить ни одного товара",
                "user_message": "Все строки Excel файла содержат ошибки или отсутствуют обязательные поля",
                "file_path": file_path,
                "start_row": start_row,
                "rows_requested": max_rows,
                "total_rows_parsed": len(data),
                "errors": errors,
                "errors_count": len(errors),
                "recoverable": True,
                "retry_suggested": True
            }
        
    except Exception as e:
        error_handler.log_error(
            error=e,
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
            component="server",
            details={"tool": "parse_excel_and_save_to_database", "file_path": file_path},
            recovery_action="Возврат пользовательского сообщения об ошибке"
        )
        return create_user_friendly_error(e, "парсинг и сохранение Excel файла")

# Функции запуска MCP сервера в различных режимах

async def run_stdio():
    """
    Запуск MCP сервера в STDIO режиме.
    
    STDIO режим используется для интеграции с MCP клиентами (Kiro, Cursor и др.).
    В этом режиме сервер общается через стандартные потоки ввода/вывода,
    что позволяет MCP клиентам запускать сервер как подпроцесс.
    
    Процесс запуска:
    1. Проверка лицензии
    2. Инициализация всех компонентов системы
    3. Регистрация MCP инструментов
    4. Ожидание команд от MCP клиента
    """
    print(" Запуск MCP сервера offers-check-marketplaces в режиме STDIO")
    print(f" ID приложения: {APP_ID}")
    print(f" Версия Python: {sys.version}")
    print(f" Рабочая директория: {os.getcwd()}")
    print(f" Переменные окружения:")
    for key in ['HOST', 'PORT', 'DEBUG', 'LICENSE_KEY']:
        value = os.getenv(key, 'не установлено')
        # Скрываем лицензионный ключ для безопасности
        if key == 'LICENSE_KEY' and value != 'не установлено':
            value = value[:8] + "..." if len(value) > 8 else "***"
        print(f"   {key}: {value}")
    
    print("=" * 70)
    print(" СИСТЕМА СРАВНЕНИЯ ЦЕН НА МАРКЕТПЛЕЙСАХ")
    print("=" * 70)
    print(" Назначение: Автоматизация поиска товаров и сравнения цен")
    print(" Поддерживаемые маркетплейсы:")
    print("   • komus.ru (Комус) - офисные товары")
    print("   • vseinstrumenti.ru (ВсеИнструменты) - инструменты")
    print("   • ozon.ru (Озон) - универсальный маркетплейс")
    print("   • wildberries.ru (Wildberries) - товары широкого потребления")
    print("   • officemag.ru (Офисмаг) - офисные принадлежности")
    print("=" * 70)
    
    # Инициализация всех компонентов системы
    print(" Инициализация компонентов системы...")
    try:
        await initialize_components()
        print(" Компоненты успешно инициализированы")
    except Exception as e:
        print(f" Ошибка инициализации: {e}")
        print(" Программа завершена из-за ошибки инициализации")
        sys.exit(1)
    
    # Показываем зарегистрированные MCP инструменты
    print(" Зарегистрированные MCP инструменты:")
    print("    Основные инструменты:")
    print("     1. get_product_details - детальная информация о товаре")
    print("     2. get_product_list - список всех товаров с пагинацией")
    print("     3. save_product_prices - сохранение найденных цен (5 форматов)")
    print("     4. get_statistics - комплексная статистика")
    print("    Excel инструменты:")
    print("     5. parse_excel_and_save_to_database - загрузка товаров из Excel")
    print("     6. parse_excel_file - парсинг Excel файлов")
    print("     7. get_excel_info - информация о структуре Excel")
    print("     8. export_to_excel - экспорт в Excel с форматированием")
    print("     9. filter_excel_data - фильтрация данных")
    print("     10. transform_excel_data - трансформация данных")
    print("    Лицензионные инструменты:")
    print("     11. check_license_status - проверка статуса лицензии")
    print("     12. set_license_key - установка лицензионного ключа")
    print("=" * 70)
    
    print(" Ожидание подключения MCP клиента через STDIO...")
    print(" Готов к обработке команд от ИИ-агентов!")
    await mcp.run_stdio_async()

async def run_sse_async(host: str, port: int):
    """
    Запуск MCP сервера в SSE (Server-Sent Events) режиме.
    
    SSE режим используется для веб-интеграции и отладки MCP сервера.
    В этом режиме сервер работает как HTTP сервер и может принимать
    запросы через веб-интерфейс или REST API.
    
    Полезно для:
    - Отладки MCP инструментов
    - Веб-интеграции
    - Тестирования функциональности
    - Мониторинга состояния сервера
    
    Args:
        host: IP адрес для привязки сервера
        port: Порт для HTTP сервера
    """
    print(" Запуск MCP сервера offers-check-marketplaces в режиме SSE")
    print(f" ID приложения: {APP_ID}")
    print(f" Версия Python: {sys.version}")
    print(f" Рабочая директория: {os.getcwd()}")
    print(f" Хост: {host}")
    print(f" Порт: {port}")
    print(f" URL сервера: http://{host}:{port}")
    print(f" Переменные окружения:")
    for key in ['HOST', 'PORT', 'DEBUG', 'LICENSE_KEY']:
        value = os.getenv(key, 'не установлено')
        # Скрываем лицензионный ключ для безопасности
        if key == 'LICENSE_KEY' and value != 'не установлено':
            value = value[:8] + "..." if len(value) > 8 else "***"
        print(f"   {key}: {value}")
    
    print("=" * 70)
    print(" СИСТЕМА СРАВНЕНИЯ ЦЕН НА МАРКЕТПЛЕЙСАХ (SSE РЕЖИМ)")
    print("=" * 70)
    print(" Назначение: Веб-интеграция и отладка MCP сервера")
    print(" Доступ: HTTP API для тестирования инструментов")
    print(" Мониторинг: Веб-интерфейс для отслеживания состояния")
    print("=" * 70)
    
    # Инициализация всех компонентов системы
    print(" Инициализация компонентов системы...")
    try:
        await initialize_components()
        print(" Компоненты успешно инициализированы")
    except Exception as e:
        print(f" Ошибка инициализации: {e}")
        print(" Программа завершена из-за ошибки инициализации")
        sys.exit(1)
    
    # Показываем зарегистрированные MCP инструменты
    print(" Доступные MCP инструменты через HTTP API:")
    print("    Основные инструменты:")
    print("     • get_product_details - детальная информация о товаре")
    print("     • get_product_list - список товаров с пагинацией")
    print("     • save_product_prices - сохранение цен (5 форматов)")
    print("     • get_statistics - комплексная статистика")
    print("    Excel инструменты:")
    print("     • parse_excel_and_save_to_database - загрузка из Excel")
    print("     • parse_excel_file, get_excel_info, export_to_excel")
    print("     • filter_excel_data, transform_excel_data")
    print("    Лицензионные инструменты:")
    print("     • check_license_status, set_license_key")
    print("=" * 70)
    
    print(" Запуск Uvicorn HTTP сервера...")
    print(f" Сервер будет доступен по адресу: http://{host}:{port}")
    print("📡 Готов к обработке HTTP запросов!")
    
    # Создание конфигурации и сервера Uvicorn
    config = uvicorn.Config(starlette_app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    
    # Запуск сервера в текущем event loop
    await server.serve()

def run_sse(host: str, port: int):
    """
    Синхронная обертка для запуска SSE сервера.
    
    Использует anyio для запуска асинхронной функции run_sse_async
    в синхронном контексте CLI команды.
    """
    anyio.run(run_sse_async, host, port)

# Интерфейс командной строки (CLI) для запуска MCP сервера

@click.command()
@click.option("--sse", is_flag=True, 
              help="Запуск в SSE режиме для веб-интеграции (по умолчанию STDIO для MCP клиентов)")
@click.option("--host", default=lambda: os.getenv("HOST", "0.0.0.0"),
              show_default=True, 
              help="IP адрес для SSE режима (можно задать через переменную HOST)")
@click.option("--port", type=int, default=lambda: int(os.getenv("PORT", 8000)),
              show_default=True, 
              help="Порт для SSE режима (можно задать через переменную PORT)")
def main(sse: bool, host: str, port: int):
    """
    MCP Сервер для автоматизации поиска товаров и сравнения цен на маркетплейсах.
    
    Система предоставляет инструменты для:
    • Поиска товаров на российских маркетплейсах
    • Сравнения цен между различными источниками  
    • Обработки Excel файлов с товарами
    • Генерации аналитики и статистики
    • Управления базой данных товаров и цен
    
    Режимы запуска:
    • STDIO (по умолчанию): для интеграции с MCP клиентами (Kiro, Cursor)
    • SSE (--sse): для веб-интеграции и отладки через HTTP API
    
    Примеры использования:
    • offers-check-marketplaces
    • offers-check-marketplaces --sse
    • offers-check-marketplaces --sse --host 127.0.0.1 --port 9000
    
    Переменные окружения:
    • LICENSE_KEY: лицензионный ключ (обязательно)
    • HOST: IP адрес для SSE режима
    • PORT: порт для SSE режима
    • DEBUG: уровень отладки
    """
    print("=" * 80)
    print("ЗАПУСК MCP СЕРВЕРА СРАВНЕНИЯ ЦЕН НА МАРКЕТПЛЕЙСАХ")
    print("=" * 80)
    print(f" Режим запуска: {' SSE (Server-Sent Events)' if sse else ' STDIO (MCP Protocol)'}")
    print(f" Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f" Платформа: {sys.platform}")
    print(f" Домашняя директория: {os.path.expanduser('~')}")
    print(f" Версия Python: {sys.version.split()[0]}")
    
    if sse:
        print(f" Сетевые параметры: {host}:{port}")
        print(f" URL доступа: http://{host}:{port}")
    
    print("=" * 80)
    print(" НАЗНАЧЕНИЕ: Автоматизация поиска и сравнения цен товаров")
    print(" МАРКЕТПЛЕЙСЫ: Комус, ВсеИнструменты, Озон, Wildberries, Офисмаг")
    print(" ИНТЕГРАЦИЯ: MCP Protocol для ИИ-агентов")
    print("=" * 80)
    
    # Запуск в соответствующем режиме
    if sse:
        print(" Запуск в SSE режиме для веб-интеграции...")
        run_sse(host, port)
    else:
        print(" Запуск в STDIO режиме для MCP клиентов...")
        anyio.run(run_stdio)

if __name__ == "__main__":
    main()