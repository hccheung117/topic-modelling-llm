import os
import unittest
import numpy as np
from embeddingio import EmbeddingStore

TEST_DB_PATH = "data/tmp/test_embeddings.db"


class TestEmbeddingStore(unittest.TestCase):
    def setUp(self):
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)
        self.store = EmbeddingStore(TEST_DB_PATH)

    def tearDown(self):
        self.store.close()
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)

    def test_add_and_get_embeddings(self):
        data = [
            ("apple", np.array([1.0, 2.0, 3.0], dtype=np.float32)),
            ("banana", np.array([4.0, 5.0, 6.0], dtype=np.float32)),
        ]
        self.store.add_embeddings(data)
        result = self.store.get_embeddings(["apple", "banana"])
        self.assertIn("apple", result)
        self.assertIn("banana", result)
        np.testing.assert_array_equal(result["apple"], data[0][1])
        np.testing.assert_array_equal(result["banana"], data[1][1])

    def test_get_embeddings_empty(self):
        result = self.store.get_embeddings([])
        self.assertEqual(result, {})

    def test_add_embeddings_empty(self):
        self.store.add_embeddings([])  # Should not raise
        result = self.store.get_embeddings(["nothing"])
        self.assertEqual(result, {})

    def test_add_invalid_embedding_type(self):
        with self.assertRaises(ValueError):
            self.store.add_embeddings([("bad", [1.0, 2.0, 3.0])])  # Not a np.ndarray

    def test_add_invalid_embedding_dtype(self):
        with self.assertRaises(ValueError):
            self.store.add_embeddings(
                [("bad", np.array([1, 2, 3], dtype=np.int32))]  # Wrong dtype
            )

    def test_insert_duplicate_keyword(self):
        data = [
            ("apple", np.array([1.0, 2.0, 3.0], dtype=np.float32)),
        ]
        self.store.add_embeddings(data)
        # Try to insert duplicate
        self.store.add_embeddings(data)
        result = self.store.get_embeddings(["apple"])
        self.assertIn("apple", result)
        np.testing.assert_array_equal(result["apple"], data[0][1])


if __name__ == "__main__":
    unittest.main()
