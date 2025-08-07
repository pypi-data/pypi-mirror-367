import re

# Тестируем извлечение цены
test_prices = [
    "299 руб",
    "от 280 руб", 
    "1250.50 рублей",
    "123",
    "45.67",
    "нет цены",
    ""
]

print("=== ТЕСТ ИЗВЛЕЧЕНИЯ ЦЕН ===")
for price_str in test_prices:
    print(f"Входная строка: '{price_str}'")
    
    if price_str:
        price_match = re.search(r'(\d+(?:\.\d+)?)', str(price_str))
        if price_match:
            price_value = float(price_match.group(1))
            print(f"  ✓ Извлечена цена: {price_value}")
        else:
            print(f"  ❌ Цена не найдена")
    else:
        print(f"  ❌ Пустая строка")
    print()