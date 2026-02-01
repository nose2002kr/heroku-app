import sqlite3
import os
from typing import Optional
from loguru import logger

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "users.db")


def init_db():
    """Initialize database and create tables if not exists."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL,
            username TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    logger.info("Database initialized")


def save_user(user_id: str, username: str, email: str = None) -> bool:
    """Save or update user information."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO users (user_id, username, email)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                email = excluded.email,
                updated_at = CURRENT_TIMESTAMP
        ''', (user_id, username, email))

        conn.commit()
        conn.close()
        logger.info(f"User saved: {username}")
        return True
    except Exception as e:
        logger.error(f"Failed to save user: {e}")
        return False


def get_user(user_id: str) -> Optional[dict]:
    """Get user by user_id."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT user_id, username, email, created_at, updated_at
            FROM users WHERE user_id = ?
        ''', (user_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "user_id": row[0],
                "username": row[1],
                "email": row[2],
                "created_at": row[3],
                "updated_at": row[4]
            }
        return None
    except Exception as e:
        logger.error(f"Failed to get user: {e}")
        return None


# Initialize database on module load
init_db()
