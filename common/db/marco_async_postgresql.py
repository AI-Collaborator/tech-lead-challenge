import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import status as http_status, HTTPException
from psycopg_pool import AsyncConnectionPool


class MarcoAsyncPostgreSQL():
    def __init__(
        self,
        dbname: str = "testdb",
        dbuser: str = "postgres",
        password: str = "password123",
        host: str = "localhost",
        port: int = 5434,
        ssl_mode: str = "prefer",
    ) -> None:
        # Prevent re-initialization of singleton instance
        if hasattr(self, "_initialized") and self._initialized:
            return

        self._initialized = True
        self.db_connection: Optional[AsyncConnectionPool] = None

        # Store connection parameters for later initialization
        self.dbname = dbname
        self.dbuser = dbuser
        self.password = password
        self.host = host
        self.port = port
        self.ssl_mode = ssl_mode

    async def initialize(self):
        """Initialize the connection pool asynchronously"""
        if self.db_connection is not None:
            return

        try:
            connection_string = f"dbname={self.dbname} user={self.dbuser} password={self.password} host={self.host} port={self.port} sslmode={self.ssl_mode}"
            # Create pool as an async context manager
            self.db_connection = AsyncConnectionPool(
                connection_string,
                min_size=1,
                max_size=10,
                timeout=30,
                kwargs={},
                open=False,
            )
            await self.db_connection.open()

            logging.debug(
                f"Pool initialized: {self.host}:{self.port}/{self.dbname} (user: {self.dbuser}) | "
                f"Pool size: {self.db_connection.min_size}-{self.db_connection.max_size}, "
                f"timeout: {self.db_connection.timeout}s"
            )
        except Exception as e:
            logging.error(f"Pool initialization failed: {str(e)}")
            raise Exception(f"Pool initialization failed: {e}")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    @asynccontextmanager
    async def get_cursor(self):
        """Async context manager for getting a database cursor"""
        connection = None
        cursor = None
        try:
            connection = await self.get_connection()
            cursor = connection.cursor()
            yield cursor
            await connection.commit()
        except Exception as e:
            if connection:
                await connection.rollback()
            raise e
        finally:
            if cursor:
                await cursor.close()
            if connection:
                await self.release_connection(connection)

    def _get_pool_stats(self) -> str:
        """Helper method to get formatted pool statistics"""
        if not self.db_connection:
            return "Pool not initialized"
        return (
            f"[total: {len(self.db_connection._pool)}, "
            f"min: {self.db_connection.min_size}, "
            f"max: {self.db_connection.max_size}, "
            f"timeout: {self.db_connection.timeout}s]"
        )

    async def close_pool(self) -> None:
        if self.db_connection:
            logging.debug(f"Closing connection pool {self._get_pool_stats()}")
            await self.db_connection.close()
            logging.debug("Pool closed successfully")

    async def get_connection(self):
        """Ensure pool is initialized before getting a connection"""
        if not self.db_connection:
            await self.initialize()

        max_retries = 3
        for attempt in range(max_retries):
            try:
                if self.db_connection:
                    pool_stats = self._get_pool_stats()
                    logging.debug(f"Getting connection... {pool_stats}")
                    connection = await self.db_connection.getconn()
                    if connection is None:
                        raise HTTPException(
                            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to obtain a connection from the pool",
                        )

                    # Test connection with a simple query
                    try:
                        async with connection.cursor() as status_cursor:
                            await status_cursor.execute(
                                "SELECT version(), current_timestamp, pg_backend_pid()"
                            )
                            version, timestamp, pid = await status_cursor.fetchone()
                            logging.debug(
                                f"Connection obtained - Backend PID: {pid} | "
                                f"Server Time: {timestamp} | "
                                f"Pool Status: {pool_stats}"
                            )
                        return connection
                    except Exception as conn_test_error:
                        # Connection test failed, return connection to pool and retry
                        logging.warning(
                            f"Connection test failed: {str(conn_test_error)}"
                        )
                        try:
                            await self.db_connection.putconn(connection)
                        except:
                            pass  # Ignore errors when returning bad connection
                        if attempt == max_retries - 1:
                            raise conn_test_error
                        continue
            except Exception as e:
                if attempt == max_retries - 1:
                    raise HTTPException(
                        status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Error getting connection: {str(e)}",
                    )
                logging.warning(f"Connection attempt {attempt + 1} failed: {str(e)}")
                continue

    async def release_connection(self, connection) -> None:
        try:
            if self.db_connection and connection:
                pool_stats = self._get_pool_stats()
                logging.debug(
                    f"Returning connection (PID: {connection.info.backend_pid})... {pool_stats}"
                )
                await self.db_connection.putconn(connection)
                logging.debug(f"Connection returned successfully {pool_stats}")
        except Exception as e:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error releasing connection: {str(e)}",
            )

    async def open_pool(self):
        """Explicitly open the connection pool."""
        if not self.db_connection:
            try:
                connection_string = f"dbname={self.dbname} user={self.dbuser} password={self.password} host={self.host} port={self.port} sslmode={self.ssl_mode}"
                logging.info(
                    f"Attempting to connect to database: {self.host}:{self.port}/{self.dbname}"
                )

                self.db_connection = AsyncConnectionPool(
                    connection_string,
                    min_size=1,
                    max_size=10,
                    timeout=30,
                    kwargs={},
                    open=False,
                )
                await self.db_connection.open()

                logging.debug(
                    f"Pool opened: {self.host}:{self.port}/{self.dbname} (user: {self.dbuser}) | "
                    f"Pool size: {self.db_connection.min_size}-{self.db_connection.max_size}, "
                    f"timeout: {self.db_connection.timeout}s"
                )
            except Exception as e:
                error_message = f"CRITICAL: Failed to connect to database {self.host}:{self.port}/{self.dbname}: {str(e)}"
                logging.critical(error_message)
                raise HTTPException(
                    status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=error_message,
                )
