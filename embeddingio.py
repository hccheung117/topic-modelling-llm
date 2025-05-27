import sqlite3
from typing import List, Dict, Tuple

import numpy as np


class EmbeddingStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._connect_and_initialize()

    def _connect_and_initialize(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._initialize_table()

    def _initialize_table(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS keyword_embeddings
            (
                keyword
                TEXT
                PRIMARY
                KEY,
                embedding
                BLOB
            )
            """
        )
        self.conn.commit()

    def get_embeddings(self, keywords: List[str]) -> Dict[str, np.ndarray]:
        if not keywords:
            return {}

        placeholders = ",".join(["?"] * len(keywords))
        self.cursor.execute(
            f"SELECT keyword, embedding FROM keyword_embeddings WHERE keyword IN ({placeholders})",
            keywords,
        )

        found_embeddings = {}
        for keyword, embedding_blob in self.cursor.fetchall():
            arr = np.frombuffer(embedding_blob, dtype=np.float32)
            arr = np.array(arr, dtype=np.float32)
            found_embeddings[keyword] = arr
        return found_embeddings

    def add_embeddings(self, new_embeddings_data: List[Tuple[str, np.ndarray]]):
        if not new_embeddings_data:
            return

        data_to_insert_db = []
        for keyword, embedding_vector in new_embeddings_data:
            if (
                not isinstance(embedding_vector, np.ndarray)
                or embedding_vector.dtype != np.float32
            ):
                raise ValueError(
                    f"Embedding for '{keyword}' must be a np.ndarray of dtype np.float32, got {type(embedding_vector)} with dtype {getattr(embedding_vector, 'dtype', None)}"
                )

            embedding_bytes = embedding_vector.tobytes()
            data_to_insert_db.append((keyword, embedding_bytes))

        self.cursor.executemany(
            "INSERT OR IGNORE INTO keyword_embeddings (keyword, embedding) VALUES (?, ?)",
            data_to_insert_db,
        )
        self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None  # Help with GC and prevent reuse of closed connection
            self.cursor = None

    def __enter__(self):
        # __init__ already connects and initializes
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
