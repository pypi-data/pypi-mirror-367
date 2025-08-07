import json
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

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
        config_file: Optional[str] = None,
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
        """
        self._client = None

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

    def _load_config_from_file(self, config_file: str):
        """Загрузка конфигурации из файла"""
        config_path = Path(config_file)

        if config_path.suffix.lower() == ".csv":
            # Загрузка из CSV файла (расширенный формат)
            pass_data = pd.read_csv(
                config_file, sep="___", engine="python", header=None
            )
            config_dict = dict(zip(pass_data.iloc[:, 0], pass_data.iloc[:, 1]))

            # Загружаем все доступные параметры из CSV
            if "host" in config_dict:
                self.host = config_dict["host"]
            if "port" in config_dict:
                self.port = int(config_dict["port"])
            if "database" in config_dict:
                self.database = config_dict["database"]
            if "username" in config_dict:
                self.username = config_dict["username"]
            if "password" in config_dict:
                self.password = config_dict["password"]

        elif config_path.suffix.lower() == ".json":
            # Загрузка из JSON файла
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
            self._update_config_from_dict(config)

        elif config_path.suffix.lower() in [".yaml", ".yml"]:
            # Загрузка из YAML файла
            with open(config_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            self._update_config_from_dict(config)

        else:
            raise ValueError("Поддерживаются файлы .csv, .json, .yaml и .yml")

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
            format: Формат файла ('yaml', 'json' или 'csv')
        """
        config_path = Path(config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        if format.lower() in ["yaml", "yml"]:
            config = {
                "host": self.host,
                "port": self.port,
                "username": self.username,
                "password": self.password,
                "database": self.database,
            }
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        elif format.lower() == "json":
            config = {
                "host": self.host,
                "port": self.port,
                "username": self.username,
                "password": self.password,
                "database": self.database,
            }
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        elif format.lower() == "csv":
            # Создаем CSV файл вручную для корректной работы с разделителем ___
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(f"host___{self.host}\n")
                f.write(f"port___{self.port}\n")
                f.write(f"database___{self.database}\n")
                f.write(f"username___{self.username}\n")
                f.write(f"password___{self.password}\n")
        else:
            raise ValueError("Поддерживаются форматы 'yaml', 'json' и 'csv'")


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


def setup_config(
    config_file: str = "clickhouse_config.yaml",
    username: str = None,
    password: str = None,
    database: str = None,
    host: str = None,
    port: int = 8123,
) -> str:
    """
    Создание локального конфигурационного файла

    Args:
        config_file: Имя файла конфигурации
        username: Имя пользователя
        password: Пароль
        database: Имя базы данных
        host: Хост сервера
        port: Порт подключения

    Returns:
        Путь к созданному файлу конфигурации
    """
    config = {
        "host": host or "your_clickhouse_host_here",
        "port": port,
        "username": username or "your_username_here",
        "password": password or "your_password_here",
        "database": database or "your_database_here",
    }

    config_path = Path(config_file)
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    print(f"Конфигурационный файл создан: {config_path.absolute()}")
    print("Отредактируйте файл, указав ваши реальные данные для подключения")

    return str(config_path.absolute())
