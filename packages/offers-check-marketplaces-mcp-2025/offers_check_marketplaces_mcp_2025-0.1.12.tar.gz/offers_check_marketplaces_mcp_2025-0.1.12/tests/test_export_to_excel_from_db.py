"""
Тесты для экспорта данных из базы данных в Excel файл.
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path
import pandas as pd

from offers_check_marketplaces.database_manager import DatabaseManager
from offers_check_marketplaces.excel_tools import ExcelTools
from offers_check_marketplaces.user_data_manager import UserDataManager


@pytest.fixture
async def temp_db_manager():
    """Создает временный менеджер базы данных для тестов."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Создаем временный UserDataManager
        user_data_manager = UserDataManager()
        # Переопределяем путь к базе данных на временный
        user_data_manager.data_dir = Path(temp_dir)
        
        db_manager = DatabaseManager(user_data_manager)
        await db_manager.init_database()
        
        yield db_manager


@pytest.fixture
def excel_tools():
    """Создает экземпляр ExcelTools для тестов."""
    return ExcelTools()


@pytest.mark.asyncio
async def test_export_empty_database(temp_db_manager, excel_tools):
    """Тестирует экспорт из пустой базы данных."""
    # Получаем данные из пустой базы
    data = await temp_db_manager.get_products_with_prices_for_export()
    
    # Проверяем, что данных нет
    assert data == []


@pytest.mark.asyncio
async def test_export_products_with_prices(temp_db_manager, excel_tools):
    """Тестирует экспорт продуктов с ценами."""
    # Добавляем тестовые продукты
    test_products = [
        {
            "code": 12345.0,
            "model_name": "Тестовый продукт 1",
            "category": "Электроника",
            "unit": "шт",
            "priority_1_source": "wildberries",
            "priority_2_source": "ozon"
        },
        {
            "code": 67890.0,
            "model_name": "Тестовый продукт 2",
            "category": "Бытовая техника",
            "unit": "шт",
            "priority_1_source": "wildberries",
            "priority_2_source": "ozon"
        }
    ]
    
    # Сохраняем продукты
    product_ids = []
    for product in test_products:
        product_id = await temp_db_manager.save_product(product)
        product_ids.append(product_id)
    
    # Добавляем цены
    prices_data = [
        {
            "product_id": product_ids[0],
            "prices": {
                "wildberries": {"price": 1000.0, "product_url": "https://wb.ru/product1"},
                "ozon": {"price": 1200.0, "product_url": "https://ozon.ru/product1"}
            }
        },
        {
            "product_id": product_ids[1],
            "prices": {
                "wildberries": {"price": 2000.0, "product_url": "https://wb.ru/product2"},
                "ozon": {"price": 1800.0, "product_url": "https://ozon.ru/product2"}
            }
        }
    ]
    
    for price_data in prices_data:
        await temp_db_manager.update_product_prices(
            price_data["product_id"], 
            price_data["prices"]
        )
    
    # Получаем данные для экспорта
    export_data = await temp_db_manager.get_products_with_prices_for_export()
    
    # Проверяем структуру данных
    assert len(export_data) == 2
    
    # Проверяем первый продукт
    product1 = export_data[0]
    expected_keys = [
        "Код\nмодели", "model_name", "Категория", "Единица измерения",
        "Приоритет \n1 Источники", "Приоритет \n2 Источники",
        "Цена позиции\nМП c НДС", "Цена позиции\nB2C c НДС",
        "Дельта в процентах", "Ссылка \nна источник",
        "Цена 2 позиции\nB2C c НДС", "Ссылка \nна источник 2"
    ]
    
    for key in expected_keys:
        assert key in product1
    
    # Проверяем значения первого продукта
    assert product1["Код\nмодели"] == 12345.0
    assert product1["model_name"] == "Тестовый продукт 1"
    assert product1["Категория"] == "Электроника"
    assert product1["Цена позиции\nМП c НДС"] == 1000.0
    assert product1["Цена позиции\nB2C c НДС"] == 1200.0
    assert product1["Дельта в процентах"] == -16.67  # (1000-1200)/1200*100
    assert product1["Ссылка \nна источник"] == "https://wb.ru/product1"
    assert product1["Ссылка \nна источник 2"] == "https://ozon.ru/product1"


@pytest.mark.asyncio
async def test_export_to_excel_file(temp_db_manager, excel_tools):
    """Тестирует полный экспорт в Excel файл."""
    # Добавляем тестовый продукт
    product_data = {
        "code": 11111.0,
        "model_name": "Excel тест продукт",
        "category": "Тестовая категория",
        "unit": "шт",
        "priority_1_source": "wildberries",
        "priority_2_source": "ozon"
    }
    
    product_id = await temp_db_manager.save_product(product_data)
    
    # Добавляем цены
    await temp_db_manager.update_product_prices(product_id, {
        "wildberries": {"price": 500.0, "product_url": "https://wb.ru/test"},
        "ozon": {"price": 600.0, "product_url": "https://ozon.ru/test"}
    })
    
    # Получаем данные для экспорта
    export_data = await temp_db_manager.get_products_with_prices_for_export()
    
    # Создаем временный файл для экспорта
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        # Экспортируем в Excel
        result = await excel_tools.export_to_excel(
            data=export_data,
            file_path=temp_path,
            sheet_name="Товары с ценами",
            apply_formatting=True
        )
        
        # Проверяем результат экспорта
        assert result["status"] == "success"
        assert result["success"] is True
        assert result["rows_exported"] == 1
        assert result["columns_exported"] == 12
        
        # Проверяем, что файл создан
        assert os.path.exists(temp_path)
        
        # Читаем файл и проверяем содержимое
        df = pd.read_excel(temp_path, sheet_name="Товары с ценами")
        
        # Проверяем количество строк и колонок
        assert len(df) == 1
        assert len(df.columns) == 12
        
        # Проверяем содержимое
        row = df.iloc[0]
        assert row["Код\nмодели"] == 11111.0
        assert row["model_name"] == "Excel тест продукт"
        assert row["Цена позиции\nМП c НДС"] == 500.0
        assert row["Цена позиции\nB2C c НДС"] == 600.0
        
    finally:
        # Удаляем временный файл
        if os.path.exists(temp_path):
            os.unlink(temp_path)


@pytest.mark.asyncio
async def test_delta_calculation():
    """Тестирует правильность расчета дельты в процентах."""
    with tempfile.TemporaryDirectory() as temp_dir:
        user_data_manager = UserDataManager()
        user_data_manager.data_dir = Path(temp_dir)
        
        db_manager = DatabaseManager(user_data_manager)
        await db_manager.init_database()
        
        # Тестовые случаи для расчета дельты
        test_cases = [
            {"mp_price": 100.0, "b2c_price": 100.0, "expected_delta": 0.0},
            {"mp_price": 110.0, "b2c_price": 100.0, "expected_delta": 10.0},
            {"mp_price": 90.0, "b2c_price": 100.0, "expected_delta": -10.0},
            {"mp_price": 150.0, "b2c_price": 100.0, "expected_delta": 50.0},
        ]
        
        for i, case in enumerate(test_cases):
            # Создаем продукт
            product_data = {
                "code": float(i + 1),
                "model_name": f"Тест дельты {i + 1}",
                "category": "Тест",
                "unit": "шт",
                "priority_1_source": "wildberries",
                "priority_2_source": "ozon"
            }
            
            product_id = await db_manager.save_product(product_data)
            
            # Добавляем цены
            await db_manager.update_product_prices(product_id, {
                "wildberries": {"price": case["mp_price"]},
                "ozon": {"price": case["b2c_price"]}
            })
        
        # Получаем данные для экспорта
        export_data = await db_manager.get_products_with_prices_for_export()
        
        # Проверяем расчет дельты для каждого случая
        for i, case in enumerate(test_cases):
            product = export_data[i]
            actual_delta = product["Дельта в процентах"]
            expected_delta = case["expected_delta"]
            
            # Проверяем с точностью до 2 знаков после запятой
            assert abs(actual_delta - expected_delta) < 0.01, \
                f"Неправильная дельта для случая {i + 1}: ожидалось {expected_delta}, получено {actual_delta}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])