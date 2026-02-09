import sqlite3
from passlib.context import CryptContext
from typing import Optional, Dict
from datetime import datetime, timedelta
from jose import JWTError, jwt

class AuthService:    
    def __init__(self, db_path: str, secret_key: str, algorithm: str = "HS256", token_expire_min: int = 30):
        self.db_path = db_path
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.token_expire_min = token_expire_min
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self._init_db()
        
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    modified_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )             
            """)
            
    def _get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def register_user(self, first_name: str, last_name: str, email: str, password: str) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO users (first_name, last_name, email, password_hash)
                    VALUES (?, ?, ?)
                    """,
                    (first_name, last_name, email, self._get_password_hash(password))
                )
            return True
        except sqlite3.IntegrityError:
            return False
        
    def login_user(self, email: str, password: str) -> Optional[dict]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password_hash from users WHERE email = ?", (email, ))
            record = cursor.fetchone()
    
        if not record or not self._verify_password(password, record[0]):
            return None
        
        expire = datetime.utcnow() + timedelta(minutes=self.token_expire_min)
        to_encode = {"sub": email, "exp": expire}
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        return {"access_token": encoded_jwt, "token_type": "bearer"}
    
    def validate_token(self, token: str) -> Optional[str]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload.get("sub")
        except JWTError:
            return None
        