from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.database import DatabaseConfig, DatabaseType


class DbConnector(ABC):
    """Abstract base class for database connectors"""

    def __init__(self, config: DatabaseConfig):
        self.config = config

    @abstractmethod
    async def get_databases(self) -> List[str]:
        """Get list of all databases"""
        pass

    @abstractmethod
    async def get_tables(self, database: str) -> List[str]:
        """Get list of all tables in a database"""
        pass

    @abstractmethod
    async def get_primary_key(self, database: str, table: str) -> Optional[str]:
        """Get the numeric primary key field name for a table"""
        pass

    @abstractmethod
    async def get_max_id(self, database: str, table: str, pk_field: str) -> Optional[int]:
        """Get the maximum ID value for a table"""
        pass

    @abstractmethod
    async def table_field_exists(self, database: str, table: str, field: str) -> bool:
        """Check if a specific table and field exists in the database"""
        pass

    @abstractmethod
    async def close(self):
        """Close database connection"""
        pass


class MySQLConnector(DbConnector):
    """MySQL database connector"""

    def __init__(self, config: DatabaseConfig):
        super().__init__(config)
        try:
            import aiomysql
            self.aiomysql = aiomysql
        except ImportError:
            raise ImportError(
                "aiomysql is required for MySQL connections. "
                "Install it with: pip install aiomysql"
            )
        self.conn = None
        self.host, self.port = self._parse_address(config.db_address)

    def _parse_address(self, address: str):
        parts = address.split(":")
        host = parts[0]
        port = int(parts[1]) if len(parts) > 1 else 3306
        return host, port

    async def _get_connection(self):
        if self.conn is None:
            self.conn = await self.aiomysql.connect(
                host=self.host,
                port=self.port,
                user=self.config.db_user,
                password=self.config.db_password
            )
        return self.conn

    async def get_databases(self) -> List[str]:
        conn = await self._get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute("SHOW DATABASES")
            result = await cursor.fetchall()
            databases = [row[0] for row in result if row[0] not in ('information_schema', 'mysql', 'performance_schema', 'sys')]
            return databases

    async def get_tables(self, database: str) -> List[str]:
        conn = await self._get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute(f"SHOW TABLES FROM `{database}`")
            result = await cursor.fetchall()
            return [row[0] for row in result]

    async def get_primary_key(self, database: str, table: str) -> Optional[str]:
        conn = await self._get_connection()
        async with conn.cursor() as cursor:
            query = """
                SELECT COLUMN_NAME, DATA_TYPE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_KEY = 'PRI'
                ORDER BY ORDINAL_POSITION
                LIMIT 1
            """
            await cursor.execute(query, (database, table))
            result = await cursor.fetchone()
            if result and result[1] in ('int', 'bigint', 'smallint', 'tinyint', 'mediumint'):
                return result[0]
            return None

    async def get_max_id(self, database: str, table: str, pk_field: str) -> Optional[int]:
        conn = await self._get_connection()
        async with conn.cursor() as cursor:
            query = f"SELECT MAX(`{pk_field}`) FROM `{database}`.`{table}`"
            await cursor.execute(query)
            result = await cursor.fetchone()
            return result[0] if result and result[0] is not None else 0

    async def table_field_exists(self, database: str, table: str, field: str) -> bool:
        conn = await self._get_connection()
        async with conn.cursor() as cursor:
            query = """
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s
            """
            await cursor.execute(query, (database, table, field))
            result = await cursor.fetchone()
            return result[0] > 0 if result else False

    async def close(self):
        if self.conn:
            self.conn.close()


class PostgreSQLConnector(DbConnector):
    """PostgreSQL database connector"""

    def __init__(self, config: DatabaseConfig):
        super().__init__(config)
        try:
            import asyncpg
            self.asyncpg = asyncpg
        except ImportError:
            raise ImportError(
                "asyncpg is required for PostgreSQL connections. "
                "Install it with: pip install asyncpg"
            )
        self.conn = None
        self.host, self.port = self._parse_address(config.db_address)

    def _parse_address(self, address: str):
        parts = address.split(":")
        host = parts[0]
        port = int(parts[1]) if len(parts) > 1 else 5432
        return host, port

    async def _get_connection(self):
        if self.conn is None:
            self.conn = await self.asyncpg.connect(
                host=self.host,
                port=self.port,
                user=self.config.db_user,
                password=self.config.db_password,
                database=self.config.db_name or 'postgres'
            )
        return self.conn

    async def get_databases(self) -> List[str]:
        conn = await self._get_connection()
        result = await conn.fetch("SELECT datname FROM pg_database WHERE datistemplate = false")
        databases = [row['datname'] for row in result if row['datname'] not in ('postgres',)]
        return databases

    async def get_tables(self, database: str) -> List[str]:
        conn = await self._get_connection()
        result = await conn.fetch("""
            SELECT tablename FROM pg_tables
            WHERE schemaname = 'public'
        """)
        return [row['tablename'] for row in result]

    async def get_primary_key(self, database: str, table: str) -> Optional[str]:
        conn = await self._get_connection()
        query = """
            SELECT a.attname, format_type(a.atttypid, a.atttypmod) as data_type
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = $1::regclass AND i.indisprimary
            LIMIT 1
        """
        result = await conn.fetchrow(query, table)
        if result and result['data_type'] in ('integer', 'bigint', 'smallint'):
            return result['attname']
        return None

    async def get_max_id(self, database: str, table: str, pk_field: str) -> Optional[int]:
        conn = await self._get_connection()
        query = f'SELECT MAX("{pk_field}") FROM "{table}"'
        result = await conn.fetchval(query)
        return result if result is not None else 0

    async def table_field_exists(self, database: str, table: str, field: str) -> bool:
        conn = await self._get_connection()
        query = """
            SELECT COUNT(*)
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = $1 AND column_name = $2
        """
        result = await conn.fetchval(query, table, field)
        return result > 0 if result else False

    async def close(self):
        if self.conn:
            await self.conn.close()


class SQLServerConnector(DbConnector):
    """SQL Server database connector (using pyodbc - synchronous)"""

    def __init__(self, config: DatabaseConfig):
        super().__init__(config)
        try:
            import pyodbc
            self.pyodbc = pyodbc
        except ImportError:
            raise ImportError(
                "pyodbc is required for SQL Server connections. "
                "Install it with: pip install pyodbc\n"
                "Also install ODBC Driver: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server"
            )
        self.conn = None
        self.host, self.port = self._parse_address(config.db_address)

    def _parse_address(self, address: str):
        parts = address.split(":")
        host = parts[0]
        port = int(parts[1]) if len(parts) > 1 else 1433
        return host, port

    def _get_connection(self):
        if self.conn is None:
            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.host},{self.port};UID={self.config.db_user};PWD={self.config.db_password}"
            self.conn = self.pyodbc.connect(conn_str)
        return self.conn

    async def get_databases(self) -> List[str]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sys.databases WHERE name NOT IN ('master', 'tempdb', 'model', 'msdb')")
        databases = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return databases

    async def get_tables(self, database: str) -> List[str]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT TABLE_NAME FROM [{database}].INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return tables

    async def get_primary_key(self, database: str, table: str) -> Optional[str]:
        conn = self._get_connection()
        cursor = conn.cursor()
        query = f"""
            SELECT c.COLUMN_NAME, c.DATA_TYPE
            FROM [{database}].INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
            JOIN [{database}].INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE cu ON tc.CONSTRAINT_NAME = cu.CONSTRAINT_NAME
            JOIN [{database}].INFORMATION_SCHEMA.COLUMNS c ON cu.COLUMN_NAME = c.COLUMN_NAME AND cu.TABLE_NAME = c.TABLE_NAME
            WHERE tc.CONSTRAINT_TYPE = 'PRIMARY KEY' AND tc.TABLE_NAME = ?
        """
        cursor.execute(query, (table,))
        result = cursor.fetchone()
        cursor.close()
        if result and result[1] in ('int', 'bigint', 'smallint', 'tinyint'):
            return result[0]
        return None

    async def get_max_id(self, database: str, table: str, pk_field: str) -> Optional[int]:
        conn = self._get_connection()
        cursor = conn.cursor()
        query = f"SELECT MAX([{pk_field}]) FROM [{database}].dbo.[{table}]"
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result and result[0] is not None else 0

    async def table_field_exists(self, database: str, table: str, field: str) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        query = f"""
            SELECT COUNT(*)
            FROM [{database}].INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = ? AND COLUMN_NAME = ?
        """
        cursor.execute(query, (table, field))
        result = cursor.fetchone()
        cursor.close()
        return result[0] > 0 if result else False

    async def close(self):
        if self.conn:
            self.conn.close()


class OracleConnector(DbConnector):
    """Oracle database connector (synchronous)"""

    def __init__(self, config: DatabaseConfig):
        super().__init__(config)
        try:
            import cx_Oracle
            self.cx_Oracle = cx_Oracle
        except ImportError:
            raise ImportError(
                "cx_Oracle is required for Oracle connections. "
                "Install it with: pip install cx_Oracle\n"
                "Also install Oracle Instant Client: https://www.oracle.com/database/technologies/instant-client.html"
            )
        self.conn = None
        self.host, self.port = self._parse_address(config.db_address)

    def _parse_address(self, address: str):
        parts = address.split(":")
        host = parts[0]
        port = int(parts[1]) if len(parts) > 1 else 1521
        return host, port

    def _get_connection(self):
        if self.conn is None:
            dsn = self.cx_Oracle.makedsn(self.host, self.port, service_name=self.config.db_name or 'ORCL')
            self.conn = self.cx_Oracle.connect(user=self.config.db_user, password=self.config.db_password, dsn=dsn)
        return self.conn

    async def get_databases(self) -> List[str]:
        return [self.config.db_name or 'ORCL']

    async def get_tables(self, database: str) -> List[str]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT table_name FROM user_tables")
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return tables

    async def get_primary_key(self, database: str, table: str) -> Optional[str]:
        conn = self._get_connection()
        cursor = conn.cursor()
        query = """
            SELECT cols.column_name, cols.data_type
            FROM all_constraints cons
            JOIN all_cons_columns cols ON cons.constraint_name = cols.constraint_name
            WHERE cons.constraint_type = 'P' AND cons.table_name = :table_name
            AND ROWNUM = 1
        """
        cursor.execute(query, {'table_name': table.upper()})
        result = cursor.fetchone()
        cursor.close()
        if result and result[1] in ('NUMBER',):
            return result[0]
        return None

    async def get_max_id(self, database: str, table: str, pk_field: str) -> Optional[int]:
        conn = self._get_connection()
        cursor = conn.cursor()
        query = f"SELECT MAX({pk_field}) FROM {table}"
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result and result[0] is not None else 0

    async def table_field_exists(self, database: str, table: str, field: str) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        query = """
            SELECT COUNT(*)
            FROM all_tab_columns
            WHERE table_name = :table_name AND column_name = :column_name
        """
        cursor.execute(query, {'table_name': table.upper(), 'column_name': field.upper()})
        result = cursor.fetchone()
        cursor.close()
        return result[0] > 0 if result else False

    async def close(self):
        if self.conn:
            self.conn.close()


class DbConnectorFactory:
    """Factory class to create database connectors"""

    @staticmethod
    def create(config: DatabaseConfig) -> DbConnector:
        if config.db_type == DatabaseType.MYSQL:
            return MySQLConnector(config)
        elif config.db_type == DatabaseType.POSTGRESQL:
            return PostgreSQLConnector(config)
        elif config.db_type == DatabaseType.SQLSERVER:
            return SQLServerConnector(config)
        elif config.db_type == DatabaseType.ORACLE:
            return OracleConnector(config)
        else:
            raise ValueError(f"Unsupported database type: {config.db_type}")
