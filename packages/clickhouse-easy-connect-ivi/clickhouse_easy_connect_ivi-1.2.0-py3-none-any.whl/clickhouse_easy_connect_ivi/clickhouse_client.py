import os
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
import yaml
from clickhouse_connect import get_client


class ClickHouseEasy:
    """
    Упрощенный клиент для работы с ClickHouse

    Позволяет один раз настроить подключение и затем выполнять SQL-запросы,
    получая результаты в виде pandas DataFrame.
    """

    # Добавляем класс-атрибут для отслеживания инициализации
    _default_config_initialized = False
    _default_config_file = "clickhouse_config.yaml"

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
        config_file: Optional[str] = None,
        auto_init_config: bool = True,
    ):
        """
        Инициализация клиента ClickHouse

        Args:
            host: Хост ClickHouse сервера
            port: Порт для подключения
            username: Имя пользователя
            password: Пароль
            database: Имя базы данных
            config_file: Путь к файлу конфигурации (опционально)
            auto_init_config: Автоматически создать конфиг при первом использовании
        """
        self._client = None

        # Если включена автоинициализация и конфиг еще не создан
        if auto_init_config and not self._default_config_initialized:
            self._auto_initialize_config()

        # Если не указан config_file, но есть дефолтный - используем его
        if config_file is None and Path(self._default_config_file).exists():
            config_file = self._default_config_file

        # Инициализируем параметры из переменных окружения по умолчанию
        self.host = host or os.getenv("CLICKHOUSE_HOST")
        self.port = port or int(os.getenv("CLICKHOUSE_PORT", "8123"))
        self.username = username or os.getenv("CLICKHOUSE_USERNAME")
        self.password = password or os.getenv("CLICKHOUSE_PASSWORD")
        self.database = database or os.getenv("CLICKHOUSE_DATABASE")

        # Если указан файл конфигурации, загружаем из него (с приоритетом над env и параметрами)
        if config_file:
            self._load_config_from_file(config_file)

        # Проверяем обязательные параметры
        if not all([self.host, self.port, self.username, self.password]):
            raise ValueError(
                "Необходимо указать host, port, username и password либо через параметры, "
                "либо через переменные окружения (CLICKHOUSE_HOST, CLICKHOUSE_PORT, "
                "CLICKHOUSE_USERNAME, CLICKHOUSE_PASSWORD), либо через файл конфигурации"
            )

    @classmethod
    def _auto_initialize_config(cls):
        """Автоматическая инициализация конфига при первом использовании"""
        if not cls._default_config_initialized and not Path(cls._default_config_file).exists():
            print(f"🔧 Создаю конфигурационный файл: {cls._default_config_file}")
            print("📝 Отредактируйте его с вашими данными для подключения")
            
            cls.initialize_config(
                config_file=cls._default_config_file,
                create_template=True
            )
            cls._default_config_initialized = True

    def _load_config_from_file(self, config_file: str):
        """Загрузка конфигурации из файла"""
        config_path = Path(config_file)

        if config_path.suffix.lower() in [".yaml", ".yml"]:
            # Загрузка из YAML файла
            with open(config_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            self._update_config_from_dict(config)

        else:
            raise ValueError("Поддерживаются только файлы .yaml и .yml")

    def _update_config_from_dict(self, config: Dict[str, Any]):
        """Обновление конфигурации из словаря"""
        if "host" in config and config["host"]:
            self.host = config["host"]
        if "port" in config and config["port"]:
            self.port = int(config["port"])
        if "username" in config and config["username"]:
            self.username = config["username"]
        if "password" in config and config["password"]:
            self.password = config["password"]
        if "database" in config and config["database"]:
            self.database = config["database"]

    def connect(self) -> bool:
        """
        Установка соединения с ClickHouse

        Returns:
            True если подключение успешно, False иначе
        """
        try:
            self._client = get_client(
                host=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                database=self.database,
            )
            # Проверяем подключение
            self._client.command("SELECT 1")
            return True
        except Exception as e:
            print(f"Ошибка подключения к ClickHouse: {e}")
            return False

    def query(self, sql_query: str, **kwargs) -> pd.DataFrame:
        """
        Выполнение SQL-запроса и получение результата в виде DataFrame

        Args:
            sql_query: SQL-запрос для выполнения
            **kwargs: Дополнительные параметры для query_df

        Returns:
            pandas.DataFrame с результатами запроса
        """
        if self._client is None:
            if not self.connect():
                raise ConnectionError("Не удалось подключиться к ClickHouse")

        try:
            return self._client.query_df(sql_query, **kwargs)
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            raise

    def execute(self, sql_command: str) -> Any:
        """
        Выполнение SQL-команды (INSERT, UPDATE, DELETE и т.д.)

        Args:
            sql_command: SQL-команда для выполнения

        Returns:
            Результат выполнения команды
        """
        if self._client is None:
            if not self.connect():
                raise ConnectionError("Не удалось подключиться к ClickHouse")

        try:
            return self._client.command(sql_command)
        except Exception as e:
            print(f"Ошибка выполнения команды: {e}")
            raise

    def close(self):
        """Закрытие соединения"""
        if self._client:
            self._client.close()
            self._client = None

    def __enter__(self):
        """Поддержка контекстного менеджера"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Закрытие соединения при выходе из контекста"""
        self.close()

    def save_config(self, config_file: str, format: str = "yaml"):
        """
        Сохранение текущей конфигурации в файл

        Args:
            config_file: Путь к файлу для сохранения
            format: Формат файла (только 'yaml')
        """
        config_path = Path(config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        config = {
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "password": self.password,
            "database": self.database,
        }

        if format.lower() in ["yaml", "yml"]:
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        else:
            raise ValueError("Поддерживается только формат 'yaml'")

    @staticmethod
    def initialize_config(
        config_file: str = "clickhouse_config.yaml",
        host: Optional[str] = None,
        port: int = 8123,
        username: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
        create_template: bool = False,
        overwrite: bool = False
    ) -> str:
        """
        Инициализация конфигурационного файла

        Args:
            config_file: Путь к файлу конфигурации
            host: Хост ClickHouse сервера
            port: Порт для подключения
            username: Имя пользователя
            password: Пароль
            database: Имя базы данных
            create_template: Создать шаблон с placeholder'ами
            overwrite: Перезаписать существующий файл

        Returns:
            Путь к созданному файлу конфигурации
        """
        config_path = Path(config_file)
        
        # Проверяем существование файла
        if config_path.exists() and not overwrite:
            response = input(f"Файл {config_file} уже существует. Перезаписать? (y/N): ")
            if response.lower() not in ['y', 'yes', 'да']:
                print("Операция отменена.")
                return str(config_path.absolute())

        # Создаем директорию если нужно
        config_path.parent.mkdir(parents=True, exist_ok=True)

        if create_template:
            # Создаем шаблон с placeholder'ами
            config = {
                "host": "your_clickhouse_host_here",
                "port": 8123,
                "username": "your_username_here", 
                "password": "your_password_here",
                "database": "your_database_here"
            }
        else:
            # Используем переданные значения
            config = {
                "host": host or "localhost",
                "port": port,
                "username": username or "default",
                "password": password or "",
                "database": database or "default"
            }

        # Сохраняем в YAML формате
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

        if create_template:
            print(f"📁 Шаблон конфигурации создан: {config_path.absolute()}")
            print("⚠️  Отредактируйте файл, указав ваши реальные данные для подключения")
        else:
            print(f"✅ Конфигурационный файл создан: {config_path.absolute()}")

        return str(config_path.absolute())

    @classmethod
    def setup_config_interactive(cls, config_file: str = "clickhouse_config.yaml") -> str:
        """
        Интерактивная настройка конфигурации через консоль

        Args:
            config_file: Путь к файлу конфигурации

        Returns:
            Путь к созданному файлу конфигурации
        """
        print("🔧 Настройка подключения к ClickHouse")
        print("=" * 40)
        
        host = input("Хост (localhost): ").strip() or "localhost"
        port = input("Порт (8123): ").strip() or "8123"
        username = input("Имя пользователя (default): ").strip() or "default"
        password = input("Пароль: ").strip()
        database = input("База данных (default): ").strip() or "default"
        
        try:
            port = int(port)
        except ValueError:
            print("⚠️  Неверный порт, использую 8123")
            port = 8123

        return cls.initialize_config(
            config_file=config_file,
            host=host,
            port=port,
            username=username,
            password=password,
            database=database,
            overwrite=True
        )

    @classmethod
    def reset_auto_init(cls):
        """Сброс флага автоинициализации (для тестирования)"""
        cls._default_config_initialized = False


# Удобная функция для быстрого создания клиента
def create_client(
    username: str, password: str, database: str, host: str, port: int = 8123
) -> ClickHouseEasy:
    """
    Быстрое создание клиента ClickHouse

    Args:
        username: Имя пользователя
        password: Пароль
        database: Имя базы данных
        host: Хост сервера
        port: Порт подключения

    Returns:
        Настроенный экземпляр ClickHouseEasy
    """
    client = ClickHouseEasy(
        host=host, port=port, username=username, password=password, database=database
    )
    return client


# Удобные функции для работы с конфигурацией
def init_config(config_file: str = "clickhouse_config.yaml", interactive: bool = False, **kwargs) -> str:
    """
    Удобная функция для инициализации конфига
    
    Args:
        config_file: Путь к файлу конфигурации
        interactive: Интерактивный режим настройки
        **kwargs: Параметры для initialize_config
    
    Returns:
        Путь к созданному файлу
    """
    if interactive:
        return ClickHouseEasy.setup_config_interactive(config_file)
    else:
        return ClickHouseEasy.initialize_config(config_file, **kwargs)

def quick_setup(**kwargs) -> ClickHouseEasy:
    """
    Быстрая настройка с созданием конфига и клиента
    
    Args:
        **kwargs: Параметры подключения
    
    Returns:
        Настроенный клиент
    """
    config_file = "clickhouse_config.yaml"
    ClickHouseEasy.initialize_config(config_file, overwrite=True, **kwargs)
    return ClickHouseEasy(config_file=config_file)
