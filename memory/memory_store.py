import sqlite3
from datetime import datetime


class MemoryStore:

    def __init__(self, db_path="student_memory.db"):
        self.db_path = db_path
        self.create_table()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def create_table(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                document TEXT,
                topic TEXT,
                subtopic TEXT,
                timestamp TEXT NOT NULL
            )
        """)

        conn.commit()
        conn.close()

    def save_interaction(
        self,
        question,
        answer,
        document,
        topic,
        subtopic
    ):

        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO interactions
            (question, answer, document, topic, subtopic, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            question,
            answer,
            document,
            topic,
            subtopic,
            datetime.now().isoformat()
        ))

        conn.commit()
        conn.close()

    def get_all_interactions(self):

        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id,
                question,
                answer,
                document,
                topic,
                subtopic,
                timestamp
            FROM interactions
            ORDER BY id ASC
        """)

        interactions = cursor.fetchall()

        conn.close()

        return interactions