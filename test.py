import unittest
import socket
import threading
import sys
from unittest.mock import Mock, patch
from server import DataStore, Server

class TestDataStore(unittest.TestCase):
    def setUp(self):
        self.data_store = DataStore()

    def test_put_and_get(self):
        self.data_store.put("X", "10", "thread1")
        self.assertEqual(self.data_store.get("X", "thread1"), "10")

    def test_delete(self):
        self.data_store.put("X", "10", "thread1")
        self.assertEqual(self.data_store.delete("X", "10"), "SUCCESS")
        self.assertIsNone(self.data_store.get("X", "thread1"))

    def test_delete_nonexistent_key(self):
        result = self.data_store.delete("Y", "thread1")
        self.assertEqual(result, "ERROR")

    def test_transaction_rollback(self):
        self.data_store.start("thread1")
        self.data_store.put("X", "10", "thread1")
        self.data_store.rollback("thread1")
        self.assertIsNone(self.data_store.get("X", "thread1"))

    def test_rollback_child_trasactions(self):
        self.data_store.start("thread1")
        self.data_store.put("X", "10", "thread1")
        self.data_store.start("thread2")
        self.data_store.put("X", "20", "thread2")
        self.data_store.rollback("thread2")
        self.assertEqual(self.data_store.get("X", "thread1"), "10")

    def test_transaction_commit(self):
        self.data_store.start("thread1")
        self.data_store.put("X", "10", "thread1")
        self.data_store.commit("thread1")
        self.assertEqual(self.data_store.get("X","thread1"), "10")

    def test_invalid_transaction_commit(self):
        result = self.data_store.commit("nonexistent_thread")
        self.assertEqual(result["status"], "Error")

if __name__ == '__main__':
    unittest.main()