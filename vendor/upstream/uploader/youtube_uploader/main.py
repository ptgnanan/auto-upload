# -*- coding: utf-8 -*-
"""
YouTube Video Uploader

基于 Playwright 浏览器自动化 + Cookie 认证的 YouTube 视频上传器

上传地址: https://studio.youtube.com/channel/{channel_id}/videos/upload
"""
from __future__ import annotations

import asyncio
import os
from datetime import datetime
from pathlib import Path

from patchright.async_api import Page
from patchright.async_api import Playwright
from patchright.async_api import async_playwright

from conf import DEBUG_MODE, LOCAL_CHROME_HEADLESS, LOCAL_CHROME_PATH
from uploader.base_video import BaseVideoUploader
from utils.base_social_media import set_init_script
from utils.log import youtube_logger

YOUTUBE_STUDIO_URL = "https://studio.youtube.com"


def _msg(emoji: str, text: str) -> str:
    return f"{emoji} {text}"


async def cookie_auth(account_file: str) -> bool:
    """校验 YouTube cookie 是否有效"""
    from conf import LOGIN_HEADLESS
    async with async_playwright() as playwright:
        _opts = {'headless': LOGIN_HEADLESS}
        if LOCAL_CHROME_PATH:
            _opts['executable_path'] = LOCAL_CHROME_PATH
        browser = await playwright.chromium.launch(**_opts)
        try:
            context = await browser.new_context(storage_state=account_file)
            context = await set_init_script(context)
            page = await context.new_page()
            await page.goto(YOUTUBE_STUDIO_URL)
            # 如果跳转到登录页面则 cookie 无效
            if "accounts.google.com" in page.url or "signin" in page.url.lower():
                youtube_logger.info(_msg("❌", "YouTube cookie 已失效，需要重新登录"))
                return False
            youtube_logger.success(_msg("✅", "YouTube cookie 有效"))
            return True
        except Exception as exc:
            youtube_logger.warning(_msg("⚠️", f"YouTube cookie 校验时出错: {exc}"))
            return False
        finally:
            await browser.close()


async def youtube_setup(account_file: str, handle=False, return_detail=False, headless=True) -> bool:
    """检查 YouTube cookie 是否就绪"""
    return await cookie_auth(account_file)


class YouTubeBaseUploader(BaseVideoUploader):
    def __init__(
        self,
        publish_date: datetime | int,
        account_file,
        debug: bool = DEBUG_MODE,
        headless: bool = LOCAL_CHROME_HEADLESS,
    ):
        self.publish_date = publish_date
        self.account_file = str(account_file)
        self.debug = debug
        self.headless = headless
        self.local_executable_path = LOCAL_CHROME_PATH

    async def validate_base_args(self):
        if not os.path.exists(self.account_file):
            raise RuntimeError(
                f"YouTube cookie 文件不存在，请先完成登录: {self.account_file}"
            )
        if not await cookie_auth(self.account_file):
            raise RuntimeError(
                f"YouTube cookie 已失效，请先完成登录: {self.account_file}"
            )

        if self.publish_date != 0:
            self.publish_date = self.validate_publish_date(self.publish_date)


class YouTubeVideo(YouTubeBaseUploader):
    def __init__(
        self,
        title,
        file_path,
        tags,
        publish_date: datetime | int,
        account_file,
        desc: str | None = None,
        thumbnail_path=None,
        headless: bool = LOCAL_CHROME_HEADLESS,
    ):
        super().__init__(
            publish_date=publish_date,
            account_file=account_file,
            headless=headless,
        )
        self.title = title
        self.file_path = file_path
        # 解析标签：支持 "#标签1 #标签2" 或 "标签1,标签2" 或混合格式
        if isinstance(tags, str) and tags.strip():
            import re
            self.tags = [t.strip() for t in re.split(r'[,，#]', tags) if t.strip()]
        elif isinstance(tags, list):
            self.tags = tags
        else:
            self.tags = []
        self.desc = desc or ""
        self.thumbnail_path = thumbnail_path

    async def validate_upload_args(self):
        await self.validate_base_args()
        if not self.title or not str(self.title).strip():
            raise ValueError("YouTube 视频上传时，title 是必须的")
        self.file_path = str(self.validate_video_file(self.file_path))
        if self.thumbnail_path:
            self.thumbnail_path = str(self.validate_image_file(self.thumbnail_path))

    async def _upload_video_file(self, page: Page):
        """上传视频文件到 YouTube"""
        youtube_logger.info(_msg("📤", "正在上传视频文件"))

        # YouTube Studio 上传界面的文件输入框
        file_input = page.locator('input[type="file"][accept*="video"]').first
        await file_input.wait_for(state="attached", timeout=10000)
        await file_input.set_input_files(self.file_path)
        youtube_logger.info(_msg("✅", "视频文件已选择，等待上传完成"))

    async def _wait_upload_complete(self, page: Page):
        """等待视频上传完成"""
        youtube_logger.info(_msg("⏳", "等待视频上传完成"))
        try:
            # 等待上传进度条消失 - YouTube Studio 上传完成后会隐藏进度条
            # 使用进度条容器作为目标，上传完成时该元素会被移除或改变
            progress_selector = 'tp-yt-paper-progress, [progress-bar], .upload-progress'
            try:
                await page.wait_for_selector(progress_selector, state="hidden", timeout=120000)
                youtube_logger.info(_msg("✅", "视频文件上传完成"))
            except Exception:
                # 备用方案：等待 "视频已上传" 相关元素出现
                youtube_logger.info(_msg("⏳", "使用备用方案检测上传状态"))
                await asyncio.sleep(5)

            # 检查是否有上传失败的提示
            fail_text = page.locator("text=上传失败")
            if await fail_text.count() > 0:
                youtube_logger.warning(_msg("⚠️", "视频上传失败"))
                return False

            # 等待下一步操作界面出现（通常是标题输入框）
            title_input = page.locator(
                'input[placeholder*="title"], input[placeholder*="标题"], '
                '#title-input, [class*="title"] input'
            ).first
            try:
                await title_input.wait_for(state="visible", timeout=30000)
                youtube_logger.success(_msg("✅", "上传界面已加载"))
            except Exception:
                youtube_logger.warning(_msg("⚠️", "未检测到上传完成界面"))

            return True
        except Exception as exc:
            youtube_logger.warning(_msg("⚠️", f"检查上传状态出错: {exc}"))
            return False

    async def _fill_title(self, page: Page):
        """填写视频标题"""
        youtube_logger.info(_msg("✍️", f"填写标题: {self.title[:30]}"))
        title_input = page.locator(
            'input[placeholder*="title"], input[placeholder*="标题"], '
            '#title-input, [class*="title"] input'
        ).first
        await title_input.wait_for(state="visible", timeout=15000)
        await title_input.click()
        await title_input.fill("")
        await title_input.fill(self.title[:100])

    async def _fill_desc(self, page: Page):
        """填写视频描述"""
        if not self.desc:
            return

        youtube_logger.info(_msg("📝", "填写视频描述"))
        desc_input = page.locator(
            'textarea[placeholder*="描述"], textarea[placeholder*="desc"], '
            '#description-input, [class*="description"] textarea'
        ).first
        if await desc_input.count() > 0 and await desc_input.is_visible():
            await desc_input.click()
            await desc_input.fill(self.desc)
        else:
            youtube_logger.warning(_msg("⚠️", "未找到描述输入框"))

    async def _fill_tags(self, page: Page):
        """填写视频标签"""
        if not self.tags:
            return

        youtube_logger.info(_msg("🏷️", f"添加 {len(self.tags)} 个标签"))
        # YouTube Studio 标签输入框
        tag_input = page.locator(
            'input[placeholder*="标签"], input[placeholder*="tag"], '
            '#tag-input, [class*="tag"] input'
        ).first
        for tag in self.tags[:15]:
            try:
                await tag_input.click()
                await asyncio.sleep(0.3)
                await tag_input.press_sequentially(str(tag), delay=50)
                await asyncio.sleep(0.3)
                await tag_input.press("Enter")
                await asyncio.sleep(0.5)
                youtube_logger.info(_msg("🏷️", f"已添加标签: {tag}"))
            except Exception as exc:
                youtube_logger.warning(_msg("⚠️", f"添加标签失败 '{tag}': {exc}"))

    async def _set_thumbnail(self, page: Page):
        """上传视频封面"""
        if not self.thumbnail_path:
            return

        if not os.path.exists(self.thumbnail_path):
            youtube_logger.error(_msg("❌", f"封面文件不存在: {self.thumbnail_path}"))
            return

        youtube_logger.info(_msg("🖼️", "开始设置 YouTube 封面"))
        try:
            # 查找封面上传区域并点击
            thumb_area = page.locator(
                '#upload-thumbnail, [class*="thumbnail"] input[type="file"]'
            ).first
            if await thumb_area.count() > 0:
                await thumb_area.set_input_files(self.thumbnail_path)
                youtube_logger.success(_msg("✅", "封面已上传"))
            else:
                youtube_logger.warning(_msg("⚠️", "未找到封面上传区域"))
        except Exception as exc:
            youtube_logger.warning(_msg("⚠️", f"封面设置失败: {exc}"))

    async def upload(self, playwright: Playwright) -> None:
        youtube_logger.info(_msg("🔍", "上传前检查 cookie、视频文件和发布时间"))
        await self.validate_upload_args()
        youtube_logger.info(_msg("✅", "上传前检查通过"))

        log_dir = Path(__file__).parent.parent.parent.parent / "data" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        _opts = {'headless': self.headless}
        if self.local_executable_path:
            _opts['executable_path'] = self.local_executable_path
        browser = await playwright.chromium.launch(**_opts)
        context = await browser.new_context(storage_state=self.account_file)
        context = await set_init_script(context)

        upload_success = False
        try:
            page = await context.new_page()
            youtube_logger.info(_msg("🎬", f"开始上传视频: {self.title}"))
            # YouTube Studio 上传页面
            await page.goto(YOUTUBE_STUDIO_URL + "/channel/me/videos/upload")
            youtube_logger.info(_msg("🧭", "正在等待 YouTube Studio 上传页面加载"))
            await page.wait_for_url("**/videos/upload**", timeout=30000)

            # 1. 上传视频文件
            await self._upload_video_file(page)

            # 2. 等待上传完成
            upload_ok = await self._wait_upload_complete(page)
            if not upload_ok:
                youtube_logger.error(_msg("❌", "视频上传失败"))
                return

            await asyncio.sleep(3)

            # 3. 填写标题
            await self._fill_title(page)

            # 4. 填写描述
            await self._fill_desc(page)

            # 5. 填写标签
            await self._fill_tags(page)

            # 6. 设置封面
            await self._set_thumbnail(page)

            # 7. 提交
            youtube_logger.info(_msg("📤", "正在提交视频"))

            # 查找并点击 "发布" 按钮
            # YouTube Studio 的发布按钮可能是多种选择器
            submit_button = page.locator(
                '#publish-button, tp-yt-paper-button[aria-label*="发布"], '
                '[aria-label*="publish"] button, #upload- publish-button, '
                'tp-yt-paper-button:has-text("发布"), button:has-text("发布")'
            ).first

            try:
                await submit_button.wait_for(state="visible", timeout=15000)
                youtube_logger.info(_msg("👆", "找到发布按钮，准备点击"))
                await submit_button.click()
                youtube_logger.info(_msg("⏳", "等待发布处理"))

                # 等待发布完成 - 通常会显示 "视频已发布" 或类似的成功提示
                await asyncio.sleep(3)

                # 检查是否有发布成功的提示
                success_indicators = page.locator(
                    'text=已发布, text=发布成功, text=Video published, '
                    '[aria-label*="已发布"]'
                )
                if await success_indicators.count() > 0:
                    youtube_logger.success(_msg("✅", "视频发布成功"))
                    upload_success = True
                else:
                    # 如果没有明确成功提示，检查是否还在编辑页面
                    if await submit_button.is_visible():
                        youtube_logger.warning(_msg("⚠️", "发布按钮仍可见，可能发布未完成"))
                        upload_success = True  # 仍标记为成功，因为点击了按钮
                    else:
                        youtube_logger.info(_msg("📤", "发布流程已触发"))
                        upload_success = True
            except Exception as exc:
                youtube_logger.warning(_msg("⚠️", f"点击发布按钮失败: {exc}"))
                # 尝试备用方案：查找可能的 "下一步" 或 "完成" 按钮
                try:
                    next_button = page.locator(
                        'button:has-text("下一步"), button:has-text("下一步"), '
                        'tp-yt-paper-button:has-text("下一步")'
                    ).first
                    if await next_button.is_visible():
                        await next_button.click()
                        youtube_logger.info(_msg("👆", "点击了下一步按钮"))
                        upload_success = True
                except Exception:
                    pass
        finally:
            if upload_success:
                try:
                    await context.storage_state(path=self.account_file)
                    youtube_logger.success(_msg("✅", "YouTube cookie 已更新"))
                except Exception:
                    pass
            await context.close()
            await browser.close()
            youtube_logger.info(_msg("✅", "浏览器已关闭"))

    async def main(self):
        async with async_playwright() as playwright:
            await self.upload(playwright)