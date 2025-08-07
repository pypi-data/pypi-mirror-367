# Примеры использования для ИИ-агента

## Обзор

Данный документ содержит практические примеры использования MCP инструментов системы сравнения цен на маркетплейсах для ИИ-агентов.

## 🎯 БАЗОВЫЕ СЦЕНАРИИ

### Сценарий 1: Поиск цены на одном маркетплейсе

**Задача:** Найти цену товара на конкретном маркетплейсе и сохранить результат.

**Шаги:**

1. **Получить информацию о товаре:**

```python
product_details = await get_product_details(195385.0)
```

2. **Найти товар на маркетплейсе** (используя MCP Playwright):

```python
# Переход на komus.ru
await browser.navigate("https://www.komus.ru")

# Поиск товара
search_input = await browser.find_element("input[name='q']")
await search_input.type("Полотно техническое БЯЗЬ ОТБЕЛЕННАЯ")
await search_input.press("Enter")

# Переход на страницу товара
first_product = await browser.find_element(".product-item:first-child a")
product_url = await first_product.get_attribute("href")
await browser.navigate(product_url)

# Извлечение цены
price_element = await browser.find_element(".price-current")
price_text = await price_element.text()
availability_element = await browser.find_element(".availability")
availability_text = await availability_element.text()
```

3. **Сохранить найденную цену:**

```python
search_results = {
    "marketplaces": {
        "komus.ru": {
            "price": price_text,  # например, "1250 руб"
            "availability": availability_text,  # например, "в наличии"
            "url": product_url
        }
    }
}

result = await save_product_prices(195385.0, search_results)
```

### Сценарий 2: Поиск цен на нескольких маркетплейсах

**Задача:** Найти цены товара на 3-х маркетплейсах и сравнить их.

**Шаги:**

1. **Получить информацию о товаре:**

```python
product_details = await get_product_details(194744.0)
product_name = product_details["product"]["model_name"]
```

2. **Поиск на komus.ru:**

```python
# ... код поиска на komus.ru ...
komus_price = "299 руб"
komus_url = "https://www.komus.ru/product/12345"
```

3. **Поиск на vseinstrumenti.ru:**

```python
# ... код поиска на vseinstrumenti.ru ...
vsei_price = "320.50 руб"
vsei_url = "https://www.vseinstrumenti.ru/product/67890"
```

4. **Поиск на ozon.ru:**

```python
# ... код поиска на ozon.ru ...
ozon_price = "285 руб"
ozon_url = "https://www.ozon.ru/product/123456789"
```

5. **Сохранить все найденные цены:**

```python
search_results = {
    "marketplaces": {
        "komus.ru": {
            "price": komus_price,
            "availability": "в наличии",
            "url": komus_url
        },
        "vseinstrumenti.ru": {
            "price": vsei_price,
            "availability": "доступен для заказа",
            "url": vsei_url
        },
        "ozon.ru": {
            "price": ozon_price,
            "availability": "в наличии",
            "url": ozon_url
        }
    }
}

result = await save_product_prices(194744.0, search_results)
```

### Сценарий 3: Массовая обработка товаров

**Задача:** Обработать первые 10 товаров из базы данных.

**Шаги:**

1. **Получить список товаров:**

```python
products_list = await get_product_list(limit=10)
products = products_list["products"]
```

2. **Обработать каждый товар:**

```python
for product in products:
    product_code = product["sku"]
    product_name = product["model_name"]

    print(f"Обрабатываю товар: {product_name} (код: {product_code})")

    # Поиск цен на маркетплейсах
    search_results = await search_product_prices(product_name)

    # Сохранение результатов
    if search_results:
        result = await save_product_prices(product_code, search_results)
        print(f"Сохранено {result.get('saved_prices', 0)} цен")
    else:
        print("Цены не найдены")
```

## 🔧 ПРОДВИНУТЫЕ СЦЕНАРИИ

### Сценарий 4: Обработка с фильтрацией по категориям

**Задача:** Найти цены только для товаров категории "Хозтовары и посуда".

```python
# 1. Получить все товары
all_products = await get_product_list(limit=1000)

# 2. Фильтровать по категории
household_products = [
    product for product in all_products["products"]
    if product["category"] == "Хозтовары и посуда"
]

# 3. Обработать отфильтрованные товары
for product in household_products[:5]:  # Первые 5 товаров
    # ... поиск и сохранение цен ...
    pass
```

### Сценарий 5: Обработка с приоритетными источниками

**Задача:** Искать цены в первую очередь в приоритетных источниках товара.

```python
product_details = await get_product_details(195385.0)
product = product_details["product"]

priority_1 = product["priority_1_source"]  # например, "Комус"
priority_2 = product["priority_2_source"]  # например, "ВсеИнструменты"

# Маппинг названий на URL
marketplace_mapping = {
    "Комус": "komus.ru",
    "ВсеИнструменты": "vseinstrumenti.ru",
    "Озон": "ozon.ru"
}

# Поиск в приоритетном порядке
search_results = {"marketplaces": {}}

for priority_source in [priority_1, priority_2]:
    if priority_source in marketplace_mapping:
        marketplace_url = marketplace_mapping[priority_source]

        # Поиск на приоритетном маркетплейсе
        price_data = await search_on_marketplace(marketplace_url, product["model_name"])

        if price_data:
            search_results["marketplaces"][marketplace_url] = price_data

# Сохранение результатов
if search_results["marketplaces"]:
    result = await save_product_prices(product["code"], search_results)
```

## 📊 РАБОТА С EXCEL

### Сценарий 6: Загрузка товаров из Excel файла

**Задача:** Загрузить товары из Excel файла в базу данных.

```python
# 1. Получить информацию о файле
file_info = await get_excel_info("data/Таблица на вход.xlsx")
print(f"Листы в файле: {file_info['sheets']}")
print(f"Колонки: {file_info['columns']}")

# 2. Загрузить товары частями (по 150 штук)
total_rows = file_info["total_rows"]
batch_size = 150

for start_row in range(0, total_rows, batch_size):
    result = await parse_excel_and_save_to_database(
        "data/Таблица на вход.xlsx",
        start_row=start_row,
        max_rows=batch_size
    )

    print(f"Загружено товаров: {result['products_created']}")
    print(f"Обновлено товаров: {result['products_updated']}")
```

### Сценарий 7: Экспорт результатов в Excel

**Задача:** Создать отчет с найденными ценами.

```python
# 1. Получить статистику
stats = await get_statistics()

# 2. Получить товары с ценами
products_with_prices = await get_product_list(filter_status="processed")

# 3. Подготовить данные для экспорта
export_data = []
for product in products_with_prices["products"]:
    details = await get_product_details(product["sku"])

    if details["status"] == "success" and details.get("prices"):
        for price_info in details["prices"]:
            export_data.append({
                "Код товара": product["sku"],
                "Название": product["model_name"],
                "Категория": product["category"],
                "Маркетплейс": price_info["marketplace"],
                "Цена": price_info["price"],
                "Валюта": price_info["currency"],
                "Наличие": price_info["availability"],
                "URL": price_info["product_url"],
                "Дата поиска": price_info["scraped_at"]
            })

# 4. Экспортировать в Excel
result = await export_to_excel(
    export_data,
    "data/отчет_по_ценам.xlsx",
    sheet_name="Найденные цены",
    apply_formatting=True
)
```

## ❌ ОБРАБОТКА ОШИБОК

### Пример обработки различных типов ошибок:

```python
async def safe_save_prices(product_code, search_results):
    """Безопасное сохранение цен с обработкой ошибок"""

    try:
        result = await save_product_prices(product_code, search_results)

        if result["status"] == "success":
            print(f"✅ Успешно сохранено {result['saved_prices']} цен")
            return True

        elif result["status"] == "not_found":
            print(f"❌ Товар с кодом {product_code} не найден в базе данных")
            return False

        elif result["status"] == "no_data":
            print(f"⚠️ Нет данных для сохранения")
            print(f"Диагностика: {result.get('diagnostic_info', {})}")
            return False

        else:
            print(f"❌ Неизвестная ошибка: {result.get('message', 'Нет описания')}")
            return False

    except Exception as e:
        print(f"💥 Исключение при сохранении цен: {e}")
        return False
```

## 🔍 ДИАГНОСТИКА И ОТЛАДКА

### Проверка качества найденных цен:

```python
def validate_price_data(price_data):
    """Валидация данных о цене перед сохранением"""

    required_fields = ["marketplace", "price"]
    for field in required_fields:
        if field not in price_data:
            print(f"❌ Отсутствует обязательное поле: {field}")
            return False

    # Проверка цены
    price = price_data["price"]
    if isinstance(price, str):
        # Попытка извлечь число из строки
        import re
        price_match = re.search(r'(\d+(?:\.\d+)?)', price)
        if not price_match:
            print(f"❌ Не удалось извлечь цену из строки: {price}")
            return False
        price_value = float(price_match.group(1))
    else:
        price_value = float(price)

    if price_value <= 0:
        print(f"❌ Некорректная цена: {price_value}")
        return False

    # Проверка URL
    if "url" in price_data or "product_url" in price_data:
        url = price_data.get("url") or price_data.get("product_url")
        if not url.startswith("http"):
            print(f"⚠️ Подозрительный URL: {url}")

    print(f"✅ Данные о цене валидны: {price_data['marketplace']} - {price}")
    return True

# Использование:
if validate_price_data(price_data):
    # Сохранить цену
    pass
else:
    # Пропустить некорректные данные
    pass
```

## 📈 МОНИТОРИНГ ПРОГРЕССА

### Отслеживание прогресса обработки:

```python
async def process_products_with_progress():
    """Обработка товаров с отслеживанием прогресса"""

    # Получить общее количество товаров
    stats = await get_statistics()
    total_products = stats["statistics"]["total_products"]

    print(f"Всего товаров для обработки: {total_products}")

    processed_count = 0
    success_count = 0

    # Обработка по батчам
    batch_size = 50
    for offset in range(0, total_products, batch_size):
        products_batch = await get_product_list(offset=offset, limit=batch_size)

        for product in products_batch["products"]:
            processed_count += 1

            # Поиск и сохранение цен
            search_results = await search_product_prices(product["model_name"])

            if search_results:
                result = await save_product_prices(product["sku"], search_results)
                if result["status"] == "success":
                    success_count += 1

            # Показать прогресс
            progress = (processed_count / total_products) * 100
            print(f"Прогресс: {progress:.1f}% ({processed_count}/{total_products}), "
                  f"успешно: {success_count}")

    print(f"Обработка завершена! Успешно обработано: {success_count}/{processed_count}")
```

## 🎯 ЛУЧШИЕ ПРАКТИКИ

### 1. Всегда проверяйте статус ответа:

```python
result = await get_product_details(product_code)
if result["status"] != "success":
    print(f"Ошибка: {result.get('message', 'Неизвестная ошибка')}")
    return
```

### 2. Используйте правильные названия маркетплейсов:

```python
# ✅ Правильно
marketplace_names = ["komus.ru", "vseinstrumenti.ru", "ozon.ru"]

# ❌ Неправильно
marketplace_names = ["komus", "vse-instrumenty", "ozon"]
```

### 3. Всегда указывайте URL товара:

```python
search_results = {
    "marketplaces": {
        "komus.ru": {
            "price": "1250 руб",
            "availability": "в наличии",
            "url": product_url  # ОБЯЗАТЕЛЬНО!
        }
    }
}
```

### 4. Обрабатывайте большие объемы данных по частям:

```python
# Обработка по 150 товаров за раз
for offset in range(0, total_count, 150):
    batch = await get_product_list(offset=offset, limit=150)
    # ... обработка батча ...
```

---

**Эти примеры покрывают основные сценарии использования MCP инструментов для автоматизации поиска и сравнения цен на маркетплейсах.**
