import platform
import pyodbc
from typing import Any, Optional, List, Dict
from connectors.base.connector import BaseConnector

# Tắt connection pooling trên macOS để tránh lỗi memory corruption / segmentation fault từ unixODBC
if platform.system() == "Darwin":
    pyodbc.pooling = False

class SQLServerConnector(BaseConnector):
    """
    SQL Server database connector.

    This class handles connecting to a SQL Server database, executing queries,
    and managing the connection lifecycle.
    """

    def __init__(self, config: Optional[List[Any]] = None):
        """
        Initializes the SQL Server connector.

        Args:
            config (Optional[List[Any]]): A list containing configuration objects.
                If provided, the first element is used as the configuration.
                Otherwise, the configuration is loaded from environment variables.
        """
        if config and len(config) > 0:
            self.config = config[0]
        else:
            from variables.sqlserver import SQLServerVariables
            self.config = SQLServerVariables.config()

        # Xử lý parse chuỗi connection string từ Object hoặc Dictionary
        if isinstance(self.config, dict):
            # Clean data (strip các dấu nháy đơn/kép nếu bị dính từ file .env)
            driver = self.config.get("SQLSERVER_DRIVER", "ODBC Driver 17 for SQL Server").strip("'\"")
            host = self.config.get("SQLSERVER_HOST", "").strip("'\"")
            port = self.config.get("SQLSERVER_PORT", "1433").strip("'\"")
            database = self.config.get("SQLSERVER_DATABASE", "").strip("'\"")
            username = self.config.get("SQLSERVER_USERNAME", "").strip("'\"")
            password = self.config.get("SQLSERVER_PASSWORD", "").strip("'\"")

            # Đảm bảo định dạng DRIVER khớp với chuỗi test thành công của bạn (không ép thêm dấu ngoặc nhọn {})
            if not driver.startswith("{") and not driver.endswith("}"):
                driver_str = f"DRIVER={driver};"
            else:
                driver_str = f"DRIVER={driver};"

            # Xây dựng chuỗi ODBC Connection String tiêu chuẩn
            self.connection_string = (
                f"{driver_str}"
                f"SERVER={host},{port};"
                f"DATABASE={database};"
                f"UID={username};"
                f"PWD={password};"
                f"Encrypt=yes;"
                f"TrustServerCertificate=yes;"
            )
        else:
            # Nếu config là một Object/Dataclass, tìm thuộc tính hoặc method sinh string của nó
            if hasattr(self.config, "get_connection_string"):
                self.connection_string = self.config.get_connection_string()
            else:
                self.connection_string = getattr(self.config, "connection_string", str(self.config))

        self.connection: Optional[pyodbc.Connection] = None

    def connect(self) -> pyodbc.Connection:
        """
        Establishes a connection to the SQL Server database if one does not exist.

        Returns:
            pyodbc.Connection: The active database connection instance.
        """
        if not self.connection:
            self.connection = pyodbc.connect(self.connection_string)
        return self.connection

    def close(self) -> None:
        """
        Closes the active database connection and resets the connection state.
        """
        if self.connection:
            self.connection.close()
            self.connection = None

    def execute_query(self, query: str, params: Optional[tuple] = None, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Executes a SQL query and returns the results.

        Args:
            query (str): The SQL query string to be executed.
            params (Optional[tuple]): Optional parameters to bind to the query.
            **kwargs (Any): Additional keyword arguments.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries representing the fetched rows,
                where keys are column names and values are the row values.
        """
        conn = self.connect()
        results: List[Dict[str, Any]] = []

        with conn.cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if cursor.description:
                columns = [column[0] for column in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            else:
                conn.commit()

        return results