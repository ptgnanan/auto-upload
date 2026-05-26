"""Heybox platform implementation."""

import asyncio
import base64
import json
import sqlite3
import threading
import uuid
from pathlib import Path
from queue import Queue

from conf import BASE_DIR

from ..base_platform import BasePlatform


class HeyboxPlatform(BasePlatform):
    platform_id = 9
    platform_key = "heybox"
    platform_name = "小黑盒"

    creator_url = "https://www.xiaoheihe.cn/creator/editor/draft/video"

    _INVALID_DISPLAY_NAMES = {
        "登录",
        "去登录",
        "首页",
        "内容管理",
        "创作者中心",
        "发布内容",
        "发布图文",
        "发布文章",
        "发布视频",
        "问题反馈",
        "草稿箱",
        "发布",
        "验证码登录",
        "密码登录",
        "登录/注册",
        "扫码快捷登录",
        "小黑盒扫码登录",
        "填写标题",
        "正文文案",
        "关联社区",
        "添加社区",
        "关联话题",
        "添加话题",
        "发布设置",
        "权限设置",
        "所有人可见",
        "仅粉丝可见",
        "仅自己可见",
        "视频类型",
        "原创",
        "转载",
        "原创说明",
        "未经授权禁止转载或摘编",
    }

    async def login(self, id: str, status_queue: Queue) -> None:
        """Open creator center, emit QR code, then persist a verified login state."""
        from patchright.async_api import TimeoutError as PlaywrightTimeoutError
        from patchright.async_api import async_playwright

        async with async_playwright() as playwright:
            browser = await self.create_browser(playwright, login_mode=True)
            context = await self.create_context(browser)
            page = await context.new_page()
            try:
                await self._open_creator_page(page)
                await self._prepare_login_dialog(page)

                qrcode_data = await self._extract_login_qrcode(page)
                status_queue.put(qrcode_data)
                status_queue.put(
                    json.dumps(
                        {"status": "100", "msg": "请使用小黑盒 App 扫码登录"},
                        ensure_ascii=False,
                    )
                )

                user_name, avatar_url = await self._wait_for_login_profile(page, timeout_ms=240000)
                if not user_name:
                    raise RuntimeError("未获取到小黑盒创作者昵称")

                uuid_v1 = uuid.uuid1()
                cookies_dir = Path(BASE_DIR / "cookiesFile")
                cookies_dir.mkdir(parents=True, exist_ok=True)
                cookie_name = f"{uuid_v1}.json"
                await context.storage_state(path=cookies_dir / cookie_name)

                with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
                    conn.execute(
                        """
                        INSERT INTO user_info (type, filePath, userName, status, avatar)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (self.platform_id, cookie_name, user_name, 1, avatar_url),
                    )
                    conn.commit()

                status_queue.put(
                    json.dumps({"status": "200", "name": user_name, "avatar": avatar_url}, ensure_ascii=False)
                )
            except PlaywrightTimeoutError:
                status_queue.put(json.dumps({"status": "500", "msg": "小黑盒登录超时，请重试"}, ensure_ascii=False))
            except TimeoutError:
                status_queue.put(json.dumps({"status": "500", "msg": "小黑盒登录超时，请重试"}, ensure_ascii=False))
            except Exception as exc:
                status_queue.put(json.dumps({"status": "500", "msg": f"小黑盒登录失败: {exc}"}, ensure_ascii=False))
            finally:
                try:
                    await page.close()
                except Exception:
                    pass
                try:
                    await context.close()
                except Exception:
                    pass
                try:
                    await browser.close()
                except Exception:
                    pass

    async def check_cookie(self, cookie_file: str) -> bool:
        """Check whether saved Heybox login state can access creator page."""
        from patchright.async_api import async_playwright

        cookie_path = str(Path(BASE_DIR / "cookiesFile" / cookie_file))
        async with async_playwright() as playwright:
            browser = await self.create_browser(playwright, headless=True)
            context = await self.create_context(browser, storage_state=cookie_path)
            page = await context.new_page()
            try:
                await self._open_creator_page(page)
                user_name, _ = await self._wait_for_creator_profile(page, timeout_ms=10000)
                return bool(user_name)
            except Exception:
                return False
            finally:
                try:
                    await page.close()
                except Exception:
                    pass
                try:
                    await context.close()
                except Exception:
                    pass
                try:
                    await browser.close()
                except Exception:
                    pass

    async def sync_profile(self, cookie_file: str) -> tuple:
        """Sync profile from creator page when possible."""
        from patchright.async_api import async_playwright

        cookie_path = str(Path(BASE_DIR / "cookiesFile" / cookie_file))
        async with async_playwright() as playwright:
            browser = await self.create_browser(playwright, headless=True)
            context = await self.create_context(browser, storage_state=cookie_path)
            page = await context.new_page()
            try:
                await self._open_creator_page(page)
                return await self._wait_for_creator_profile(page, timeout_ms=10000)
            except Exception:
                return "", ""
            finally:
                try:
                    await page.close()
                except Exception:
                    pass
                try:
                    await context.close()
                except Exception:
                    pass
                try:
                    await browser.close()
                except Exception:
                    pass

    async def open_creator_center(self, cookie_file: str) -> None:
        """Open Heybox creator center in visible browser."""
        cookie_path = str(Path(BASE_DIR / "cookiesFile" / cookie_file))
        url = self.creator_url

        def _launch():
            from patchright.sync_api import sync_playwright
            from myUtils.browser import create_browser_sync, create_context_sync

            pw = sync_playwright().start()
            try:
                browser = create_browser_sync(pw, headless=False)
                context = create_context_sync(browser, storage_state=cookie_path)
                page = context.new_page()
                page.goto(url)
                try:
                    page.wait_for_event("close", timeout=0)
                except Exception:
                    pass
            finally:
                try:
                    browser.close()
                except Exception:
                    pass
                pw.stop()

        thread = threading.Thread(target=_launch, daemon=True)
        thread.start()

    def publish_video(self, **kwargs) -> bool:
        """Publish a single video to Heybox creator center."""
        from patchright.sync_api import TimeoutError as PlaywrightTimeoutError
        from patchright.sync_api import sync_playwright

        title = kwargs.get("title", "") or ""
        description = kwargs.get("desc", "") or ""
        files = kwargs.get("files", []) or []
        account_files = kwargs.get("account_file", []) or []

        if not files:
            raise ValueError("小黑盒发布失败: 缺少视频文件")
        if not account_files:
            raise ValueError("小黑盒发布失败: 缺少账号 Cookie")

        video_path = str(Path(BASE_DIR / "videoFile" / files[0]))
        cookie_path = str(Path(BASE_DIR / "cookiesFile" / account_files[0]))

        with sync_playwright() as playwright:
            browser = self._create_sync_browser(playwright)
            context = self._create_sync_context(browser, cookie_path)
            page = context.new_page()
            try:
                page.goto(self.creator_url, wait_until="domcontentloaded", timeout=45000)
                page.wait_for_timeout(3000)

                if not self._is_logged_in_sync(page):
                    raise ValueError("小黑盒账号未登录或登录态已失效")

                self._fill_sync_editor(page, title=title, description=description)
                self._trigger_upload(page, video_path)
                self._submit_publish(page)
                return True
            except PlaywrightTimeoutError as exc:
                raise ValueError(f"小黑盒发布超时: {exc}") from exc
            finally:
                try:
                    page.close()
                except Exception:
                    pass
                try:
                    context.close()
                except Exception:
                    pass
                try:
                    browser.close()
                except Exception:
                    pass

    async def _open_creator_page(self, page) -> None:
        await page.goto(self.creator_url, wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_timeout(3000)

    async def _prepare_login_dialog(self, page) -> None:
        await self._dismiss_login_gate(page)
        if await self._is_login_dialog_visible(page):
            return

        confirm_button = page.locator(".alert-btn-box__btn.confirm").first
        if await confirm_button.count():
            await confirm_button.click(force=True)
            await page.wait_for_timeout(1500)

        if await self._is_login_dialog_visible(page):
            return

        login_button = page.locator(".user-box__login").first
        if await login_button.count():
            await login_button.click(force=True)
            await page.wait_for_timeout(1000)

        confirm_button = page.locator(".alert-btn-box__btn.confirm").first
        if await confirm_button.count():
            await confirm_button.click(force=True)
            await page.wait_for_timeout(1500)

        await self._wait_for_login_dialog(page, timeout_ms=15000)

    async def _dismiss_login_gate(self, page) -> None:
        cancel_button = page.locator(".alert-btn-box__btn.cancel").first
        if await cancel_button.count():
            try:
                await cancel_button.click(force=True, timeout=2000)
                await page.wait_for_timeout(800)
            except Exception:
                pass

    async def _wait_for_login_dialog(self, page, timeout_ms: int = 15000) -> None:
        end_at = asyncio.get_running_loop().time() + timeout_ms / 1000
        while asyncio.get_running_loop().time() < end_at:
            if await self._is_login_dialog_visible(page):
                return
            await page.wait_for_timeout(500)
        raise RuntimeError("未打开小黑盒登录弹层")

    async def _is_login_dialog_visible(self, page) -> bool:
        markers = [
            ".right-box",
            ".right-box .qrcode-box",
            ".right-box #login-qrcode",
            ".right-box .bottom-text",
            ".login-register",
        ]
        for selector in markers:
            locator = page.locator(selector).first
            if not await locator.count():
                continue
            try:
                if await locator.is_visible():
                    return True
            except Exception:
                continue
        return False

    async def _extract_login_qrcode(self, page) -> str:
        selectors = [
            "#login-qrcode",
            ".right-box .qrcode-box canvas",
            ".qrcode-box canvas",
            ".qr-login-wrapper canvas",
            ".right-box .qrcode-box img",
            ".right-box img",
        ]
        for selector in selectors:
            locator = page.locator(selector).first
            if not await locator.count():
                continue
            try:
                await locator.wait_for(state="visible", timeout=15000)
            except Exception:
                continue
            data_url = await self._locator_to_data_url(locator)
            if data_url:
                return data_url
        raise RuntimeError("未获取到小黑盒登录二维码")

    async def _locator_to_data_url(self, locator) -> str:
        try:
            tag_name = await locator.evaluate("el => el.tagName.toLowerCase()")
        except Exception:
            tag_name = ""

        if tag_name == "canvas":
            try:
                data_url = await locator.evaluate(
                    """
                    canvas => {
                      if (!(canvas instanceof HTMLCanvasElement)) return '';
                      try {
                        return canvas.toDataURL('image/png');
                      } catch (error) {
                        return '';
                      }
                    }
                    """
                )
            except Exception:
                data_url = ""
            if data_url and data_url.startswith("data:image"):
                return data_url

        if tag_name == "img":
            try:
                src = await locator.get_attribute("src")
            except Exception:
                src = ""
            if src and src.startswith("data:image"):
                return src

        try:
            image_bytes = await locator.screenshot(type="png")
        except Exception:
            image_bytes = b""

        if image_bytes:
            encoded = base64.b64encode(image_bytes).decode("ascii")
            return f"data:image/png;base64,{encoded}"
        return ""

    async def _wait_for_login_profile(self, page, timeout_ms: int = 240000) -> tuple[str, str]:
        profile = await self._wait_for_creator_profile(page, timeout_ms=timeout_ms)
        if profile[0]:
            return profile
        raise TimeoutError("manual login timeout")

    async def _wait_for_creator_profile(self, page, timeout_ms: int = 10000) -> tuple[str, str]:
        end_at = asyncio.get_running_loop().time() + timeout_ms / 1000
        while asyncio.get_running_loop().time() < end_at:
            profile = await self._scrape_profile(page)
            if profile[0]:
                return profile
            await page.wait_for_timeout(1200)
        return "", ""

    async def _scrape_profile(self, page) -> tuple[str, str]:
        selectors = [
            ".view-header__user-box .user-box__username",
            ".user-box__username",
            ".view-header__right .user-box__username",
            ".view-header__user-box p",
            ".view-header__right [class*='user-box'] p",
            ".view-header__right p",
        ]
        for selector in selectors:
            text = await self._read_first_text(page, selector)
            name = self._normalize_display_name(text)
            if not name:
                continue
            return name, await self._extract_avatar(page)
        return "", ""

    async def _extract_avatar(self, page) -> str:
        selectors = [
            "#view-header__avatar img",
            "#view-header__avatar .hb-avatar__image",
            ".view-header__user-box .user-box__avatar img",
            ".user-box__avatar img",
            ".view-header__right .hb-avatar__image",
            ".view-header__user-box img",
        ]
        for selector in selectors:
            locator = page.locator(selector).first
            if not await locator.count():
                continue
            try:
                src = (await locator.get_attribute("src") or "").strip()
            except Exception:
                continue
            if src and not self._is_placeholder_avatar(src):
                return src
        return ""

    async def _read_first_text(self, page, selector: str) -> str:
        locator = page.locator(selector).first
        if not await locator.count():
            return ""
        try:
            text = await locator.inner_text()
        except Exception:
            return ""
        return " ".join((text or "").split())

    def _normalize_display_name(self, value: str) -> str:
        normalized = " ".join((value or "").split())
        if not normalized or len(normalized) > 40:
            return ""
        if normalized in self._INVALID_DISPLAY_NAMES:
            return ""
        blocked_tokens = ("扫码登录", "验证码登录", "密码登录", "登录/注册")
        if any(token in normalized for token in blocked_tokens):
            return ""
        return normalized

    def _is_placeholder_avatar(self, src: str) -> bool:
        value = (src or "").strip()
        if not value:
            return True
        return value == self.creator_url or value.startswith(self.creator_url)

    def _create_sync_browser(self, playwright):
        from myUtils.browser import create_browser_sync

        return create_browser_sync(playwright, headless=False)

    def _create_sync_context(self, browser, cookie_path: str):
        from myUtils.browser import create_context_sync

        return create_context_sync(browser, storage_state=cookie_path)

    def _is_logged_in_sync(self, page) -> bool:
        user_name, _ = self._scrape_profile_sync(page)
        return bool(user_name)

    def _scrape_profile_sync(self, page) -> tuple[str, str]:
        selectors = [
            ".view-header__user-box .user-box__username",
            ".user-box__username",
            ".view-header__right .user-box__username",
            ".view-header__user-box p",
            ".view-header__right [class*='user-box'] p",
            ".view-header__right p",
        ]
        for selector in selectors:
            text = self._read_first_text_sync(page, selector)
            name = self._normalize_display_name(text)
            if not name:
                continue
            return name, self._extract_avatar_sync(page)
        return "", ""

    def _extract_avatar_sync(self, page) -> str:
        selectors = [
            "#view-header__avatar img",
            "#view-header__avatar .hb-avatar__image",
            ".view-header__user-box .user-box__avatar img",
            ".user-box__avatar img",
            ".view-header__right .hb-avatar__image",
            ".view-header__user-box img",
        ]
        for selector in selectors:
            locator = page.locator(selector).first
            if not locator.count():
                continue
            try:
                src = (locator.get_attribute("src") or "").strip()
            except Exception:
                continue
            if src and not self._is_placeholder_avatar(src):
                return src
        return ""

    def _read_first_text_sync(self, page, selector: str) -> str:
        locator = page.locator(selector).first
        if not locator.count():
            return ""
        try:
            text = locator.inner_text()
        except Exception:
            return ""
        return " ".join((text or "").split())

    def _fill_sync_editor(self, page, title: str, description: str) -> None:
        editors = page.locator(".ProseMirror.hb-editor")
        if editors.count() < 2:
            raise ValueError("小黑盒发布失败: 未找到标题或正文输入框")

        title_editor = editors.nth(0)
        content_editor = editors.nth(1)

        title_editor.click(force=True)
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        if title:
            title_editor.type(title[:30], delay=20)

        content_editor.click(force=True)
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        if description:
            content_editor.type(description, delay=12)

    def _trigger_upload(self, page, video_path: str) -> None:
        with page.expect_file_chooser(timeout=10000) as chooser_info:
            page.locator(".video-uploader__unload").click(force=True)
        chooser_info.value.set_files(video_path)
        page.wait_for_timeout(5000)

    def _submit_publish(self, page) -> None:
        publish_button = page.locator(".editor-publish__btn.main-btn")
        if not publish_button.count():
            raise ValueError("小黑盒发布失败: 未找到发布按钮")

        publish_button.click(force=True)
        page.wait_for_timeout(4000)

        body_text = page.locator("body").inner_text()
        if "去登录" in body_text or "验证码登录" in body_text:
            raise ValueError("小黑盒发布失败: 发布时仍处于未登录状态")
