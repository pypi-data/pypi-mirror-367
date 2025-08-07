"""
Базовые тесты для ClickHouse Easy
"""

import os
import tempfile

import pytest

from clickhouse_easy_connect_ivi import ClickHouseEasy, init_config


def test_import():
    """Тест импорта библиотеки"""
    from clickhouse_easy_connect_ivi import (ClickHouseEasy, create_client,
                                             init_config, quick_setup)

    assert ClickHouseEasy is not None
    assert create_client is not None
    assert init_config is not None
    assert quick_setup is not None


def test_init_config():
    """Тест создания конфигурационного файла"""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = os.path.join(temp_dir, "test_config.yaml")
        result_path = init_config(config_path, create_template=True)

        assert result_path == config_path
        assert os.path.exists(config_path)

        # Проверяем содержимое файла
        with open(config_path, "r") as f:
            content = f.read()
            assert "host:" in content
            assert "username:" in content
            assert "password:" in content
            assert "database:" in content


def test_client_creation():
    """Тест создания клиента"""
    # Тест создания клиента без подключения
    client = ClickHouseEasy(
        host="test_host",
        port=8123,
        username="test_user",
        password="test_pass",
        database="test_db",
    )

    assert client.host == "test_host"
    assert client.port == 8123
    assert client.username == "test_user"
    assert client.database == "test_db"


def test_client_creation_with_env():
    """Тест создания клиента с переменными окружения"""
    # Устанавливаем переменные окружения
    os.environ["CLICKHOUSE_HOST"] = "env_host"
    os.environ["CLICKHOUSE_PORT"] = "9000"
    os.environ["CLICKHOUSE_USERNAME"] = "env_user"
    os.environ["CLICKHOUSE_PASSWORD"] = "env_pass"
    os.environ["CLICKHOUSE_DATABASE"] = "env_db"

    try:
        client = ClickHouseEasy()
        assert client.host == "env_host"
        assert client.port == 9000
        assert client.username == "env_user"
        assert client.password == "env_pass"
        assert client.database == "env_db"
    finally:
        # Очищаем переменные окружения
        for key in [
            "CLICKHOUSE_HOST",
            "CLICKHOUSE_PORT",
            "CLICKHOUSE_USERNAME",
            "CLICKHOUSE_PASSWORD",
            "CLICKHOUSE_DATABASE",
        ]:
            if key in os.environ:
                del os.environ[key]


def test_client_creation_with_auto_init():
    """Тест создания клиента с автоинициализацией"""
    # Сбрасываем флаг автоинициализации
    ClickHouseEasy.reset_auto_init()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)  # Переходим в временную директорию
        
        # Устанавливаем переменные окружения для корректного создания клиента
        os.environ["CLICKHOUSE_HOST"] = "test_host"
        os.environ["CLICKHOUSE_PORT"] = "8123"
        os.environ["CLICKHOUSE_USERNAME"] = "test_user"
        os.environ["CLICKHOUSE_PASSWORD"] = "test_pass"
        os.environ["CLICKHOUSE_DATABASE"] = "test_db"
        
        try:
            # При автоинициализации должен создаться конфиг-файл
            client = ClickHouseEasy(auto_init_config=True)
            
            # Проверяем что конфиг создался
            assert os.path.exists("clickhouse_config.yaml")
            
            assert client.host == "test_host"
            assert client.port == 8123
            assert client.username == "test_user"
            assert client.password == "test_pass"
            assert client.database == "test_db"
            
        finally:
            # Очищаем переменные окружения
            for key in [
                "CLICKHOUSE_HOST",
                "CLICKHOUSE_PORT", 
                "CLICKHOUSE_USERNAME",
                "CLICKHOUSE_PASSWORD",
                "CLICKHOUSE_DATABASE",
            ]:
                if key in os.environ:
                    del os.environ[key]


def test_client_creation_missing_params():
    """Тест создания клиента с отсутствующими параметрами"""
    # Отключаем автоинициализацию для этого теста
    with pytest.raises(
        ValueError,
        match="Необходимо указать host, port, username и password либо через параметры, ",
    ):
        ClickHouseEasy(auto_init_config=False)


if __name__ == "__main__":
    pytest.main([__file__])
