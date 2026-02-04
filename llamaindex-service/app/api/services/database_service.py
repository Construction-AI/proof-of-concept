import sqlite3
from typing import Optional
from app.core.logger import get_logger


class DatabaseService:
    DATABASE_FILE_NAME = "/data/database.db"
    USERS_TABLE_NAME = "users"

    def __init__(self):
        # 🔧 CHANGE: enable row access by column name (optional but useful)
        self.connection = sqlite3.connect(
            DatabaseService.DATABASE_FILE_NAME,
            check_same_thread=False
        )
        self.connection.row_factory = sqlite3.Row

        # 🔧 CHANGE: cursor is no longer stored persistently
        self.logger = get_logger("DatabaseService")

        # 🔧 CHANGE: initialize table safely
        if not self.__check_table_exists(DatabaseService.USERS_TABLE_NAME):
            self.__create_users_table()

    ###########
    # INTERNAL
    ###########
    def __check_table_exists(self, table: str) -> bool:
        """
        Checks whether a table exists in the SQLite database.
        """
        try:
            query = """
                SELECT 1
                FROM sqlite_master
                WHERE type='table' AND name=?
                LIMIT 1;
            """
            # 🔧 CHANGE: correct tuple usage (table,)
            return self.connection.execute(query, (table,)).fetchone() is not None

        except sqlite3.Error as e:
            # 🔧 CHANGE: log error instead of swallowing it silently
            self.logger.error(f"Table check failed: {e}")
            return False

    def __create_users_table(self) -> None:
        """
        Creates the users table.
        """
        try:
            # 🔧 CHANGE: table name must be interpolated directly (safe because constant)
            self.connection.execute(
                f"DROP TABLE IF EXISTS {DatabaseService.USERS_TABLE_NAME}"
            )

            # 🔧 CHANGE: add PRIMARY KEY and correct SQLite types
            self.connection.execute(
                f"""
                CREATE TABLE {DatabaseService.USERS_TABLE_NAME} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE
                );
                """
            )

            # 🔧 CHANGE: commit schema changes
            self.connection.commit()

            self.logger.info(f"{DatabaseService.USERS_TABLE_NAME} table created")

        except sqlite3.Error as e:
            self.connection.rollback()
            self.logger.error(
                f"Error creating {DatabaseService.USERS_TABLE_NAME} table: {e}"
            )

    ###########
    # USER DATA
    ###########
    def create_user(self, first_name: str, last_name: str, email: str) -> None:
        """
        Inserts a new user safely.
        """
        try:
            # 🔧 CHANGE: parameterized query (prevents SQL injection)
            self.connection.execute(
                f"""
                INSERT INTO {DatabaseService.USERS_TABLE_NAME}
                (first_name, last_name, email)
                VALUES (?, ?, ?)
                """,
                (first_name, last_name, email)
            )

            # 🔧 CHANGE: commit data change
            self.connection.commit()

        except sqlite3.Error as e:
            self.connection.rollback()
            self.logger.error(f"Error creating user: {e}")

    def read_user(self, user_id: int) -> Optional[sqlite3.Row]:
        """
        Reads a single user by ID.
        """
        try:
            # 🔧 CHANGE: safe parameter usage
            cursor = self.connection.execute(
                f"""
                SELECT *
                FROM {DatabaseService.USERS_TABLE_NAME}
                WHERE id = ?
                """,
                (user_id,)
            )

            # 🔧 CHANGE: return actual data, not cursor
            return cursor.fetchone()

        except sqlite3.Error as e:
            self.logger.error(f"Error reading user: {e}")
            return None

    def read_all_users(self) -> list[sqlite3.Row]:
        """
        Reads all users.
        """
        try:
            cursor = self.connection.execute(
                f"SELECT * FROM {DatabaseService.USERS_TABLE_NAME}"
            )

            # 🔧 CHANGE: return data, not cursor
            return cursor.fetchall()

        except sqlite3.Error as e:
            self.logger.error(f"Error reading all users: {e}")
            return []

    ###########
    # CLEANUP
    ###########
    def close(self) -> None:
        """
        Closes the database connection.
        """
        self.connection.close()
