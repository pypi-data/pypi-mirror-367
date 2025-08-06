import json
import html
import os.path
import logging

from bs4 import BeautifulSoup
from typing import Literal, Optional
from functools import cached_property
from base_api.base import BaseCore, setup_logger
from base_api.modules.errors import ResourceGone
from base_api.modules.config import RuntimeConfig
from base_api.modules.progress_bars import Callback

try:
    from modules.consts import *
    from modules.errors import *

except (ImportError, ModuleNotFoundError):
    from .modules.consts import *
    from .modules.errors import *


class Video:
    def __init__(self, url, core: Optional[BaseCore]):
        self.core = core
        self.url = url  # Needed for Porn Fetch
        self.html_content = self.core.fetch(url)
        if '<div class="warning_process">' in self.html_content:
            raise VideoIsProcessing

        self.logger = setup_logger(name="SPANKBANG API - [Video]", log_file=None, level=logging.ERROR)
        self.soup = BeautifulSoup(self.html_content, features="html.parser")
        self.extract_script_2()
        self.extract_script_1()

    def enable_logging(self, log_file: str = None, level=None, log_ip: str = None, log_port: int = None):
        self.logger = setup_logger(name="SPANKBANG API - [Video]", log_file=log_file, level=level, http_ip=log_ip,
                                   http_port=log_port)

    def extract_script_1(self):
        """This extracts the script with the basic video information"""
        self.logger.debug("Trying to extract the first script...")
        script_tag = self.soup.find_all('script', {"type": "application/ld+json"})
        self.logger.debug("Successfully extracted the first script!")

        for script in script_tag:
            if "thumbnailUrl" in script.text:
                self.logger.debug("Script is valid!")
                text = html.unescape(script.text)
                text = text.replace("\t", " ")
                self.json_tags = json.loads(html.unescape(text))
                return

        self.logger.error("Couldn't find 'thumbnailUrl' in the script!, script is probably invalid, please report this!")
        raise "No script was found, please report this immediately with the URL you used"

    def extract_script_2(self):
        """This extracts the script with the m3u8 URLs which contain the segments used for downloading"""
        self.logger.debug("Trying to extract the second script...")
        main_container = self.soup.find('main', class_='main-container')
        script_tag = main_container.find('script', {'type': 'text/javascript'})
        self.stream_data_js = re.search(r'var stream_data = ({.*?});', script_tag.text.replace("\t", " "), re.DOTALL).group(1)
        m3u8_pattern = re.compile(r"'m3u8': \['(https://[^']+master.m3u8[^']*)'\]")
        resolution_pattern = re.compile(r"'(240p|320p|480p|720p|1080p|4k)': \['(https://[^']+.mp4[^']*)'\]")

        # Extract m3u8 master URL
        m3u8_match = m3u8_pattern.search(self.stream_data_js)
        m3u8_url = m3u8_match.group(1) if m3u8_match else None

        # Extract resolution URLs
        resolution_matches = resolution_pattern.findall(self.stream_data_js)
        resolution_urls = [url for res, url in resolution_matches]
        self.logger.info("Found m3u8 and resolution information!")
        # Combine the URLs with m3u8 first
        self.urls_list = [m3u8_url] + resolution_urls if m3u8_url else resolution_urls
        # (Damn I love ChatGPT xD)

    @cached_property
    def title(self) -> str:
        """Returns the title of the video"""
        return self.json_tags.get("name")

    @cached_property
    def description(self) -> str:
        """Returns the description of the video"""
        return self.json_tags.get("description")

    @cached_property
    def thumbnail(self) -> str:
        """Returns the thumbnail of the video"""
        return self.json_tags.get("thumbnailUrl")

    @cached_property
    def publish_date(self) -> str:
        """Returns the publish date of the video"""
        return self.json_tags.get("uploadDate")

    @cached_property
    def embed_url(self):
        """Returns the url of the video embed"""
        return self.json_tags.get("embedUrl")

    @cached_property
    def tags(self) -> list:
        """Returns the keywords of the video"""
        return str(self.json_tags.get("keywords")).split(",")

    @cached_property
    def author(self) -> str:
        """Returns the author of the video"""
        return REGEX_VIDEO_AUTHOR.search(self.html_content).group(1)

    @cached_property
    def rating(self) -> str:
        """Returns the rating of the video"""
        return REGEX_VIDEO_RATING.search(self.html_content).group(1)

    @cached_property
    def length(self) -> str:
        """Returns the length in possibly 00:00 format"""
        return REGEX_VIDEO_LENGTH.search(self.stream_data_js).group(1)

    @cached_property
    def m3u8_base_url(self) -> str:
        """Returns the master m3u8 URL of the video"""
        return self.urls_list[0]

    @cached_property
    def direct_download_urls(self) -> list:
        """returns the CDN URLs of the video (direct download links)"""
        _ = []
        for idx, url in enumerate(self.urls_list):
            if idx != 0:
                _.append(url)
        return _

    @cached_property
    def video_qualities(self) -> list:
        """Returns the available qualities of the video"""
        quals = self.direct_download_urls
        qualities = set()
        for url in quals:
            match = PATTERN_RESOLUTION.search(url)
            if match:
                qualities.add(match.group(1).strip("p"))
        return sorted(qualities, key=int)

    def get_segments(self, quality) -> list:
        """Returns a list of segments by a given quality for HLS streaming"""
        return self.core.get_segments(quality=quality, m3u8_url_master=self.m3u8_base_url)

    def download(self, quality: str, downloader: str = "threaded", path="./" ,callback=Callback.text_progress_bar,
                 no_title=False, use_hls=True, remux: bool = False, remux_callback = None):

        if no_title is False:
            path = os.path.join(path, self.core.strip_title(self.title) + ".mp4")

        if use_hls:
            try:
                self.core.download(video=self, quality=quality, path=path, callback=callback, downloader=downloader,
                               remux=remux, callback_remux=remux_callback)
                return True

            except ResourceGone:
                raise VideoUnavailable("The video stream is gone. This is an issue from spankbang! (Not my fault)")

        else:
            cdn_urls = self.direct_download_urls
            quals = self.video_qualities
            quality_url_map = {qual: url for qual, url in zip(quals, cdn_urls)}

            quality_map = {
                "best": max(quals, key=lambda x: int(x)),
                "half": sorted(quals, key=lambda x: int(x))[len(quals) // 2],
                "worst": min(quals, key=lambda x: int(x))
            }

            selected_quality = quality_map[quality]
            download_url = quality_url_map[selected_quality]
            self.logger.info(f"Downloading legacy with URL -->: {download_url}")
            self.core.legacy_download(url=download_url, path=path, callback=callback)
            return True

class Search:
    def __init__(self, query, core: Optional[BaseCore], trending : bool = False, new: bool = False, popular: bool = False, featured: bool = False,
                 quality: Literal["hd", "fhd", "uhd"] = "",
                 duration: Literal["10", "20", "40"] = "",
                 date: Literal["d", "w", "m", "y"] = ""
                 ):
        self.core = core
        """
        :param query:
        :param trending:
        :param new:
        :param popular:
        :param featured:
        :param quality: hd = 720p, fhd = 1080p, uhd = 4k ->: DEFAULT: All qualities
        :param duration: 10 = 10 min, 20 = 20 min, 40 = 40+ min ->: DEFAULT: All durations
        :param date: "d" = day, "w" = week, "m" = month, "y" = year -->: DEFAULT: All dates
        """
        if trending:
            trending = "trending"

        else:
            ""
        if new:
            new = "new"

        else:

            self.html_content = self.core.fetch(url=f"https://www.spankbang.com/s/{query}/?o={trending}", cookies=cookies)


class Client:
    def __init__(self, core: Optional[BaseCore] = None):
        self.core = core or BaseCore(config=RuntimeConfig())
        self.core.initialize_session(headers)

    def get_video(self, url) -> Video:
        return Video(url, core=self.core)
