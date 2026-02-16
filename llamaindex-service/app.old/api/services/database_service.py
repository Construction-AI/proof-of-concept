import sqlite3
from typing import Optional
from app.core.logger import get_logger


class DatabaseService:
    DATABASE_FILE_NAME = "/data/database.db"
    USERS_TABLE_NAME = "users"
    PROJECTS_TABLE_NAME = "projects"
    DOCUMENTS_TABLE_NAME = "documents"

    def __init__(self):
        # 🔧 CHANGE: enable row access by column name (optional but useful)
        self.connection = sqlite3.connect(
            DatabaseService.DATABASE_FILE_NAME,
            check_same_thread=False
        )
        self.connection.row_factory = sqlite3.Row
        self.logger = get_logger("DatabaseService")
        self.__init_base_tables()

    ###########
    # INTERNAL
    ###########
    def __init_base_tables(self) -> None:
        if not self.__check_table_exists(DatabaseService.USERS_TABLE_NAME):
            self.__create_users_table()
        if not self.__check_table_exists(DatabaseService.PROJECTS_TABLE_NAME):
            self.__create_projects_table()
        if not self.__check_table_exists(DatabaseService.DOCUMENTS_TABLE_NAME):
            self.__create_documents_table()
    
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
                    email TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    modified_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
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
            
    def __create_projects_table(self) -> None:
        """
        Creates the projects table.
        Projects are linked to users via a foreign key.
        """
        try:
            # 🔧 CHANGE: drop correct table
            self.connection.execute(
                f"DROP TABLE IF EXISTS {DatabaseService.PROJECTS_TABLE_NAME}"
            )

            # 🔧 CHANGE: proper schema + foreign key constraint
            self.connection.execute(
                f"""
                CREATE TABLE {DatabaseService.PROJECTS_TABLE_NAME} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    user_id INTEGER NOT NULL,

                    name TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    modified_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                    FOREIGN KEY (user_id)
                        REFERENCES {DatabaseService.USERS_TABLE_NAME}(id)
                        ON DELETE CASCADE
                        ON UPDATE CASCADE
                );
                """
            )

            self.connection.commit()

            # 🔧 CHANGE: correct log message
            self.logger.info(f"{DatabaseService.PROJECTS_TABLE_NAME} table created")

        except sqlite3.Error as e:
            self.connection.rollback()
            self.logger.error(
                f"Error creating {DatabaseService.PROJECTS_TABLE_NAME} table: {e}"
            )
            
    def __create_documents_table(self) -> None:
        """
        Creates the documents table.
        Documents are linked to projects via a foreign key.
        """
        try:
            self.connection.execute(
                f"DROP TABLE IF EXISTS {DatabaseService.DOCUMENTS_TABLE_NAME}"
            )

            self.connection.execute(
                f"""
                CREATE TABLE {DatabaseService.DOCUMENTS_TABLE_NAME} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    project_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,

                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    modified_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                    FOREIGN KEY (project_id)
                        REFERENCES {DatabaseService.PROJECTS_TABLE_NAME}(id)
                        ON DELETE CASCADE
                        ON UPDATE CASCADE,
                        
                    FOREIGN KEY (user_id)
                        REFERENCES {DatabaseService.USERS_TABLE_NAME}(id)
                        ON DELETE CASCADE
                        ON UPDATE CASCADE
                );
                """
            )

            self.connection.commit()

            # 🔧 CHANGE: correct log message
            self.logger.info(f"{DatabaseService.DOCUMENTS_TABLE_NAME} table created")

        except sqlite3.Error as e:
            self.connection.rollback()
            self.logger.error(
                f"Error creating {DatabaseService.DOCUMENTS_TABLE_NAME} table: {e}"
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
            cursor = self.connection.execute(
                f"""
                INSERT INTO {DatabaseService.USERS_TABLE_NAME}
                (first_name, last_name, email)
                VALUES (?, ?, ?)
                """,
                (first_name, last_name, email)
            )

            # 🔧 CHANGE: commit data change
            self.connection.commit()
            return cursor.rowcount == 1

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
    # PROJECTS
    ###########
    def create_project(self, project_name: str, user_id: int) -> None:
        """
        Inserts a new project.
        """
        try:
            # Simple check if user_id is valid
            user = self.read_user(user_id=user_id)
            if not user:
                raise ValueError(f"User with given id '{user_id}' does not exist. Project '{project_name}' was not created.")
            
            cursor = self.connection.execute(
                f"""
                INSERT INTO {DatabaseService.PROJECTS_TABLE_NAME}
                (name, user_id, created_at, modified_at)
                VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """,
                (project_name, user_id)
            )

            self.connection.commit()
            return cursor.rowcount == 1

        except sqlite3.Error as e:
            self.connection.rollback()
            self.logger.error(f"Error creating project: {e}")

    def read_project(self, project_id: int) -> Optional[sqlite3.Row]:
        """
        Reads a single project by ID.
        """
        try:
            cursor = self.connection.execute(
                f"""
                SELECT *
                FROM {DatabaseService.PROJECTS_TABLE_NAME}
                WHERE id = ?
                """,
                (project_id,)
            )
            return cursor.fetchone()

        except sqlite3.Error as e:
            self.logger.error(f"Error reading project: {e}")
            return None

    def read_projects_by_user_id(self, user_id: int) -> list[sqlite3.Row]:
        """
        Reads all projects for given user_id.
        """
        try:
            cursor = self.connection.execute(
                f"SELECT * FROM {DatabaseService.PROJECTS_TABLE_NAME} WHERE user_id = ?",
                (user_id,)
            )

            return cursor.fetchall()

        except sqlite3.Error as e:
            self.logger.error(f"Error reading projects for user_id '{user_id}': {e}")
            return []
        
    def read_all_projects(self) -> list[sqlite3.Row]:
        """
        Reads all projects.
        """
        try:
            cursor = self.connection.execute(
                f"SELECT * FROM {DatabaseService.PROJECTS_TABLE_NAME}"
            )

            return cursor.fetchall()

        except sqlite3.Error as e:
            self.logger.error(f"Error reading all projects: {e}")
            return []
        
    ############
    # DOCUMENTS
    ############
    def create_document(self, user_id: int, project_id: int, document_title: str) -> bool:
        """
        Inserts a new document to a given project.
        """
        try:
            if not self.read_user(user_id=user_id):
                raise ValueError(f"User of id '{user_id}' was not found. The document was not inserted.")
            if not self.read_project(project_id=project_id):
                raise ValueError(f"Project of id '{project_id}' was not found")
            
            cursor = self.connection.execute(
                f"""
                INSERT INTO {DatabaseService.DOCUMENTS_TABLE_NAME}
                (project_id, user_id, title, created_at, modified_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """,
                (project_id, user_id, document_title)
            )
            
            self.connection.commit()
            return cursor.rowcount == 1

        except sqlite3.Error as e:
            self.connection.rollback()
            self.logger.error(f"Error creating document: {e}")
            return False

    def read_document(self, document_id: int) -> Optional[sqlite3.Row]:
        """
        Reads a single document by ID.
        """
        try:
            # 🔧 CHANGE: safe parameter usage
            cursor = self.connection.execute(
                f"""
                SELECT *
                FROM {DatabaseService.DOCUMENTS_TABLE_NAME}
                WHERE id = ?
                """,
                (document_id,)
            )

            return cursor.fetchone()

        except sqlite3.Error as e:
            self.logger.error(f"Error reading document for id {document_id}: {e}")
            return None

    def read_documents_by_project(self, project_id: int) -> list[sqlite3.Row]:
        """
        Reads all documents for a given project.
        """
        try:
            cursor = self.connection.execute(
                f"SELECT * FROM {DatabaseService.DOCUMENTS_TABLE_NAME} WHERE project_id = ?",
                (project_id,)
            )

            return cursor.fetchall()

        except sqlite3.Error as e:
            self.logger.error(f"Error reading all documents for a given project: {e}")
            return []
        
    def read_all_documents(self) -> list[sqlite3.Row]:
        """
        Reads all documents.
        """
        try:
            cursor = self.connection.execute(
                f"SELECT * FROM {DatabaseService.DOCUMENTS_TABLE_NAME}"
            )

            return cursor.fetchall()

        except sqlite3.Error as e:
            self.logger.error(f"Error reading all documents: {e}")
            return []

    ###########
    # CLEANUP
    ###########
    def close(self) -> None:
        """
        Closes the database connection.
        """
        self.connection.close()
