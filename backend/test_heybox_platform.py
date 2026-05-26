"""Regression tests for Heybox platform login helpers."""

import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = REPO_ROOT / "backend"
UPSTREAM_DIR = REPO_ROOT / "vendor" / "upstream"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(UPSTREAM_DIR) not in sys.path:
    sys.path.insert(1, str(UPSTREAM_DIR))

from impl.heybox.platform import HeyboxPlatform  # noqa: E402


class HeyboxPlatformTests(unittest.TestCase):
    def setUp(self):
        self.platform = HeyboxPlatform()

    def test_normalize_display_name_rejects_navigation_labels(self):
        self.assertEqual(self.platform._normalize_display_name("首页"), "")
        self.assertEqual(self.platform._normalize_display_name(" 创作者中心 "), "")
        self.assertEqual(self.platform._normalize_display_name("扫码快捷登录"), "")

    def test_normalize_display_name_accepts_real_nickname(self):
        self.assertEqual(self.platform._normalize_display_name("盒友小明"), "盒友小明")
        self.assertEqual(self.platform._normalize_display_name(" 玩家_A1 "), "玩家_A1")

    def test_placeholder_avatar_is_rejected(self):
        self.assertTrue(self.platform._is_placeholder_avatar(""))
        self.assertTrue(self.platform._is_placeholder_avatar(self.platform.creator_url))
        self.assertTrue(self.platform._is_placeholder_avatar(f"{self.platform.creator_url}?foo=bar"))
        self.assertFalse(self.platform._is_placeholder_avatar("https://imgheybox.max-c.com/avatar/test.png"))


if __name__ == "__main__":
    unittest.main()
