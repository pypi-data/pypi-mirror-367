"""
Менеджер базы данных для системы сравнения цен на маркетплейсах.

Обеспечивает управление SQLite базой данных, включая создание схемы,
CRUD операции для продуктов и цен, а также генерацию статистики.
"""

import aiosqlite
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from .models import Product, SearchResult, Statistics
from .user_data_manager import UserDataManager
from .error_handling import (
    handle_database_errors,
    handle_errors,
    DatabaseError,
    ErrorCategory,
    ErrorSeverity,
    error_handler,
    log_recovery_attempt
)


logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Менеджер для работы с SQLite базой данных.
    
    Обеспечивает полный цикл работы с данными: создание схемы,
    CRUD операции, статистику и обработку ошибок.
    """

    def __init__(self, user_data_manager: Optional[UserDataManager] = None):
        """
        Инициализирует менеджер базы данных.
        
        Args:
            user_data_manager: Менеджер пользовательских данных для определения пути к БД
        """
        if user_data_manager is None:
            user_data_manager = UserDataManager()
        
        self.user_data_manager = user_data_manager
        self.db_path = str(user_data_manager.get_database_path())
        
        logger.info(f"DatabaseManager инициализирован с путем к БД: {self.db_path}")

    def _ensure_data_directory(self) -> None:
        """Обеспечивает существование директории для базы данных."""
        # Директория уже создана через UserDataManager
        db_dir = Path(self.db_path).parent
        if not db_dir.exists():
            logger.warning(f"Директория БД {db_dir} не существует, создаем...")
            db_dir.mkdir(parents=True, exist_ok=True)

    @handle_database_errors(operation="init_database", retry_count=2)
    async def init_database(self) -> None:
        """
        Инициализирует базу данных, создает таблицы и индексы.
        
        Создает схему согласно проектированию:
        - Таблица products для хранения информации о товарах
        - Таблица prices для хранения ценовой информации
        - Индексы для оптимизации запросов
        """
        async with aiosqlite.connect(self.db_path) as db:
            # Создание таблицы продуктов
            await db.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code REAL UNIQUE NOT NULL,
                    model_name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    unit TEXT NOT NULL,
                    priority_1_source TEXT NOT NULL,
                    priority_2_source TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Создание таблицы цен
            await db.execute("""
                CREATE TABLE IF NOT EXISTS prices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    marketplace TEXT NOT NULL,
                    price REAL,
                    currency TEXT DEFAULT 'RUB',
                    availability TEXT,
                    product_url TEXT,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products (id),
                    UNIQUE(product_id, marketplace)
                )
            """)

            # Создание индексов для оптимизации запросов
            await self._create_indexes(db)
            
            await db.commit()
            logger.info("База данных успешно инициализирована")
            
            log_recovery_attempt(
                component="database_manager",
                action="Успешная инициализация базы данных",
                success=True
            )

    async def _create_indexes(self, db: aiosqlite.Connection) -> None:
        """
        Создает индексы для оптимизации запросов.
        
        Args:
            db: Соединение с базой данных
        """
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_products_code ON products(code)",
            "CREATE INDEX IF NOT EXISTS idx_prices_product_marketplace ON prices(product_id, marketplace)",
            "CREATE INDEX IF NOT EXISTS idx_prices_scraped_at ON prices(scraped_at)",
            "CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)",
            "CREATE INDEX IF NOT EXISTS idx_prices_marketplace ON prices(marketplace)"
        ]

        for index_sql in indexes:
            try:
                await db.execute(index_sql)
                logger.debug(f"Создан индекс: {index_sql}")
            except Exception as e:
                logger.warning(f"Не удалось создать индекс {index_sql}: {e}")

    async def close(self) -> None:
        """
        Закрывает соединение с базой данных.
        
        В текущей реализации с aiosqlite соединения закрываются автоматически
        при выходе из контекстного менеджера, но метод оставлен для совместимости.
        """
        logger.debug("Соединение с базой данных закрыто")

    def _get_connection(self):
        """
        Возвращает контекстный менеджер для соединения с базой данных.
        
        Returns:
            aiosqlite.Connection: Контекстный менеджер соединения
        """
        return aiosqlite.connect(self.db_path)

    async def _execute_with_error_handling(self, query: str, params: tuple = ()) -> Optional[aiosqlite.Cursor]:
        """
        Выполняет SQL запрос с обработкой ошибок.
        
        Args:
            query: SQL запрос
            params: Параметры запроса
            
        Returns:
            aiosqlite.Cursor: Курсор результата или None при ошибке
            
        Raises:
            Exception: При критических ошибках базы данных
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(query, params)
                await db.commit()
                return cursor
        except aiosqlite.IntegrityError as e:
            logger.warning(f"Нарушение целостности данных: {e}")
            raise
        except aiosqlite.OperationalError as e:
            logger.error(f"Операционная ошибка SQLite: {e}")
            raise
        except Exception as e:
            logger.error(f"Неожиданная ошибка базы данных: {e}")
            raise

    async def _fetch_with_error_handling(self, query: str, params: tuple = ()) -> List[aiosqlite.Row]:
        """
        Выполняет SELECT запрос с обработкой ошибок.
        
        Args:
            query: SQL запрос
            params: Параметры запроса
            
        Returns:
            List[aiosqlite.Row]: Список строк результата
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(query, params)
                return await cursor.fetchall()
        except Exception as e:
            logger.error(f"Ошибка выполнения запроса: {e}")
            raise

    @handle_database_errors(operation="save_product", retry_count=2)
    async def save_product(self, product_data: dict) -> int:
        """
        Сохраняет продукт в базу данных.
        
        Args:
            product_data: Словарь с данными продукта (поддерживает как Excel, так и обычный формат)
            
        Returns:
            int: ID созданного продукта
            
        Raises:
            aiosqlite.IntegrityError: При дублировании кода продукта
        """
        try:
            # Поддерживаем как Excel формат (с переносами строк), так и обычный формат
            code = product_data.get("Код\nмодели") or product_data.get("code")
            model_name = product_data.get("model_name")
            category = product_data.get("Категория") or product_data.get("category")
            unit = product_data.get("Единица измерения") or product_data.get("unit")
            priority_1 = product_data.get("Приоритет \n1 Источники") or product_data.get("priority_1_source")
            priority_2 = product_data.get("Приоритет \n2 Источники") or product_data.get("priority_2_source")
            
            query = """
                INSERT INTO products (code, model_name, category, unit, priority_1_source, priority_2_source)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            params = (code, model_name, category, unit, priority_1, priority_2)

            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(query, params)
                await db.commit()
                product_id = cursor.lastrowid
                logger.info(f"Продукт сохранен с ID: {product_id}")
                return product_id

        except aiosqlite.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                code = product_data.get("Код\nмодели") or product_data.get("code")
                logger.warning(f"Продукт с кодом {code} уже существует")
                raise aiosqlite.IntegrityError(f"Продукт с кодом {code} уже существует")
            raise
        except Exception as e:
            logger.error(f"Ошибка сохранения продукта: {e}")
            raise

    @handle_database_errors(operation="update_product", retry_count=2)
    async def update_product(self, product_data: dict) -> bool:
        """
        Обновляет существующий продукт в базе данных.
        
        Args:
            product_data: Словарь с данными продукта (должен содержать code)
            
        Returns:
            bool: True если продукт обновлен, False если не найден
        """
        try:
            query = """
                UPDATE products 
                SET model_name = ?, category = ?, unit = ?, 
                    priority_1_source = ?, priority_2_source = ?, updated_at = CURRENT_TIMESTAMP
                WHERE code = ?
            """
            params = (
                product_data.get("model_name"),
                product_data.get("category"),
                product_data.get("unit"),
                product_data.get("priority_1_source"),
                product_data.get("priority_2_source"),
                product_data.get("code")
            )

            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(query, params)
                await db.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"Продукт с кодом {product_data.get('code')} обновлен")
                    return True
                else:
                    logger.warning(f"Продукт с кодом {product_data.get('code')} не найден для обновления")
                    return False

        except Exception as e:
            logger.error(f"Ошибка обновления продукта: {e}")
            raise

    @handle_database_errors(operation="get_product_by_code", retry_count=2)
    async def get_product_by_code(self, code: float) -> Optional[dict]:
        """
        Получает продукт по коду.
        
        Args:
            code: Код продукта
            
        Returns:
            Optional[dict]: Словарь с данными продукта или None если не найден
        """
        try:
            query = """
                SELECT id, code, model_name, category, unit, 
                       priority_1_source, priority_2_source, created_at, updated_at
                FROM products 
                WHERE code = ?
            """

            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(query, (code,))
                row = await cursor.fetchone()

                if row:
                    return {
                        "id": row["id"],
                        "code": row["code"],
                        "model_name": row["model_name"],
                        "category": row["category"],
                        "unit": row["unit"],
                        "priority_1_source": row["priority_1_source"],
                        "priority_2_source": row["priority_2_source"],
                        "created_at": row["created_at"],
                        "updated_at": row["updated_at"]
                    }
                return None

        except Exception as e:
            logger.error(f"Ошибка получения продукта по коду {code}: {e}")
            raise

    @handle_database_errors(operation="save_price", retry_count=2)
    async def save_price(self, product_id: int, price_data: dict) -> int:
        """
        Сохраняет ценовую информацию для продукта.
        
        Args:
            product_id: ID продукта
            price_data: Словарь с ценовой информацией
            
        Returns:
            int: ID созданной записи цены
        """
        try:
            query = """
                INSERT OR REPLACE INTO prices 
                (product_id, marketplace, price, currency, availability, product_url)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            params = (
                product_id,
                price_data.get("marketplace"),
                price_data.get("price"),
                price_data.get("currency", "RUB"),
                price_data.get("availability"),
                price_data.get("product_url")
            )

            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(query, params)
                await db.commit()
                price_id = cursor.lastrowid
                logger.info(f"Цена сохранена с ID: {price_id}")
                return price_id

        except Exception as e:
            logger.error(f"Ошибка сохранения цены: {e}")
            raise

    @handle_database_errors(operation="update_product_prices", retry_count=2)
    async def update_product_prices(self, product_id: int, prices: Dict[str, dict]) -> bool:
        """
        Обновляет ценовую информацию для продукта на всех маркетплейсах.
        
        Args:
            product_id: ID продукта
            prices: Словарь с ценами по маркетплейсам
            
        Returns:
            bool: True если цены обновлены успешно
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                for marketplace, price_info in prices.items():
                    query = """
                        INSERT OR REPLACE INTO prices 
                        (product_id, marketplace, price, currency, availability, product_url)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """
                    params = (
                        product_id,
                        marketplace,
                        price_info.get("price"),
                        price_info.get("currency", "RUB"),
                        price_info.get("availability"),
                        price_info.get("product_url")
                    )
                    await db.execute(query, params)

                await db.commit()
                logger.info(f"Цены обновлены для продукта ID: {product_id}")
                return True

        except Exception as e:
            logger.error(f"Ошибка обновления цен для продукта {product_id}: {e}")
            raise

    @handle_database_errors(operation="get_product_prices", retry_count=2)
    async def get_product_prices(self, product_id: int) -> List[dict]:
        """
        Получает все цены для продукта.
        
        Args:
            product_id: ID продукта
            
        Returns:
            List[dict]: Список цен с разных маркетплейсов
        """
        try:
            query = """
                SELECT marketplace, price, currency, availability, product_url, scraped_at
                FROM prices 
                WHERE product_id = ?
                ORDER BY scraped_at DESC
            """

            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(query, (product_id,))
                rows = await cursor.fetchall()

                return [
                    {
                        "marketplace": row["marketplace"],
                        "price": row["price"],
                        "currency": row["currency"],
                        "availability": row["availability"],
                        "product_url": row["product_url"],
                        "scraped_at": row["scraped_at"]
                    }
                    for row in rows
                ]

        except Exception as e:
            logger.error(f"Ошибка получения цен для продукта {product_id}: {e}")
            raise

    @handle_database_errors(operation="has_product_prices", retry_count=2)
    async def has_product_prices(self, product_id: int) -> bool:
        """
        Проверяет, есть ли у продукта сохраненные цены.
        
        Args:
            product_id: ID продукта
            
        Returns:
            bool: True если у продукта есть цены, False если нет
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "SELECT COUNT(*) FROM prices WHERE product_id = ?",
                    (product_id,)
                )
                row = await cursor.fetchone()
                return row[0] > 0 if row else False

        except Exception as e:
            logger.error(f"Ошибка проверки цен для продукта {product_id}: {e}")
            raise

    @handle_database_errors(operation="delete_product", retry_count=2)
    async def delete_product(self, code: float) -> bool:
        """
        Удаляет продукт и все связанные цены.
        
        Args:
            code: Код продукта
            
        Returns:
            bool: True если продукт удален, False если не найден
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Сначала получаем ID продукта
                cursor = await db.execute("SELECT id FROM products WHERE code = ?", (code,))
                row = await cursor.fetchone()
                
                if not row:
                    logger.warning(f"Продукт с кодом {code} не найден для удаления")
                    return False

                product_id = row[0]

                # Удаляем связанные цены
                await db.execute("DELETE FROM prices WHERE product_id = ?", (product_id,))
                
                # Удаляем продукт
                cursor = await db.execute("DELETE FROM products WHERE code = ?", (code,))
                await db.commit()

                logger.info(f"Продукт с кодом {code} и все связанные цены удалены")
                return True

        except Exception as e:
            logger.error(f"Ошибка удаления продукта {code}: {e}")
            raise

    @handle_database_errors(operation="get_statistics", retry_count=2)
    async def get_statistics(self) -> Statistics:
        """
        Генерирует агрегированную статистику по всем продуктам.
        
        Returns:
            Statistics: Объект со статистикой
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row

                # Общее количество продуктов
                cursor = await db.execute("SELECT COUNT(*) as total FROM products")
                total_products = (await cursor.fetchone())["total"]

                # Количество продуктов с ценами
                cursor = await db.execute("""
                    SELECT COUNT(DISTINCT p.id) as with_prices
                    FROM products p
                    INNER JOIN prices pr ON p.id = pr.product_id
                    WHERE pr.price IS NOT NULL
                """)
                products_with_prices = (await cursor.fetchone())["with_prices"]

                # Разбивка по категориям
                cursor = await db.execute("""
                    SELECT category, COUNT(*) as count
                    FROM products
                    GROUP BY category
                    ORDER BY count DESC
                """)
                category_rows = await cursor.fetchall()
                category_breakdown = {row["category"]: row["count"] for row in category_rows}

                # Покрытие маркетплейсов
                cursor = await db.execute("""
                    SELECT marketplace, COUNT(DISTINCT product_id) as count
                    FROM prices
                    WHERE price IS NOT NULL
                    GROUP BY marketplace
                    ORDER BY count DESC
                """)
                marketplace_rows = await cursor.fetchall()
                marketplace_coverage = {row["marketplace"]: row["count"] for row in marketplace_rows}

                # Средняя дельта цен (рассчитываем на основе доступных цен)
                average_delta = await self._calculate_average_price_delta(db)

                return Statistics(
                    total_products=total_products,
                    products_with_prices=products_with_prices,
                    average_delta_percent=average_delta,
                    category_breakdown=category_breakdown,
                    marketplace_coverage=marketplace_coverage
                )

        except Exception as e:
            logger.error(f"Ошибка генерации статистики: {e}")
            raise

    async def _calculate_average_price_delta(self, db: aiosqlite.Connection) -> float:
        """
        Рассчитывает среднюю процентную дельту цен между маркетплейсами.
        
        Args:
            db: Соединение с базой данных
            
        Returns:
            float: Средняя процентная дельта
        """
        try:
            # Получаем продукты с ценами на нескольких маркетплейсах
            cursor = await db.execute("""
                SELECT product_id, marketplace, price
                FROM prices
                WHERE price IS NOT NULL AND price > 0
                ORDER BY product_id, marketplace
            """)
            price_rows = await cursor.fetchall()

            if not price_rows:
                return 0.0

            # Группируем цены по продуктам
            product_prices = {}
            for row in price_rows:
                product_id = row["product_id"]
                if product_id not in product_prices:
                    product_prices[product_id] = []
                product_prices[product_id].append(row["price"])

            # Рассчитываем дельты для продуктов с несколькими ценами
            deltas = []
            for product_id, prices in product_prices.items():
                if len(prices) >= 2:
                    min_price = min(prices)
                    max_price = max(prices)
                    if min_price > 0:
                        delta = ((max_price - min_price) / min_price) * 100
                        deltas.append(delta)

            return sum(deltas) / len(deltas) if deltas else 0.0

        except Exception as e:
            logger.error(f"Ошибка расчета средней дельты цен: {e}")
            return 0.0

    async def get_products_by_category(self, category: str) -> List[dict]:
        """
        Получает все продукты определенной категории.
        
        Args:
            category: Название категории
            
        Returns:
            List[dict]: Список продуктов категории
        """
        try:
            query = """
                SELECT id, code, model_name, category, unit, 
                       priority_1_source, priority_2_source
                FROM products 
                WHERE category = ?
                ORDER BY model_name
            """

            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(query, (category,))
                rows = await cursor.fetchall()

                return [
                    {
                        "id": row["id"],
                        "code": row["code"],
                        "model_name": row["model_name"],
                        "category": row["category"],
                        "unit": row["unit"],
                        "priority_1_source": row["priority_1_source"],
                        "priority_2_source": row["priority_2_source"]
                    }
                    for row in rows
                ]

        except Exception as e:
            logger.error(f"Ошибка получения продуктов категории {category}: {e}")
            raise

    async def get_marketplace_statistics(self, marketplace: str) -> dict:
        """
        Получает статистику по конкретному маркетплейсу.
        
        Args:
            marketplace: Название маркетплейса
            
        Returns:
            dict: Статистика маркетплейса
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row

                # Количество товаров с ценами на маркетплейсе
                cursor = await db.execute("""
                    SELECT COUNT(*) as count
                    FROM prices
                    WHERE marketplace = ? AND price IS NOT NULL
                """, (marketplace,))
                products_count = (await cursor.fetchone())["count"]

                # Средняя цена на маркетплейсе
                cursor = await db.execute("""
                    SELECT AVG(price) as avg_price
                    FROM prices
                    WHERE marketplace = ? AND price IS NOT NULL AND price > 0
                """, (marketplace,))
                avg_price = (await cursor.fetchone())["avg_price"] or 0.0

                # Минимальная и максимальная цены
                cursor = await db.execute("""
                    SELECT MIN(price) as min_price, MAX(price) as max_price
                    FROM prices
                    WHERE marketplace = ? AND price IS NOT NULL AND price > 0
                """, (marketplace,))
                price_range = await cursor.fetchone()

                return {
                    "marketplace": marketplace,
                    "products_count": products_count,
                    "average_price": round(avg_price, 2),
                    "min_price": price_range["min_price"] or 0.0,
                    "max_price": price_range["max_price"] or 0.0
                }

        except Exception as e:
            logger.error(f"Ошибка получения статистики маркетплейса {marketplace}: {e}")
            raise

    async def get_all_products(self, limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        """
        Получает все продукты с пагинацией.
        
        Args:
            limit: Максимальное количество продуктов (None для всех)
            offset: Смещение для пагинации
            
        Returns:
            List[dict]: Список продуктов
        """
        try:
            query = """
                SELECT id, code, model_name, category, unit, 
                       priority_1_source, priority_2_source, created_at, updated_at
                FROM products 
                ORDER BY created_at DESC
            """
            
            params = ()
            if limit is not None:
                query += " LIMIT ? OFFSET ?"
                params = (limit, offset)

            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(query, params)
                rows = await cursor.fetchall()

                return [
                    {
                        "id": row["id"],
                        "code": row["code"],
                        "model_name": row["model_name"],
                        "category": row["category"],
                        "unit": row["unit"],
                        "priority_1_source": row["priority_1_source"],
                        "priority_2_source": row["priority_2_source"],
                        "created_at": row["created_at"],
                        "updated_at": row["updated_at"]
                    }
                    for row in rows
                ]

        except Exception as e:
            logger.error(f"Ошибка получения списка продуктов: {e}")
            raise

    @handle_database_errors(operation="get_products_with_prices_for_export", retry_count=2)
    async def get_products_with_prices_for_export(self) -> List[dict]:
        """
        Получает все продукты с ценами для экспорта в Excel в формате исходной структуры.
        
        Returns:
            List[dict]: Список продуктов с ценами в формате для Excel экспорта
        """
        try:
            # Сначала получаем все продукты
            products_query = """
                SELECT id, code, model_name, category, unit, priority_1_source, priority_2_source
                FROM products 
                ORDER BY code
            """

            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                # Получаем все продукты
                cursor = await db.execute(products_query)
                products = await cursor.fetchall()

                export_data = []
                for product in products:
                    # Получаем цены для этого продукта
                    prices_query = """
                        SELECT marketplace, price, product_url
                        FROM prices 
                        WHERE product_id = ? AND price IS NOT NULL
                    """
                    cursor = await db.execute(prices_query, (product["id"],))
                    prices = await cursor.fetchall()
                    
                    # Создаем словарь цен по маркетплейсам
                    price_dict = {}
                    for price_row in prices:
                        price_dict[price_row["marketplace"]] = {
                            "price": price_row["price"],
                            "url": price_row["product_url"]
                        }
                    
                    # Если нет цен, пропускаем продукт или показываем пустые значения
                    if not price_dict:
                        mp_price = ""
                        b2c_price = ""
                        second_b2c_price = ""
                        delta_percent = ""
                        mp_source_link = ""
                        b2c_source_link = ""
                        second_source_link = ""
                    else:
                        # Сортируем цены по возрастанию для поиска лучших предложений
                        sorted_prices = sorted(price_dict.items(), key=lambda x: x[1]["price"])
                        
                        # Ищем цены для приоритетных источников
                        priority_1 = product["priority_1_source"]
                        priority_2 = product["priority_2_source"]
                        
                        mp_price, mp_source_link, mp_marketplace = self._find_price_for_source(priority_1, price_dict)
                        b2c_price, b2c_source_link, b2c_marketplace = self._find_price_for_source(priority_2, price_dict)
                        
                        # Если не нашли цену для приоритета 1, берем самую низкую цену
                        if mp_price is None and sorted_prices:
                            mp_marketplace, mp_info = sorted_prices[0]
                            mp_price = mp_info["price"]
                            mp_source_link = mp_info["url"] or ""
                        
                        # Если не нашли цену для приоритета 2, берем вторую самую низкую цену (если есть)
                        if b2c_price is None and len(sorted_prices) > 1:
                            # Ищем цену, отличную от уже выбранной для МП
                            for marketplace, info in sorted_prices:
                                if marketplace != mp_marketplace:
                                    b2c_marketplace = marketplace
                                    b2c_price = info["price"]
                                    b2c_source_link = info["url"] or ""
                                    break
                        
                        # Ищем третью цену для дополнительного сравнения
                        second_b2c_price = ""
                        second_source_link = ""
                        if len(sorted_prices) > 2:
                            for marketplace, info in sorted_prices:
                                if marketplace != mp_marketplace and marketplace != b2c_marketplace:
                                    second_b2c_price = info["price"]
                                    second_source_link = info["url"] or ""
                                    break
                        
                        # Рассчитываем дельту в процентах
                        delta_percent = ""
                        if mp_price is not None and b2c_price is not None and b2c_price > 0:
                            delta_percent = round(((mp_price - b2c_price) / b2c_price) * 100, 2)
                    
                    # Формируем текстовое описание всех доступных цен
                    additional_info = self._format_all_prices_info(price_dict)
                    
                    # Формируем данные в формате Excel структуры
                    export_row = {
                        "Код\nмодели": product["code"],
                        "model_name": product["model_name"] or "",
                        "Категория": product["category"] or "",
                        "Единица измерения": product["unit"] or "",
                        "Приоритет \n1 Источники": product["priority_1_source"] or "",
                        "Приоритет \n2 Источники": product["priority_2_source"] or "",
                        "Цена позиции\nМП c НДС": mp_price if mp_price != "" else "",
                        "Цена позиции\nB2C c НДС": b2c_price if b2c_price != "" else "",
                        "Дельта в процентах": delta_percent,
                        "Ссылка \nна источник": mp_source_link,
                        "Цена 2 позиции\nB2C c НДС": second_b2c_price,
                        "Ссылка \nна источник 2": second_source_link or b2c_source_link,
                        "Дополнительно": additional_info
                    }
                    
                    export_data.append(export_row)

                logger.info(f"Подготовлено {len(export_data)} продуктов для экспорта")
                return export_data

        except Exception as e:
            logger.error(f"Ошибка получения данных для экспорта: {e}")
            raise

    def _find_price_for_source(self, priority_source: str, price_dict: dict) -> tuple:
        """
        Ищет цену для указанного приоритетного источника.
        
        Args:
            priority_source: Название приоритетного источника
            price_dict: Словарь с ценами по маркетплейсам
            
        Returns:
            tuple: (цена, ссылка, название_маркетплейса) или (None, "", None)
        """
        if not priority_source or not price_dict:
            return None, "", None
        
        priority_lower = priority_source.lower()
        
        # Словарь для сопоставления названий
        marketplace_mapping = {
            "комус": ["komus", "komus.ru"],
            "всеинструменты": ["vseinstrumenti", "vseinstrumenti.ru", "всеинструменты.ру", "vse_instrumenti", "vi"],
            "озон": ["ozon", "ozon.ru"],
            "wildberries": ["wildberries", "wildberries.ru", "wb"],
            "яндекс": ["yandex", "yandex_market", "market.yandex.ru", "яндекс маркет"],
            "офисмаг": ["officemag", "officemag.ru"]
        }
        
        # Сначала пробуем точное совпадение
        for marketplace, price_info in price_dict.items():
            if marketplace.lower() == priority_lower:
                return price_info["price"], price_info["url"] or "", marketplace
        
        # Затем пробуем сопоставление через словарь
        for key, variants in marketplace_mapping.items():
            if key in priority_lower:
                for marketplace, price_info in price_dict.items():
                    marketplace_lower = marketplace.lower()
                    for variant in variants:
                        if variant in marketplace_lower:
                            return price_info["price"], price_info["url"] or "", marketplace
        
        # Если не нашли через словарь, пробуем частичное совпадение
        for marketplace, price_info in price_dict.items():
            marketplace_lower = marketplace.lower()
            if (priority_lower in marketplace_lower or 
                marketplace_lower in priority_lower or
                any(word in marketplace_lower for word in priority_lower.split()) or
                any(word in priority_lower for word in marketplace_lower.split())):
                return price_info["price"], price_info["url"] or "", marketplace
        
        return None, "", None

    def _format_all_prices_info(self, price_dict: dict) -> str:
        """
        Форматирует все доступные цены в текстовый вид для колонки "Дополнительно".
        
        Args:
            price_dict: Словарь с ценами по маркетплейсам
            
        Returns:
            str: Отформатированная строка со всеми данными о ценах
        """
        if not price_dict:
            return "Цены не найдены"
        
        # Сортируем цены по возрастанию для удобства
        sorted_prices = sorted(price_dict.items(), key=lambda x: x[1]["price"])
        
        info_parts = []
        for i, (marketplace, price_info) in enumerate(sorted_prices, 1):
            price = price_info["price"]
            url = price_info["url"]
            
            # Формируем строку для каждого маркетплейса
            price_str = f"{i}. {marketplace}: {price} руб"
            
            if url:
                price_str += f" | Ссылка: {url}"
            else:
                price_str += " | Ссылка: не указана"
            
            info_parts.append(price_str)
        
        # Добавляем статистику
        if len(sorted_prices) > 1:
            min_price = sorted_prices[0][1]["price"]
            max_price = sorted_prices[-1][1]["price"]
            min_marketplace = sorted_prices[0][0]
            max_marketplace = sorted_prices[-1][0]
            
            delta = round(((max_price - min_price) / min_price) * 100, 2)
            
            info_parts.append(f"--- СТАТИСТИКА ---")
            info_parts.append(f"Мин: {min_price} руб ({min_marketplace})")
            info_parts.append(f"Макс: {max_price} руб ({max_marketplace})")
            info_parts.append(f"Разброс: {delta}%")
            info_parts.append(f"Всего источников: {len(sorted_prices)}")
        
        return " | ".join(info_parts)