"""Database loader and SQL analytics execution engine supporting DuckDB and PostgreSQL."""

from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd

from banking_analytics.utils.exceptions import DBConnectionError
from banking_analytics.utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """Unified database interface managing DuckDB and PostgreSQL backends."""

    def __init__(self, config: Dict[str, Any]):
        """Initializes database manager with configuration parameters."""
        self.config = config
        db_conf = config.get("database", {})
        self.backend = db_conf.get("backend", "duckdb").lower()
        self.duckdb_path = db_conf.get("duckdb", {}).get("path", "data/banking_analytics.duckdb")
        self.pg_conf = db_conf.get("postgresql", {})
        self._duckdb_conn = None

    def get_connection(self):
        """Establishes and returns an active connection to the configured database.

        Returns:
            DuckDB connection object or SQLAlchemy / psycopg2 connection.

        Raises:
            DBConnectionError: If connection cannot be established.
        """
        if self.backend == "duckdb":
            try:
                import duckdb
                Path(self.duckdb_path).parent.mkdir(parents=True, exist_ok=True)
                if self._duckdb_conn is None:
                    self._duckdb_conn = duckdb.connect(self.duckdb_path)
                logger.info("Connected to DuckDB database at: %s", self.duckdb_path)
                return self._duckdb_conn
            except Exception as exc:
                raise DBConnectionError(
                    f"Failed to connect to DuckDB: {exc}",
                    module="db_loader.get_connection",
                    action=f"Verify write permissions for path {self.duckdb_path}.",
                ) from exc

        elif self.backend == "postgresql":
            try:
                from sqlalchemy import create_engine
                host = self.pg_conf.get("host", "localhost")
                port = self.pg_conf.get("port", 5432)
                dbname = self.pg_conf.get("dbname", "banking_analytics")
                user = self.pg_conf.get("user", "postgres")
                password = self.pg_conf.get("password", "")
                url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
                engine = create_engine(url)
                conn = engine.connect()
                logger.info("Connected to PostgreSQL at %s:%s/%s", host, port, dbname)
                return conn
            except Exception as exc:
                raise DBConnectionError(
                    f"Failed to connect to PostgreSQL: {exc}",
                    module="db_loader.get_connection",
                    action="Ensure PostgreSQL is running and credentials in .env are correct, or switch database.backend to 'duckdb' in config/config.yaml.",
                ) from exc
        else:
            raise DBConnectionError(
                f"Unsupported database backend: '{self.backend}'",
                module="db_loader.get_connection",
                action="Set database.backend to 'duckdb' or 'postgresql' in config/config.yaml.",
            )

    def init_schema(self, schema_path: str = "sql/schema/create_tables.sql") -> None:
        """Executes table creation DDL from specified SQL script."""
        path = Path(schema_path)
        if not path.is_file():
            raise FileNotFoundError(f"Schema file not found at: {schema_path}")

        conn = self.get_connection()
        ddl_sql = path.read_text(encoding="utf-8")

        # Normalize column types if running on duckdb
        if self.backend == "duckdb":
            # DuckDB handles standard DDL seamlessly
            # Execute statement by statement
            statements = [s.strip() for s in ddl_sql.split(";") if s.strip()]
            for stmt in statements:
                conn.execute(stmt)
        else:
            # PostgreSQL execution
            from sqlalchemy import text
            for stmt in [s.strip() for s in ddl_sql.split(";") if s.strip()]:
                conn.execute(text(stmt))
            conn.commit()

        logger.info("Database schema initialized successfully from: %s", schema_path)

    def load_data(self, df: pd.DataFrame, table_name: str = "loan_applications") -> None:
        """Loads a pandas DataFrame into the database table, replacing existing rows."""
        # Lowercase column names for SQL consistency
        load_df = df.copy()
        load_df.columns = [col.lower() for col in load_df.columns]

        conn = self.get_connection()
        if self.backend == "duckdb":
            conn.register("temp_staging_df", load_df)
            conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM temp_staging_df")
            conn.unregister("temp_staging_df")
        else:
            load_df.to_sql(table_name, con=conn, if_exists="replace", index=False)

        logger.info("Loaded %d records into table '%s'", len(load_df), table_name)

    def create_views(self, views_dir: str = "sql/queries/views") -> None:
        """Executes all view creation SQL files in the views directory."""
        v_dir = Path(views_dir)
        if not v_dir.is_dir():
            logger.warning("Views directory '%s' does not exist.", views_dir)
            return

        conn = self.get_connection()
        view_files = sorted(list(v_dir.glob("*.sql")))
        for v_file in view_files:
            v_sql = v_file.read_text(encoding="utf-8")
            if self.backend == "duckdb":
                conn.execute(v_sql)
            else:
                from sqlalchemy import text
                conn.execute(text(v_sql))
                conn.commit()
            logger.info("Created view from: %s", v_file.name)

    def run_query(self, query_sql: str) -> pd.DataFrame:
        """Executes a SQL query string and returns the result as a pandas DataFrame."""
        conn = self.get_connection()
        if self.backend == "duckdb":
            return conn.execute(query_sql).df()
        else:
            return pd.read_sql_query(query_sql, con=conn)

    def run_query_file(self, query_file_path: str) -> pd.DataFrame:
        """Executes a SQL query from file and returns the result as a pandas DataFrame."""
        path = Path(query_file_path)
        if not path.is_file():
            raise FileNotFoundError(f"Query file not found at: {query_file_path}")
        query_sql = path.read_text(encoding="utf-8")
        return self.run_query(query_sql)

    def execute_all_queries(self, queries_dir: str = "sql/queries") -> Dict[str, pd.DataFrame]:
        """Runs all analytical query files (q01-q06) and returns dictionary of results."""
        q_dir = Path(queries_dir)
        results = {}
        for q_file in sorted(list(q_dir.glob("q*.sql"))):
            logger.info("Executing analytical query: %s", q_file.name)
            df_res = self.run_query_file(str(q_file))
            results[q_file.stem] = df_res
        return results

    def close(self):
        """Closes any open database connections."""
        if self._duckdb_conn is not None:
            self._duckdb_conn.close()
            self._duckdb_conn = None
