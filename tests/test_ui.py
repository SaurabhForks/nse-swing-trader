"""
Unit Tests for Swing UI & Server Handler.
"""

import unittest
import json
from unittest.mock import patch, MagicMock
from io import BytesIO
from swing_ui.server import SwingServerHandler


class DummyRequest:
    def __init__(self, data=b""):
        self._data = data

    def makefile(self, *args, **kwargs):
        return BytesIO(self._data)


class TestSwingServer(unittest.TestCase):

    def test_routes_exist(self):
        # Verify static index.html exists
        import os
        from swing_ui.server import STATIC_DIR
        index_file = os.path.join(STATIC_DIR, "index.html")
        self.assertTrue(os.path.exists(index_file))


if __name__ == "__main__":
    unittest.main()
