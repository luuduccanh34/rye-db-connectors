# from dataclasses import dataclass
# from typing import Optional
# from connectors.sqlserver.connector import SQLServerConnector
#
# connector = SQLServerConnector()
# print(connector.execute_query("SELECT 1"))

import platform
import pyodbc

# Tắt pooling trên macOS để tránh lỗi segmentation fault từ unixODBC
if platform.system() == "Darwin":
    pyodbc.pooling = False

# Thay thế thông tin chính xác của bạn vào đây
conn_str = "DRIVER=ODBC Driver 18 for SQL Server;SERVER=118.69.140.120,1433;DATABASE=PDWM_QAS;UID=admin;PWD=@Dm!n2024;Encrypt=yes;TrustServerCertificate=yes;"

print("--- Đang thử kết nối trực tiếp ---")
try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    print("Kết quả test:", cursor.fetchone())
    conn.close()
    print("🎉 Kết nối thành công! Lỗi nằm ở logic bóc tách class.")
except Exception as e:
    print("❌ Thất bại nhưng không crash Python:", e)