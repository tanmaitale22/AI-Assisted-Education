import sqlite3


class HierarchyStore:

    def __init__(self, db_path="student_memory.db"):
        self.db_path = db_path
        self.create_tables()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def create_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hierarchy_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                title TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hierarchy_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                FOREIGN KEY (document_id)
                REFERENCES hierarchy_documents(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hierarchy_subtopics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                FOREIGN KEY (topic_id)
                REFERENCES hierarchy_topics(id)
            )
        """)

        # NEW: stores RAG chunks inside the hierarchy
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hierarchy_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER NOT NULL,
                topic_id INTEGER,
                subtopic_id INTEGER,
                chunk_index INTEGER NOT NULL,
                content TEXT NOT NULL,
                FOREIGN KEY (document_id)
                REFERENCES hierarchy_documents(id),
                FOREIGN KEY (topic_id)
                REFERENCES hierarchy_topics(id),
                FOREIGN KEY (subtopic_id)
                REFERENCES hierarchy_subtopics(id)
            )
        """)

        conn.commit()
        conn.close()

    def save_hierarchy(self, filename, title, topics, chunks=None):

        conn = self.get_connection()
        cursor = conn.cursor()

        # --------------------------------
        # Check if document already exists
        # --------------------------------

        cursor.execute("""
            SELECT id
            FROM hierarchy_documents
            WHERE filename = ?
        """, (filename,))

        existing_document = cursor.fetchone()

        if existing_document:
            conn.close()
            return existing_document[0]

        # --------------------------------
        # Save new document
        # --------------------------------

        cursor.execute("""
            INSERT INTO hierarchy_documents
            (filename, title)
            VALUES (?, ?)
        """, (filename, title))

        document_id = cursor.lastrowid

        # --------------------------------
        # Helper for matching names
        # --------------------------------

        def normalize_name(name):
            return " ".join(name.strip().lower().split())

        # --------------------------------
        # Save topics and subtopics
        # --------------------------------

        topic_ids = {}
        subtopic_ids = {}


        for topic in topics:

            topic_name = topic["name"]

            cursor.execute("""
                INSERT INTO hierarchy_topics
                (document_id, name)
                VALUES (?, ?)
            """, (
                document_id,
                topic_name
            ))

            topic_id = cursor.lastrowid

            topic_ids[normalize_name(topic["name"])] = topic_id

            for subtopic in topic.get("subtopics", []):

                cursor.execute("""
                    INSERT INTO hierarchy_subtopics
                    (topic_id, name)
                    VALUES (?, ?)
                """, (
                    topic_id,
                    subtopic
                ))

                subtopic_id = cursor.lastrowid

                subtopic_ids[
                    (
                        normalize_name(topic["name"]),
                        normalize_name(subtopic)
                    )
                ] = subtopic_id

        # --------------------------------
        # Save chunks
        # --------------------------------

        if chunks:

            for chunk in chunks:

                topic_name = chunk.get("topic")
                subtopic_name = chunk.get("subtopic")

                normalized_topic = normalize_name(topic_name)
                normalized_subtopic = normalize_name(subtopic_name)

                topic_id = topic_ids.get(normalized_topic)

                subtopic_id = subtopic_ids.get(
                    (
                        normalized_topic,
                        normalized_subtopic
                    )
                )

                cursor.execute("""
                    INSERT INTO hierarchy_chunks
                    (
                        document_id,
                        topic_id,
                        subtopic_id,
                        chunk_index,
                        content
                    )
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    document_id,
                    topic_id,
                    subtopic_id,
                    chunk["index"],
                    chunk["content"]
                ))

        conn.commit()
        conn.close()

        return document_id

    def get_hierarchy(self):

        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, filename, title
            FROM hierarchy_documents
        """)

        documents = cursor.fetchall()

        result = []

        for document in documents:

            document_id = document[0]

            cursor.execute("""
                SELECT id, name
                FROM hierarchy_topics
                WHERE document_id = ?
            """, (document_id,))

            topics = cursor.fetchall()

            topic_list = []

            for topic in topics:

                topic_id = topic[0]

                cursor.execute("""
                    SELECT id, name
                    FROM hierarchy_subtopics
                    WHERE topic_id = ?
                """, (topic_id,))

                subtopics = cursor.fetchall()

                subtopic_list = []

                for subtopic in subtopics:

                    subtopic_id = subtopic[0]

                    cursor.execute("""
                        SELECT id, chunk_index, content
                        FROM hierarchy_chunks
                        WHERE subtopic_id = ?
                    """, (subtopic_id,))

                    chunks = cursor.fetchall()

                    subtopic_list.append({
                        "id": subtopic_id,
                        "name": subtopic[1],
                        "chunks": [
                            {
                                "id": chunk[0],
                                "index": chunk[1],
                                "content": chunk[2]
                            }
                            for chunk in chunks
                        ]
                    })

                topic_list.append({
                    "id": topic_id,
                    "name": topic[1],
                    "subtopics": subtopic_list
                })

            result.append({
                "id": document_id,
                "filename": document[1],
                "title": document[2],
                "topics": topic_list
            })

        conn.close()

        return result