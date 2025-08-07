import os
import math
import datetime
import decimal
import pymysql

from dbutils.pooled_db import PooledDB

from src.model import DatabaseConfig
from src.strategy.database_strategy import DatabaseStrategy


class MySQLStrategy(DatabaseStrategy):

    def __init__(self, config: DatabaseConfig):
        super().__init__(config)
        self.pool = None

    def create_pool(self) -> PooledDB:
        if not self.pool:
            self.pool = PooledDB(
                creator=pymysql,
                host=self.config.host,
                port=self.config.port,
                user=self.config.user,
                password=self.config.password,
                database=self.config.database,
                mincached=self.config.minCached or 5,
                maxcached=self.config.maxCached or 10,
                maxconnections=self.config.maxConnections or 20,
            )
        return self.pool

    def get_connection(self) -> pymysql.connections.Connection:
        if not self.pool:
            self.create_pool()
        return self.pool.connection()

    def close_connection(self, connection: object) -> None:
        if connection:
            connection.close()

    def list_tables(self) -> str:
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT TABLE_NAME, TABLE_COMMENT
                    FROM information_schema.tables
                    WHERE TABLE_SCHEMA = %s
                    """,
                    (self.config.database,),
                )
            tables = cursor.fetchall()

            headers = ["TABLE_NAME", "TABLE_COMMENT"]
            return self.format_table(headers, list(tables))
        finally:
            self.close_connection(connection)

    def describe_Table(self, table_name: str) -> str:
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COLUMN_NAME,
                           COLUMN_COMMENT,
                           DATA_TYPE,
                           COLUMN_TYPE,
                           COLUMN_DEFAULT,
                           COLUMN_KEY,
                           IS_NULLABLE,
                           EXTRA
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = %s
                      AND TABLE_NAME = %s;
                    """,
                    (
                        self.config.database,
                        table_name,
                    ),
                )
                table_infos = cursor.fetchall()

                result_infos = []

                for table_info in table_infos:
                    cursor.execute(
                        """
                        SELECT INDEX_NAME
                        FROM INFORMATION_SCHEMA.STATISTICS
                        WHERE TABLE_SCHEMA = %s
                          AND TABLE_NAME = %s
                          AND COLUMN_NAME = %s
                        """,
                        (
                            self.config.database,
                            table_name,
                            table_info[0],
                        ),
                    )
                    index_results = cursor.fetchall()

                    index_names = [row[0] for row in index_results]

                    if index_names:
                        info_list = list(table_info)
                        if info_list[5]:
                            info_list[5] = f"{info_list[5]} ({', '.join(index_names)})"
                        result_infos.append(tuple(info_list))
                    else:
                        result_infos.append(table_info)

                headers = [
                    "COLUMN_NAME",
                    "COLUMN_COMMENT",
                    "DATA_TYPE",
                    "COLUMN_TYPE",
                    "COLUMN_DEFAULT",
                    "COLUMN_KEY",
                    "IS_NULLABLE",
                    "EXTRA",
                ]
            return self.format_table(headers, result_infos)
        finally:
            self.close_connection(connection)

    def execute_sql(self, sql: str, params: tuple = None) -> str:
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                sql_stripped = sql.strip()
                if sql_stripped.upper().startswith("SELECT"):
                    cursor.execute(sql_stripped, params)
                    column_names = [desc[0] for desc in cursor.description]
                    result = cursor.fetchall()
                    return self.format_table(column_names, list(result))
                else:
                    connection.begin()
                    affected_rows = cursor.execute(sql_stripped, params)
                    return self.format_update(affected_rows)
        finally:
            self.close_connection(connection)

    def export_data(self, table_name: str, file_path: str = None) -> str:
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                if not table_name.replace('_', '').replace('-', '').isalnum():
                    raise ValueError(f"Invalid table name: {table_name}")

                cursor.execute(
                    f"""
                    SELECT COUNT(*)
                    FROM {table_name}
                    """
                )
                count = cursor.fetchone()[0]
                if count < 0:
                    return f"Table '{table_name}' does not data."

                if not file_path:
                    # 使用脚本所在目录的相对路径，确保始终在项目根目录下创建
                    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    file_path = os.path.join(script_dir, "export_data")

                # 确保目录存在
                os.makedirs(file_path, exist_ok=True)

                # 将count 平均拆分1000条一个文件
                batch_size = 1000
                file_count = math.ceil(count / batch_size)

                for i in range(file_count):
                    start = i * batch_size
                    end = min((i + 1) * batch_size, count)
                    cursor.execute(
                        f"""
                        SELECT *
                        FROM {table_name}
                        LIMIT {start}, {end - start}
                        """
                    )
                    rows = cursor.fetchall()

                    if not rows:
                        continue

                    headers = [desc[0] for desc in cursor.description]

                    # 组装为insert sql
                    insert_values = []
                    for row in rows:
                        values = []
                        for val in row:
                            if val is None:
                                values.append("NULL")
                            elif isinstance(val, str):
                                # 转义单引号并添加引号
                                escaped_val = val.replace("'", "''")
                                values.append(f"'{escaped_val}'")
                            elif isinstance(val, (datetime.datetime, datetime.date, datetime.time)):
                                # 日期时间类型需要加引号
                                values.append(f"'{val}'")
                            elif isinstance(val, bytes):
                                # 二进制数据转为十六进制
                                hex_val = val.hex()
                                values.append(f"0x{hex_val}")
                            elif isinstance(val, bool):
                                # 布尔值转为1或0
                                values.append("1" if val else "0")
                            elif isinstance(val, (int, float, decimal.Decimal)):
                                # 数字类型直接转字符串
                                values.append(str(val))
                            else:
                                # 其他类型当作字符串处理
                                escaped_val = str(val).replace("'", "''")
                                values.append(f"'{escaped_val}'")
                        insert_values.append(f"({', '.join(values)})")

                    insert_sql = f"INSERT INTO {table_name} ({', '.join(headers)}) VALUES "
                    insert_sql += ", ".join(insert_values) + ";"

                    # 写入文件，确保路径正确
                    file_name = os.path.join(file_path, f"{table_name}_{i}.sql")
                    with open(file_name, "w", encoding='utf-8') as f:
                        f.write(insert_sql)

                return f"Exported {count} rows to {file_path}."
        finally:
            self.close_connection(connection)
