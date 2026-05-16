"""
SQL Server Variables
"""

from typing import Dict, Any
from variables.helper import BaseConfig

class SQLServerVariables(BaseConfig):
    """
    Configuration mapped to SQL Server environment variables.
    """

    VARIABLES = [
        "SQLSERVER_HOST",
        "SQLSERVER_PORT",
        "SQLSERVER_DATABASE",
        "SQLSERVER_USERNAME",
        "SQLSERVER_PASSWORD",
        "SQLSERVER_DRIVER"
    ]

    @classmethod
    def config(cls) -> Dict[str, Any]:
        """
        Retrieve SQL Server configuration as a dictionary.

        Returns:
            Dict[str, Any]: Values mapped from environment variables.
        """
        return cls.load()
