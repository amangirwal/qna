import sqlite3
import os

DB_PATH = "qna.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            media TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            FOREIGN KEY (question_id) REFERENCES questions (id)
        )
    """)
    conn.commit()
    conn.close()

def add_question(text, media=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO questions (text, media) VALUES (?, ?)", (text, media))
    conn.commit()
    conn.close()

def get_questions():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": row[0], "text": row[1], "media": row[2]} for row in rows]

def add_answer(question_id, text):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO answers (question_id, text) VALUES (?, ?)", (question_id, text))
    conn.commit()
    conn.close()

def get_answers(question_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM answers WHERE question_id = ?", (question_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"id": row[0], "question_id": row[1], "text": row[2]} for row in rows]
