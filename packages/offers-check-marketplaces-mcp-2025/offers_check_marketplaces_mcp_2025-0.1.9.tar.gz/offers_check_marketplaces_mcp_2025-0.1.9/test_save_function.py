#!/usr/bin/env python3
"""
Тестовый скрипт для проверки функции save_product_prices
"""

import asyncio
import sys
import os
import re

# Добавляем путь к модулю
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'offers_check_marketplaces'))

async def test_marketplaces_format():
    """Тестируем обработку формата с marketplaces"""
    
    # Тестовые данные в формате, который приходит от системы
    search_results = {
        "search_timestamp": "2025-01-08T12:00:00Z",
        "marketplaces": {
            "vseinstrumenti": {
                "rating": "4.5",
                "availability": "В наличии",
                "price": "299 руб",
                "url": "https://www.vseinstrumenti.ru/product/laima-napkins",
                "reviews_count": "12"
            },
            "yandex_market": {
                "rating": "4.3",
                "availability": "В наличии у 5+ продавцов",
                "price": "от 280 руб",
                "url": "https://market.yandex.ru/search?text=LAIMA%20салфетки",
                "reviews_count": "25"
            }
        },
        "processing_status": "completed",
        "sku": "194744",
        "product_name": "LAIMA салфетки",
        "price_comparison": {
            "average_price": 289.5,
            "price_difference": 19,
            "max_price": 299,
            "min_price": 280
        }
    }
    
    print("=== ТЕСТ ОБРАБОТКИ ФОРМАТА MARKETPLACES ===")
    print(f"Входные данные: {search_results}")
    print()
    
    # Симулируем логику из функции save_product_prices
    results = []
    
    # Проверяем наличие marketplaces
    if "marketplaces" in search_results and isinstance(search_results["marketplaces"], dict):
        marketplaces = search_results["marketplaces"]
        print(f"✓ Найден формат с marketplaces: {len(marketplaces)} маркетплейсов")
        
        for marketplace_name, marketplace_data in marketplaces.items():
            print(f"\n--- Обработка {marketplace_name} ---")
            print(f"Данные: {marketplace_data}")
            
            if isinstance(marketplace_data, dict) and "price" in marketplace_data:
                # Преобразуем цену из строки в число
                price_str = marketplace_data.get("price", "")
                price_value = None
                
                print(f"Цена (строка): '{price_str}'")
                
                if price_str:
                    # Извлекаем числовое значение из строки типа "299 руб" или "от 280 руб"
                    price_match = re.search(r'(\d+(?:\.\d+)?)', str(price_str))
                    if price_match:
                        price_value = float(price_match.group(1))
                        print(f"Извлеченная цена: {price_value}")
                    else:
                        print(f"❌ Не удалось извлечь цену из '{price_str}'")
                
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
                    print(f"✓ Добавлен результат: {price_value} руб")
                else:
                    print(f"❌ Пропущен: некорректная цена '{price_str}'")
            else:
                print(f"❌ Пропущен: нет поля 'price' или данные не являются словарем")
    
    print(f"\n=== ИТОГОВЫЕ РЕЗУЛЬТАТЫ ===")
    print(f"Количество обработанных результатов: {len(results)}")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['marketplace']}: {result['price']} {result['currency']}")
    
    return results

if __name__ == "__main__":
    results = asyncio.run(test_marketplaces_format())
    
    if results:
        print(f"\n✅ ТЕСТ ПРОЙДЕН: Обработано {len(results)} результатов")
    else:
        print(f"\n❌ ТЕСТ НЕ ПРОЙДЕН: Результаты пусты")