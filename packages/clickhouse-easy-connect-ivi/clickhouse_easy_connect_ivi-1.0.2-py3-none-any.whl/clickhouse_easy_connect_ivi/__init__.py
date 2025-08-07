"""
A simplified library for working with ClickHouse.
"""

from .clickhouse_client import ClickHouseEasy, create_client, setup_config

__version__ = "1.0.2"
__author__ = "Your Name"

__all__ = ["ClickHouseEasy", "create_client", "setup_config"]
