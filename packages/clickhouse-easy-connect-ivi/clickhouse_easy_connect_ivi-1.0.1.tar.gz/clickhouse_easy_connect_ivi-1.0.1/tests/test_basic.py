"""
Базовые тесты для ClickHouse Easy
"""

import os
import tempfile

import pytest

from clickhouse_easy_connect_ivi import ClickHouseEasy, setup_config


def test_import():
    """Тест импорта библиотеки"""
    from clickhouse_easy_connect_ivi import (ClickHouseEasy, create_client,
                                             setup_config)

    assert ClickHouseEasy is not None
    assert create_client is not None
    assert setup_config is not None


def test_setup_config():
    """Тест создания конфигурационного файла"""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = os.path.join(temp_dir, "test_config.yaml")
        result_path = setup_config(config_path)

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


def test_client_creation_missing_params():
    """Тест создания клиента с отсутствующими параметрами"""
    with pytest.raises(
        ValueError,
        match="Необходимо указать host, port, username и password либо через параметры, ",
    ):
        ClickHouseEasy()


if __name__ == "__main__":
    pytest.main([__file__])
