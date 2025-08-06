import os
import logging
import traceback

from typing import Optional
from base_api import BaseCore
from functools import cached_property
from base_api.base import setup_logger
from base_api.modules.config import RuntimeConfig
from base_api.modules.progress_bars import Callback

try:
    from modules.consts import *

except (ModuleNotFoundError, ImportError):
    from .modules.consts import *


class Video:
    def __init__(self, url: str, core: Optional[BaseCore] = None) -> None:
        self.url = url
        self.core = core
        core.enable_logging(level=logging.DEBUG)
        self.logger = setup_logger(name="MISSAV API - [Video]", log_file=None, level=logging.CRITICAL)
        self.content = self.core.fetch(url)

    def enable_logging(self, level, log_file: str = None):
        self.logger = setup_logger(name="MISSAV API - [Video]", log_file=log_file, level=level)

    @cached_property
    def title(self) -> str:
        """Returns the title of the video. Language depends on the URL language"""
        return regex_title.search(self.content).group(1)

    @cached_property
    def video_code(self) -> str:
        """Returns the specific video code"""
        return regex_video_code.search(self.content).group(1)

    @cached_property
    def publish_date(self) -> str:
        """Returns the publication date of the video"""
        return regex_publish_date.search(self.content).group(1)

    @cached_property
    def m3u8_base_url(self) -> str:
        """Returns the m3u8 base URL (master playlist)"""
        javascript_content = regex_m3u8_js.search(self.content).group(1)
        url_parts = javascript_content.split("|")[::-1]
        self.logger.debug(f"Constructing HLS URL from: {url_parts}")
        url = f"{url_parts[1]}://{url_parts[2]}.{url_parts[3]}/{url_parts[4]}-{url_parts[5]}-{url_parts[6]}-{url_parts[7]}-{url_parts[8]}/playlist.m3u8"
        self.logger.debug(f"Final URL: {url}")
        return url

    @cached_property
    def thumbnail(self) -> str:
        """Returns the main video thumbnail"""
        return f"{regex_thumbnail.search(self.content).group(1)}cover-n.jpg"

    def get_segments(self, quality: str) -> list:
        """Returns the list of HLS segments for a given quality"""
        return self.core.get_segments(quality=quality, m3u8_url_master=self.m3u8_base_url)

    def download(self, quality: str, downloader: str, path: str = "./", no_title=False,
                 callback=Callback.text_progress_bar,
                 remux: bool = False, remux_callback = None) -> bool:
        """Downloads the video from HLS"""
        if no_title is False:
            path = os.path.join(path, self.core.truncate(self.core.strip_title(self.title)) + ".mp4")

        try:
            self.core.download(video=self, quality=quality, path=path, callback=callback, downloader=downloader,
                               remux=remux, callback_remux=remux_callback)
            return True

        except Exception:
            error = traceback.format_exc()
            self.logger.error(error)
            return False


class Client:
    def __init__(self, core: Optional[BaseCore] = None):
        self.core = core or BaseCore(config=RuntimeConfig())
        self.core.initialize_session(headers)

    def get_video(self, url: str) -> Video:
        """Returns the video object"""
        return Video(url, core=self.core)
