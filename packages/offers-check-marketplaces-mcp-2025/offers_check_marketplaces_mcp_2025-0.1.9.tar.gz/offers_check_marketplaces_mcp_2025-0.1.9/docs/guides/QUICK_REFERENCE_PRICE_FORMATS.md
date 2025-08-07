# Быстрая справка: Форматы данных для save_product_prices

## Основной формат (РЕКОМЕНДУЕТСЯ)

```json
{
  "marketplaces": {
    "komus.ru": {
      "price": "1250 руб",
      "availability": "в наличии",
      "url": "https://www.komus.ru/product/12345"
    },
    "vseinstrumenti.ru": {
      "price": "1320.50 руб",
      "availability": "доступен",
      "url": "https://www.vseinstrumenti.ru/product/67890"
    }
  }
}
```

## Альтернативные форматы

### Массив результатов

```json
{
  "results": [
    {
      "marketplace": "ozon.ru",
      "price": 890.5,
      "currency": "RUB",
      "availability": "в наличии",
      "product_url": "https://www.ozon.ru/product/123456789",
      "product_found": true
    }
  ]
}
```

### Одиночный результат

```json
{
  "marketplace": "wildberries.ru",
  "price": 945.0,
  "currency": "RUB",
  "availability": "в наличии",
  "product_url": "https://www.wildberries.ru/catalog/12345/detail.aspx",
  "product_found": true
}
```

### Прямой массив

```json
[
  {
    "marketplace": "officemag.ru",
    "price": 567.0,
    "currency": "RUB",
    "availability": "в наличии",
    "product_url": "https://www.officemag.ru/product/abc123"
  }
]
```

## Обязательные поля

- ✅ **`marketplace`** - название маркетплейса
- ✅ **`price`** - цена (число или строка с числом)

## Рекомендуемые поля

- 🔸 **`currency`** - валюта (по умолчанию "RUB")
- 🔸 **`availability`** - статус наличия
- 🔸 **`product_url`** - ссылка на товар (ВАЖНО для верификации)
- 🔸 **`product_found`** - найден ли товар (по умолчанию true)

## Поддерживаемые форматы цен

- `1250.0` - число
- `"1250"` - строка с числом
- `"299 руб"` - строка с текстом (извлекается 299)
- `"от 280 руб"` - строка с префиксом (извлекается 280)

## Пример вызова

```python
result = await save_product_prices(195385.0, search_results)
```

## Успешный ответ

```json
{
  "status": "success",
  "message": "Сохранено 2 цен для товара 195385.0",
  "product_code": 195385.0,
  "saved_prices": 2,
  "prices_saved": [
    {
      "marketplace": "komus.ru",
      "price": 1250.0,
      "currency": "RUB",
      "availability": "в наличии"
    }
  ]
}
```

## Частые ошибки

❌ **Нулевая цена**: `"price": 0`  
❌ **Товар не найден**: `"product_found": false`  
❌ **Отсутствует маркетплейс**: без поля `marketplace`  
❌ **Неверный код товара**: товар не существует в БД

## Диагностика

При ошибке `"status": "no_data"` проверьте поле `diagnostic_info` в ответе для детальной информации о проблеме.
