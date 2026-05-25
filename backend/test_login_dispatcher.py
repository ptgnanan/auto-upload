"""Regression tests for login dispatcher behavior."""

import sys
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
import sau_backend  # noqa: E402


class _FakePlatform:
    async def login(self, account_id, status_queue):
        status_queue.put("data:image/png;base64,test")


class LoginDispatcherTests(unittest.TestCase):
    def setUp(self):
        backend_app_module.app.testing = True
        self.client = backend_app_module.app.test_client()

    def test_login_route_survives_broken_stdout(self):
        """The login route should not 500 if debug output cannot be written."""

        with patch.object(backend_app_module, "get_engine_mode", return_value="new"), \
             patch.object(backend_app_module, "get_platform", return_value=_FakePlatform()), \
             patch.object(sau_backend, "sse_stream", return_value=iter(["data: ok\n\n"])), \
             patch.object(backend_app_module, "print", side_effect=BrokenPipeError("stdout closed")):
            response = self.client.get("/login?type=5&id=test-account")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.headers.get("Content-Type", "").startswith("text/event-stream"))


if __name__ == "__main__":
    unittest.main()
