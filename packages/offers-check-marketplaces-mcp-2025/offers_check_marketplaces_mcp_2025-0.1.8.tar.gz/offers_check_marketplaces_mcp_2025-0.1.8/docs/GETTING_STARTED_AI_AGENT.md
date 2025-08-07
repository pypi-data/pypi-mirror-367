# Быстрый старт для ИИ-агента

## 🚀 Добро пожаловать!

Вы работаете с MCP сервером **offers-check-marketplaces** - системой автоматизации поиска товаров и сравнения цен на маркетплейсах.

## ⚡ Быстрый старт (5 минут)

### 1. Проверьте подключение

```python
result = await test_connection()
# Должен вернуть: {"status": "success", "message": "MCP сервер работает корректно"}
```

### 2. Получите список товаров

```python
products = await get_product_list(limit=5)
# Получите первые 5 товаров для тестирования
```

### 3. Сохраните цену товара

```python
search_results = {
    "marketplaces": {
        "komus.ru": {
            "price": "1250 руб",
            "availability": "в наличии",
            "url": "https://www.komus.ru/product/12345"
        }
    }
}

result = await save_product_prices(195385.0, search_results)
```

### 4. Проверьте результат

```python
details = await get_product_details(195385.0)
# Увидите сохраненную цену в разделе "prices"
```

## 📋 Основные инструменты

| Инструмент              | Назначение     | Документация                                                                            |
| ----------------------- | -------------- | --------------------------------------------------------------------------------------- |
| `get_product_list()`    | Список товаров | [MCP_TOOL_USAGE_GUIDE.md](implementation/MCP_TOOL_USAGE_GUIDE.md#2-get_product_list)    |
| `save_product_prices()` | Сохранение цен | [AI_AGENT_PRICE_FORMAT_GUIDE.md](implementation/AI_AGENT_PRICE_FORMAT_GUIDE.md)         |
| `get_product_details()` | Детали товара  | [MCP_TOOL_USAGE_GUIDE.md](implementation/MCP_TOOL_USAGE_GUIDE.md#1-get_product_details) |
| `get_statistics()`      | Статистика     | [MCP_TOOL_USAGE_GUIDE.md](implementation/MCP_TOOL_USAGE_GUIDE.md#4-get_statistics)      |

## 🎯 Рекомендуемый формат для цен

**Используйте этот формат в первую очередь:**

```json
{
  "marketplaces": {
    "НАЗВАНИЕ_МАРКЕТПЛЕЙСА": {
      "price": "ЦЕНА_С_ТЕКСТОМ",
      "availability": "СТАТУС_НАЛИЧИЯ",
      "url": "ССЫЛКА_НА_ТОВАР"
    }
  }
}
```

**Стандартные названия маркетплейсов:**

- `komus.ru`
- `vseinstrumenti.ru`
- `ozon.ru`
- `wildberries.ru`
- `officemag.ru`

## 📚 Полная документация

### Для быстрого доступа:

- **[Шпаргалка по форматам](guides/PRICE_FORMAT_CHEAT_SHEET.md)** - самое необходимое на одной странице

### Для изучения:

- **[Руководство по форматам](implementation/AI_AGENT_PRICE_FORMAT_GUIDE.md)** - подробное описание всех форматов
- **[Примеры использования](implementation/AI_AGENT_EXAMPLES.md)** - практические сценарии
- **[Все MCP инструменты](implementation/MCP_TOOL_USAGE_GUIDE.md)** - полный справочник

### Для разработчиков:

- **[Техническая спецификация](implementation/PRICE_DATA_FORMAT_SPECIFICATION.md)** - детальные технические требования

## ⚠️ Важные правила

### ✅ ОБЯЗАТЕЛЬНО:

- Переходить на страницы товаров на маркетплейсах
- Указывать URL товара в поле `url` или `product_url`
- Использовать стандартные названия маркетплейсов
- Проверять, что цена больше 0

### ❌ ЗАПРЕЩЕНО:

- Брать цены из Google/Yandex поиска
- Использовать цены из поисковых сниппетов
- Сохранять цены товаров "нет в наличии"
- Использовать нестандартные названия маркетплейсов

## 🔧 Диагностика проблем

### Если цены не сохраняются:

1. **Проверьте формат данных** - используйте рекомендуемый формат выше
2. **Проверьте код товара** - товар должен существовать в базе данных
3. **Изучите поле `diagnostic_info`** в ответе функции
4. **Проверьте цену** - она должна быть больше 0

### При ошибке "no_data":

```json
{
  "status": "no_data",
  "diagnostic_info": {
    "received_keys": ["marketplaces"],
    "has_marketplaces": true,
    "komus.ru_has_price": false // ← Проблема здесь!
  }
}
```

## 🎉 Готовы начать?

1. Изучите [шпаргалку](guides/PRICE_FORMAT_CHEAT_SHEET.md) (2 минуты)
2. Попробуйте [примеры](implementation/AI_AGENT_EXAMPLES.md) (10 минут)
3. Начните работать с реальными товарами!

---

**Удачи в автоматизации поиска цен! 🛒💰**
