import sqlite3
import bcrypt
from pathlib import Path
import streamlit as st
from datetime import datetime

DB_PATH = Path(__file__).parent / 'users.db'


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT,
            is_active INTEGER DEFAULT 1,
            is_admin INTEGER DEFAULT 0,
            created_at TEXT
        )"""
    )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT,
            ts TEXT
        )"""
    )
    conn.commit()
    conn.close()


def create_user(username: str, email: str, password: str, is_admin: bool = False):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (username, email, password, is_admin, created_at) VALUES (?, ?, ?, ?, ?)",
        (username, email, hashed, int(is_admin), datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def authenticate(username: str, password: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, password, is_admin, is_active FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    conn.close()
    if row and row[3]:
        user_id, hashed, is_admin, _ = row
        if bcrypt.checkpw(password.encode(), hashed.encode()):
            return {"id": user_id, "username": username, "is_admin": bool(is_admin)}
    return None


def get_user(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, username, email, is_admin, is_active, created_at FROM users WHERE id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        keys = ["id", "username", "email", "is_admin", "is_active", "created_at"]
        return dict(zip(keys, row))
    return None


def update_user(user_id: int, **fields):
    if not fields:
        return
    keys = []
    vals = []
    for k, v in fields.items():
        keys.append(f"{k}=?")
        vals.append(v)
    vals.append(user_id)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(f"UPDATE users SET {', '.join(keys)} WHERE id=?", tuple(vals))
    conn.commit()
    conn.close()


def list_users(search: str = ""):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if search:
        cur.execute("SELECT id, username, email, is_active, is_admin FROM users WHERE username LIKE ? OR email LIKE ?", (f"%{search}%", f"%{search}%"))
    else:
        cur.execute("SELECT id, username, email, is_active, is_admin FROM users")
    rows = cur.fetchall()
    conn.close()
    return rows


def log_message(user_id: int, message: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO logs (user_id, message, ts) VALUES (?, ?, ?)", (user_id, message, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()


def count_logs():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM logs")
    total = cur.fetchone()[0]
    conn.close()
    return total


def require_login(admin: bool = False):
    if "user" not in st.session_state:
        st.session_state["user"] = None
    user = st.session_state["user"]
    if not user:
        login_form(admin)
        st.stop()
    if admin and not user.get("is_admin"):
        st.error("Admins only")
        st.stop()


def login_form(admin: bool = False):
    st.header("Admin Login" if admin else "Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = authenticate(username, password)
        if user:
            st.session_state["user"] = user
            st.experimental_rerun()
        else:
            st.error("Invalid credentials or inactive account")

    if not admin:
        with st.expander("Register"):
            r_user = st.text_input("New username", key="reg_user")
            r_email = st.text_input("Email", key="reg_email")
            r_pwd = st.text_input("Password", type="password", key="reg_pwd")
            if st.button("Create Account"):
                try:
                    create_user(r_user, r_email, r_pwd)
                    st.success("Account created. Please log in.")
                except sqlite3.IntegrityError:
                    st.error("Username or email already exists")

    st.stop()


def logout_button():
    if st.sidebar.button("Logout"):
        st.session_state["user"] = None
        st.experimental_rerun()
