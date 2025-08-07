"""
A simplified library for working with ClickHouse.
"""

from .clickhouse_client import ClickHouseEasy, create_client, init_config, quick_setup

__version__ = "1.1.0"
__author__ = "Your Name"

__all__ = ["ClickHouseEasy", "create_client", "init_config", "quick_setup"]
