# create_db.py
import sqlite3
from passlib.hash import argon2
import getpass
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'users.db')

def create_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    conn.close()

def add_user(username, password):
    pw_hash = argon2.hash(password)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, pw_hash))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_db()
    print("Database created/verified at:", DB_PATH)
    username = input("Enter username to create: ").strip()
    password = getpass.getpass("Enter password for {}: ".format(username)).strip()
    add_user(username, password)
    print("User created:", username)