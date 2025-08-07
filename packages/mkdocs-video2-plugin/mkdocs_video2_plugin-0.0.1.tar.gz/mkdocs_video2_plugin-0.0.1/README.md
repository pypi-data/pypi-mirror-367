# mkdocs-video2-plugin

MkDocs plugin for embedding videos in generated documentation.

This plugin allows you to embed videos directly in your markdown content using a simple comment-based syntax that gets converted to HTML video elements.

![screenshot](https://github.com/mihaigalos/mkdocs-video2-plugin/raw/main/screenshots/mkdocs-video2-plugin.png)

## Setup

Install the plugin using pip:

```bash
pip install mkdocs-video2-plugin
```

Activate the plugin in `mkdocs.yaml`:

```yaml
plugins:
  - video2:
      video_autoplay: false  # Enable/disable autoplay by default
      video_muted: false     # Enable/disable muted by default
      video_loop: false      # Enable/disable loop by default
      video_controls: true   # Enable/disable controls by default
      video_type: "mp4"      # Default video type
```

## Usage

To embed a video in your markdown, use the following syntax:

```markdown
https://example.com/video.mp4 <!--video 640x480 autoplay=true mute=true loop=false controls=true-->
```

### Parameters

The video comment supports the following parameters:

- **Dimensions**: `640x480` - Set video width and height
- **autoplay**: `true|false` - Enable/disable autoplay
- **mute**: `true|false` - Enable/disable muted audio
- **loop**: `true|false` - Enable/disable video looping
- **controls**: `true|false` - Show/hide video controls
- **type**: `mp4|webm|ogg|quicktime` - Explicit video type (optional)

### Examples

Basic video with custom dimensions:
```markdown
https://example.com/video.mp4 <!--video 640x480-->
```

Video with all options:
```markdown
https://example.com/video.webm <!--video 1280x720 autoplay=true mute=true loop=true controls=true type=video/webm-->
```

Multiple videos:
```markdown
First video:
https://example.com/video1.mp4 <!--video 640x480 autoplay=true-->

Second video:
https://example.com/video2.webm <!--video 800x600 loop=true controls=false-->
```

## Supported Video Formats

The plugin automatically detects video types from URL extensions:

- **MP4**: `.mp4` → `video/mp4`
- **WebM**: `.webm` → `video/webm`
- **OGG**: `.ogg` → `video/ogg`
- **QuickTime**: `.mov` → `video/quicktime`
- **AVI**: `.avi` → `video/x-msvideo`
- **WMV**: `.wmv` → `video/x-ms-wmv`

For URLs without clear extensions, you can specify the type explicitly:

```markdown
https://example.com/video <!--video 640x480 type=mp4-->
https://example.com/video <!--video 640x480 type=video/webm-->
```

## Generated HTML

The plugin converts the markdown syntax into standard HTML5 video elements:

```html
<video width="640" height="480" controls muted>
  <source src="https://example.com/video.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>
```

## Development

### Running Tests

To run the tests, use the following commands:

```bash
# Run tests directly
python3 mkdocs_video2_plugin/test_plugin.py

# Run tests with verbose output
python3 mkdocs_video2_plugin/test_plugin.py --verbose

# Run with unittest discovery
python3 -m unittest discover -s mkdocs_video2_plugin -p "test_*.py"
```

### Project Structure

```
mkdocs-video2-plugin/
├── mkdocs_video2_plugin/
│   ├── __init__.py
│   ├── plugin.py          # Main plugin implementation
│   ├── test_plugin.py     # Unit tests
│   └── example.md         # Usage examples
├── README.md
├── setup.py
└── mkdocs.yaml
```
