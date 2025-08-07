#!/usr/bin/env python3

from mkdocs_video2_plugin.plugin import Video2
from unittest.mock import MagicMock
import sys
import os
import logging
import unittest

sys.path.insert(0, os.path.dirname(__file__))


config_mock = MagicMock()
config_mock.config_options = MagicMock()
config_mock.config_options.Type = MagicMock(return_value=MagicMock())
sys.modules["mkdocs.config"] = config_mock

plugins_mock = MagicMock()
plugins_mock.BasePlugin = object
sys.modules["mkdocs.plugins"] = plugins_mock


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class TestVideo2Plugin(unittest.TestCase):

    def setUp(self):
        self.plugin = Video2()

        self.plugin.config = {
            "video_autoplay": False,
            "video_muted": False,
            "video_loop": False,
            "video_controls": True,
            "video_type": "mp4",
        }

    def test_video_parsing(self):

        test_html = """Here's a video:
https://foo.bar/myuser/notes/assets/8554/586611ec-a727-4041-9c29-76c19dbe7e8f <!--video 640x480 autoplay=false mute=true-->
End of content"""

        result = self.plugin.on_page_content(test_html, None, None, None)

        expected_elements = [
            'src="https://foo.bar/myuser/notes/assets/8554/586611ec-a727-4041-9c29-76c19dbe7e8f"',
            'data-canonical-src="https://foo.bar/myuser/notes/assets/8554/586611ec-a727-4041-9c29-76c19dbe7e8f"',
            'controls="controls"',
            'muted="muted"',
            'class="d-block rounded-bottom-2 border-top width-fit"',
            'style="width:640px; height:480px; min-height: 200px"',
        ]

        for element in expected_elements:
            self.assertIn(element, result, f"Expected element not found: {element}")
            logger.debug(f"✅ Found expected element: {element}")

        logger.debug("✅ Basic video parsing test passed")

    def test_multiple_videos(self):

        test_html = """First video:
https://foo.bar/video1.mp4 <!--video 640x480 autoplay=true mute=false-->
Second video:
https://foo.bar/video2.webm <!--video 800x600 loop=true controls=false-->"""

        result = self.plugin.on_page_content(test_html, None, None, None)

        expected_elements = [
            'src="https://foo.bar/video1.mp4"',
            'autoplay="autoplay"',
            'src="https://foo.bar/video2.webm"',
            'loop="loop"',
            'style="width:640px; height:480px; min-height: 200px"',
            'style="width:800px; height:600px; min-height: 200px"',
        ]

        for element in expected_elements:
            self.assertIn(element, result, f"Expected element not found: {element}")
            logger.debug(f"✅ Found expected element: {element}")

        video_count = result.count("<video")
        self.assertEqual(video_count, 2, f"Expected 2 videos, found {video_count}")

        logger.debug("✅ Multiple videos test passed")

    def test_explicit_video_type(self):

        test_html = """Video with explicit type:
https://foo.bar/video <!--video 640x480 type=mp4-->
Video with MIME type:
https://foo.bar/video2 <!--video 800x600 type=video/webm-->"""

        result = self.plugin.on_page_content(test_html, None, None, None)

        self.assertIn(
            'src="https://foo.bar/video"', result, "Expected video URL not found"
        )
        self.assertIn(
            'src="https://foo.bar/video2"', result, "Expected video2 URL not found"
        )

        logger.debug("✅ Found video URLs")

        logger.debug("✅ Explicit video type test passed")

    def test_parameter_parsing(self):

        test_html = """No controls:
https://foo.bar/video1.mp4 <!--video 640x480 controls=false-->
All attributes:
https://foo.bar/video2.mp4 <!--video 1280x720 autoplay=true mute=true loop=true controls=true-->"""

        result = self.plugin.on_page_content(test_html, None, None, None)

        # Video without controls should not have controls attribute
        self.assertNotIn(
            'controls="controls"',
            result.split("<video")[1].split("</video>")[0],
            "Video without controls should not have controls attribute",
        )
        # Video with all attributes should have all attributes
        self.assertIn(
            'controls="controls"',
            result,
            "Video with controls should have controls attribute",
        )
        self.assertIn(
            'autoplay="autoplay"',
            result,
            "Video with autoplay should have autoplay attribute",
        )
        self.assertIn(
            'muted="muted"', result, "Video with mute should have muted attribute"
        )
        self.assertIn(
            'loop="loop"', result, "Video with loop should have loop attribute"
        )

        logger.debug("✅ Parameter parsing test passed")

    def test_asset_url_transformation(self):

        test_html = """https://code.rbi.tech/raiffeisen/Mercury/assets/8554/8787819d-4b2b-41bf-b71b-ffe84ca454c1"""

        result = self.plugin.on_page_content(test_html, None, None, None)

        expected_elements = [
            'src="https://media.code.rbi.tech/user/8554/files/8787819d-4b2b-41bf-b71b-ffe84ca454c1"',
            'data-canonical-src="https://media.code.rbi.tech/user/8554/files/8787819d-4b2b-41bf-b71b-ffe84ca454c1"',
            'controls="controls"',
            'class="d-block rounded-bottom-2 border-top width-fit"',
            'style="max-height:640px; min-height: 200px"',
        ]

        for element in expected_elements:
            self.assertIn(element, result, f"Expected element not found: {element}")
            logger.debug(f"✅ Found expected element: {element}")

        # Verify muted is NOT present (since default is False)
        self.assertNotIn(
            'muted="muted"', result, "Muted should not be present with default config"
        )

        logger.debug("✅ Asset URL transformation test passed")


if __name__ == "__main__":
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    unittest.main()
