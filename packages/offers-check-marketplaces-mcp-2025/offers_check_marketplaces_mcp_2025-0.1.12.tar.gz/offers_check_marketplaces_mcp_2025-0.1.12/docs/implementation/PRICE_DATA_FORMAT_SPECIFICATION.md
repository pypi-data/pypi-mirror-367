# Спецификация форматов данных для сохранения цен

## Обзор

Данный документ определяет точные форматы данных для функции `save_product_prices`, которые должен использовать ИИ-агент при сохранении найденных цен товаров.

## Функция save_product_prices

```python
save_product_prices(product_code: float, search_results: dict) -> dict
```

### Параметры

- `product_code` - код товара из базы данных (число)
- `search_results` - словарь с результатами поиска цен (поддерживает 5 различных форматов)

## Поддерживаемые форматы данных

### Формат 1: Основной формат системы (РЕКОМЕНДУЕТСЯ)

```json
{
  "search_timestamp": "2025-01-08T12:00:00Z",
  "sku": "194744",
  "product_name": "LAIMA салфетки",
  "processing_status": "completed",
  "marketplaces": {
    "vseinstrumenti": {
      "price": "299 руб",
      "availability": "В наличии",
      "url": "https://www.vseinstrumenti.ru/product/laima-napkins",
      "rating": "4.5",
      "reviews_count": "12"
    },
    "yandex_market": {
      "price": "от 280 руб",
      "availability": "В наличии у 5+ продавцов",
      "url": "https://market.yandex.ru/search?text=LAIMA%20салфетки",
      "rating": "4.3",
      "reviews_count": "25"
    }
  },
  "price_comparison": {
    "average_price": 289.5,
    "price_difference": 19,
    "max_price": 299,
    "min_price": 280
  }
}
```

**Особенности:**

- Цена может быть строкой с текстом ("299 руб", "от 280 руб")
- Система автоматически извлекает числовое значение с помощью регулярного выражения
- Поддерживает дополнительные поля: rating, reviews_count, availability
- Включает метаданные поиска и сравнение цен

### Формат 2: Массив результатов

```json
{
  "results": [
    {
      "marketplace": "komus.ru",
      "price": 1250.0,
      "currency": "RUB",
      "availability": "в наличии",
      "product_url": "https://www.komus.ru/product/12345",
      "product_found": true
    },
    {
      "marketplace": "vseinstrumenti.ru",
      "price": 1320.0,
      "currency": "RUB",
      "availability": "в наличии",
      "product_url": "https://www.vseinstrumenti.ru/product/67890",
      "product_found": true
    }
  ]
}
```

### Формат 3: Массив найденных предложений

```json
{
  "found_offers": [
    {
      "marketplace": "ozon.ru",
      "price": 890.5,
      "currency": "RUB",
      "availability": "доступен",
      "product_url": "https://www.ozon.ru/product/123456789"
    },
    {
      "marketplace": "wildberries.ru",
      "price": 945.0,
      "currency": "RUB",
      "availability": "в наличии",
      "product_url": "https://www.wildberries.ru/catalog/12345/detail.aspx"
    }
  ]
}
```

**Примечание:** Для формата `found_offers` поле `product_found` автоматически устанавливается в `true`.

### Формат 4: Одиночный результат

```json
{
  "marketplace": "officemag.ru",
  "price": 567.0,
  "currency": "RUB",
  "availability": "в наличии",
  "product_url": "https://www.officemag.ru/product/abc123",
  "product_found": true
}
```

### Формат 5: Прямой массив

```json
[
  {
    "marketplace": "komus.ru",
    "price": 1250.0,
    "currency": "RUB",
    "availability": "в наличии",
    "product_url": "https://www.komus.ru/product/12345"
  },
  {
    "marketplace": "vseinstrumenti.ru",
    "price": 1320.0,
    "currency": "RUB",
    "availability": "в наличии",
    "product_url": "https://www.vseinstrumenti.ru/product/67890"
  }
]
```

**Примечание:** Для прямого массива поле `product_found` автоматически устанавливается в `true`.

## Обязательные поля

### Минимально необходимые поля для каждого результата:

1. **`marketplace`** (string) - название маркетплейса
2. **`price`** (number или string) - цена товара

### Рекомендуемые поля:

3. **`currency`** (string) - валюта (по умолчанию "RUB")
4. **`availability`** (string) - статус наличия товара
5. **`product_url`** (string) - ссылка на страницу товара
6. **`product_found`** (boolean) - найден ли товар (по умолчанию true)

### Дополнительные поля (опциональные):

7. **`rating`** (string) - рейтинг товара
8. **`reviews_count`** (string) - количество отзывов
9. **`error_message`** (string) - сообщение об ошибке (если есть)

## Обработка цен

### Поддерживаемые форматы цен:

1. **Числовые значения**: `1250.0`, `890`, `567.99`
2. **Строки с числами**: `"1250"`, `"890.5"`
3. **Строки с текстом**: `"299 руб"`, `"1 250,00 ₽"`, `"от 280 руб"`

### Алгоритм извлечения цены:

```python
import re

def extract_price(price_str):
    """Извлекает числовое значение цены из строки"""
    if isinstance(price_str, (int, float)):
        return float(price_str)

    price_match = re.search(r'(\d+(?:\.\d+)?)', str(price_str))
    if price_match:
        return float(price_match.group(1))

    return None
```

**Примеры:**

- `"299 руб"` → `299.0`
- `"от 280 руб"` → `280.0`
- `"1 250,00 ₽"` → `1.0` (берется первое число)
- `"1250.50"` → `1250.5`

## Валидация данных

### Проверки при сохранении:

1. **Код товара** должен существовать в базе данных
2. **Цена** должна быть положительным числом (> 0)
3. **Маркетплейс** должен быть указан
4. **product_found** должен быть `true` (если указан)

### Обработка ошибок:

- Некорректные цены пропускаются с предупреждением
- Товары с `product_found: false` игнорируются
- Отсутствующие обязательные поля вызывают ошибку

## Примеры использования

### Пример 1: Сохранение цен в основном формате

```python
# Данные от ИИ-агента
search_results = {
    "marketplaces": {
        "komus.ru": {
            "price": "1250 руб",
            "availability": "в наличии",
            "url": "https://www.komus.ru/product/12345"
        },
        "vseinstrumenti.ru": {
            "price": "1320.50 руб",
            "availability": "доступен для заказа",
            "url": "https://www.vseinstrumenti.ru/product/67890"
        }
    }
}

# Вызов функции
result = await save_product_prices(195385.0, search_results)
```

### Пример 2: Сохранение одиночного результата

```python
search_results = {
    "marketplace": "ozon.ru",
    "price": 890.5,
    "currency": "RUB",
    "availability": "в наличии",
    "product_url": "https://www.ozon.ru/product/123456789",
    "product_found": true
}

result = await save_product_prices(194744.0, search_results)
```

### Пример 3: Сохранение массива результатов

```python
search_results = {
    "results": [
        {
            "marketplace": "wildberries.ru",
            "price": 945.0,
            "availability": "в наличии",
            "product_url": "https://www.wildberries.ru/catalog/12345/detail.aspx",
            "product_found": true
        },
        {
            "marketplace": "officemag.ru",
            "price": 567.0,
            "availability": "под заказ",
            "product_url": "https://www.officemag.ru/product/abc123",
            "product_found": true
        }
    ]
}

result = await save_product_prices(195386.0, search_results)
```

## Ответы функции

### Успешное сохранение:

```json
{
  "status": "success",
  "message": "Сохранено 2 цен для товара 195385.0",
  "product_code": 195385.0,
  "product_name": "Полотно техническое БЯЗЬ ОТБЕЛЕННАЯ ГОСТ",
  "saved_prices": 2,
  "total_results": 2,
  "prices_saved": [
    {
      "marketplace": "komus.ru",
      "price": 1250.0,
      "currency": "RUB",
      "availability": "в наличии"
    },
    {
      "marketplace": "vseinstrumenti.ru",
      "price": 1320.5,
      "currency": "RUB",
      "availability": "доступен для заказа"
    }
  ],
  "timestamp": "2025-01-08T15:30:45.123456"
}
```

### Ошибка - товар не найден:

```json
{
  "status": "not_found",
  "message": "Продукт с кодом 999999.0 не найден",
  "error_code": "PRODUCT_NOT_FOUND",
  "user_message": "Товар с указанным кодом не найден в базе данных",
  "recoverable": false,
  "retry_suggested": false
}
```

### Ошибка - нет данных для сохранения:

```json
{
  "status": "no_data",
  "message": "Нет результатов поиска для сохранения",
  "user_message": "Результаты поиска пусты, нечего сохранять",
  "diagnostic_info": {
    "received_keys": ["search_timestamp", "marketplaces"],
    "has_marketplaces": true,
    "marketplaces_count": 2,
    "komus.ru_has_price": false,
    "vseinstrumenti.ru_has_price": true
  },
  "recoverable": true,
  "retry_suggested": false
}
```

## Рекомендации для ИИ-агента

### 1. Используйте основной формат (marketplaces)

Это наиболее гибкий и информативный формат, который поддерживает дополнительные метаданные.

### 2. Всегда указывайте URL товара

Поле `product_url` критически важно для верификации найденных цен.

### 3. Проверяйте соответствие товара

Убедитесь, что найденный товар действительно соответствует искомому.

### 4. Обрабатывайте ошибки

Проверяйте ответ функции и обрабатывайте различные статусы ошибок.

### 5. Используйте осмысленные названия маркетплейсов

Предпочтительные названия: `komus.ru`, `vseinstrumenti.ru`, `ozon.ru`, `wildberries.ru`, `officemag.ru`.

## Диагностика проблем

### Если цены не сохраняются:

1. Проверьте формат данных - используйте один из 5 поддерживаемых форматов
2. Убедитесь, что цены являются положительными числами
3. Проверьте, что товар с указанным кодом существует в базе данных
4. Изучите поле `diagnostic_info` в ответе для детальной диагностики

### Логирование:

Функция подробно логирует процесс обработки данных. Проверьте логи для понимания причин ошибок.

## Заключение

Данная спецификация обеспечивает гибкость в форматах данных при сохранении строгих требований к качеству. ИИ-агент может использовать любой из 5 поддерживаемых форматов в зависимости от источника данных и контекста поиска.
