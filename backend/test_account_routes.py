"""Regression tests for account list routes."""

import json
import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = REPO_ROOT / "backend"
UPSTREAM_DIR = REPO_ROOT / "vendor" / "upstream"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(UPSTREAM_DIR) not in sys.path:
    sys.path.insert(1, str(UPSTREAM_DIR))

import app as backend_app_module  # noqa: E402


class _AlwaysValidPlatform:
    async def check_cookie(self, file_path):
        return True


class AccountRouteTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.db_dir = Path(self.temp_dir.name) / "db"
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.db_dir / "database.db"

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE user_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type INTEGER NOT NULL,
                    filePath TEXT NOT NULL,
                    userName TEXT NOT NULL,
                    status INTEGER DEFAULT 0,
                    avatar TEXT DEFAULT ''
                )
                """
            )
            conn.execute(
                """
                INSERT INTO user_info (type, filePath, userName, status, avatar)
                VALUES (?, ?, ?, ?, ?)
                """,
                (5, "bili-cookie.json", "Bili User", 1, "https://example.com/avatar.png"),
            )
            conn.commit()

        self.db_path_patch = patch.object(backend_app_module, "DB_PATH", self.db_path)
        self.db_path_patch.start()
        self.addCleanup(self.db_path_patch.stop)

        backend_app_module.app.testing = True
        self.client = backend_app_module.app.test_client()

    def test_get_accounts_returns_object_rows(self):
        """Refreshing accounts should return structured rows, not positional arrays."""

        response = self.client.get("/getAccounts")

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["code"], 200)
        self.assertEqual(
            payload["data"],
            [
                {
                    "id": 1,
                    "type": 5,
                    "filePath": "bili-cookie.json",
                    "userName": "Bili User",
                    "status": 1,
                    "avatar": "https://example.com/avatar.png",
                }
            ],
        )

    def test_get_valid_accounts_keeps_structured_rows(self):
        """Validated account fetch should keep the same structured payload shape."""

        with patch.object(backend_app_module, "get_engine_mode", return_value="new"), patch.object(
            backend_app_module, "get_platform", return_value=_AlwaysValidPlatform()
        ):
            response = self.client.get("/getValidAccounts")

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["code"], 200)
        self.assertEqual(payload["data"][0]["userName"], "Bili User")
        self.assertEqual(payload["data"][0]["status"], 1)


if __name__ == "__main__":
    unittest.main()
