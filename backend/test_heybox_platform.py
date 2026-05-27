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
        cache = getattr(self.platform, "_EDITOR_SEARCH_CACHE", None)
        if isinstance(cache, dict):
            cache.clear()

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
        self.assertTrue(
            self.platform._is_placeholder_avatar(f"{self.platform.creator_url}?foo=bar")
        )
        self.assertFalse(
            self.platform._is_placeholder_avatar(
                "https://imgheybox.max-c.com/avatar/test.png"
            )
        )

    def test_editor_search_cache_normalizes_keyword(self):
        expected = [{"name": "艾尔登法环", "desc": "动作游戏"}]

        self.platform._set_editor_search_cache(
            "cookie.json", "community", "  法环  ", expected
        )

        self.assertEqual(
            self.platform._get_editor_search_cache("cookie.json", "community", "法环"),
            expected,
        )
        self.assertEqual(
            self.platform._get_editor_search_cache(
                "cookie.json", "community", "  法环  "
            ),
            expected,
        )

    def test_editor_search_cache_returns_copy(self):
        cached = [{"name": "怪物猎人", "desc": "共斗"}]

        self.platform._set_editor_search_cache("cookie.json", "topic", "mh", cached)
        result = self.platform._get_editor_search_cache("cookie.json", "topic", "mh")
        result.append({"name": "额外话题"})

        self.assertEqual(
            self.platform._get_editor_search_cache("cookie.json", "topic", "mh"),
            cached,
        )

    def test_editor_search_cache_expired_entry_is_ignored(self):
        expected = [{"name": "射击游戏"}]
        cache_key = self.platform._get_editor_search_cache_key(
            "cookie.json", "community", "fps"
        )
        self.platform._EDITOR_SEARCH_CACHE[cache_key] = {
            "expires_at": 0,
            "items": expected,
        }

        self.assertIsNone(
            self.platform._get_editor_search_cache("cookie.json", "community", "fps")
        )
        self.assertNotIn(cache_key, self.platform._EDITOR_SEARCH_CACHE)


if __name__ == "__main__":
    unittest.main()
