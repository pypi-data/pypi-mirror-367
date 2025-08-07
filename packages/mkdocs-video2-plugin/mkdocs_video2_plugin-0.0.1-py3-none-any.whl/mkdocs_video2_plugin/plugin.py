import re
from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin


class Video2(BasePlugin):

    config_scheme = (
        ("mark", config_options.Type(str, default="type:video")),
        ("is_video", config_options.Type(bool, default=False)),
        ("video_type", config_options.Type(str, default="mp4")),
        ("video_muted", config_options.Type(bool, default=False)),
        ("video_loop", config_options.Type(bool, default=False)),
        ("video_controls", config_options.Type(bool, default=True)),
        ("video_autoplay", config_options.Type(bool, default=False)),
        (
            "css_style",
            config_options.Type(
                dict,
                default={"position": "relative", "width": "100%", "height": "22.172vw"},
            ),
        ),
    )

    def on_page_content(self, html, page, config, files):
        """
        Process page content to convert video markdown to HTML video elements.

        Looks for patterns like:
        https://code.rbi.tech/raiffeisen/Mercury/assets/8554/8787819d-4b2b-41bf-b71b-ffe84ca454c1

        And converts them to HTML video elements with proper media URLs.
        """
        asset_pattern = r"https://code\.rbi\.tech/[^/]+/[^/]+/assets/(\d+)/([a-f0-9-]+)"

        video_pattern = r"(https?://[^\s]+)\s*<!--\s*video\s+([^>]+)-->"

        def replace_asset_url(match):
            user_id = match.group(1)
            file_id = match.group(2)
            return f"https://media.code.rbi.tech/user/{user_id}/files/{file_id}"

        def replace_video(match):
            video_url = match.group(1)
            video_params = match.group(2) if len(match.groups()) > 1 else ""

            video_url = re.sub(asset_pattern, replace_asset_url, video_url)

            width, height = self._parse_dimensions(video_params)
            autoplay = self._parse_boolean_param(
                video_params, "autoplay", self.config["video_autoplay"]
            )
            muted = self._parse_boolean_param(
                video_params, "mute", self.config["video_muted"]
            )
            loop = self._parse_boolean_param(
                video_params, "loop", self.config["video_loop"]
            )
            controls = self._parse_boolean_param(
                video_params, "controls", self.config["video_controls"]
            )

            video_type = self._parse_video_type(video_params, video_url)

            return self._generate_video_html(
                video_url, video_type, width, height, autoplay, muted, loop, controls
            )

        def replace_standalone_asset(match):
            transformed_url = replace_asset_url(match)
            return self._generate_video_html(
                transformed_url,
                "video/quicktime",
                None,
                None,
                self.config["video_autoplay"],
                self.config["video_muted"],
                self.config["video_loop"],
                self.config["video_controls"],
            )

        html = re.sub(asset_pattern, replace_standalone_asset, html)
        html = re.sub(video_pattern, replace_video, html)

        return html

    def _parse_dimensions(self, params):
        """Parse width and height from video parameters."""

        dimension_match = re.search(r"(\d+)x(\d+)", params)
        if dimension_match:
            return dimension_match.group(1), dimension_match.group(2)
        return None, None

    def _parse_boolean_param(self, params, param_name, default_value):
        """Parse boolean parameters from video comment."""

        param_match = re.search(rf"{param_name}=(\w+)", params)
        if param_match:
            value = param_match.group(1).lower()
            return value in ["true", "1", "yes", "on"]
        return default_value

    def _parse_video_type(self, params, video_url):
        """Parse video type from parameters or determine from URL."""

        type_match = re.search(r"type=([a-zA-Z0-9/-]+)", params)
        if type_match:
            type_value = type_match.group(1)

            if "/" not in type_value:
                return f"video/{type_value}"
            return type_value

        return self._determine_video_type(video_url)

    def _determine_video_type(self, video_url):
        """Determine video MIME type from URL extension."""
        url_lower = video_url.lower()

        if url_lower.endswith(".mp4"):
            return "video/mp4"
        elif url_lower.endswith(".webm"):
            return "video/webm"
        elif url_lower.endswith(".ogg"):
            return "video/ogg"
        elif url_lower.endswith(".mov"):
            return "video/quicktime"
        elif url_lower.endswith(".avi"):
            return "video/x-msvideo"
        elif url_lower.endswith(".wmv"):
            return "video/x-ms-wmv"
        else:
            if "quicktime" in url_lower or ".mov" in url_lower:
                return "video/quicktime"
            elif "webm" in url_lower:
                return "video/webm"
            elif "mp4" in url_lower:
                return "video/mp4"
            else:
                return "video/quicktime"

    def _generate_video_html(
        self, video_url, video_type, width, height, autoplay, muted, loop, controls
    ):
        """Generate HTML video element in GitHub/GitLab style."""

        video_attrs = [f'src="{video_url}"', f'data-canonical-src="{video_url}"']

        if controls:
            video_attrs.append('controls="controls"')
        if autoplay:
            video_attrs.append('autoplay="autoplay"')
        if muted:
            video_attrs.append('muted="muted"')
        if loop:
            video_attrs.append('loop="loop"')

        video_attrs.append('class="d-block rounded-bottom-2 border-top width-fit"')

        if width and height:
            video_attrs.append(
                f'style="width:{width}px; height:{height}px; min-height: 200px"'
            )
        else:
            video_attrs.append('style="max-height:640px; min-height: 200px"')

        attrs_str = " ".join(video_attrs)

        return f"<video {attrs_str}></video>"
