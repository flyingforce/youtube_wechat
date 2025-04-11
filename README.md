# YouTube to WeChat

A Python application that automatically downloads videos from YouTube channels and sends them to WeChat contacts or groups.

## Features

- Download videos from multiple YouTube channels using yt-dlp (robust against YouTube API changes)
- Multi-threaded downloads for faster performance
- Smart downloading: downloads audio-only when MP3 conversion is enabled (saves bandwidth)
- Duplicate detection: tracks downloaded videos to avoid re-downloading the same content
- Date-based organization: files are stored in date-based directories for easy management
- Filter videos by publication date
- Convert videos to MP3 format
- Send videos and/or MP3s to WeChat contacts or groups
- Run as a one-time operation or as a daemon that checks periodically
- Configurable via YAML file or command-line arguments

## Installation

### Prerequisites

- Python 3.7 or higher
- WeChat account
- FFmpeg (required for MP3 conversion)
  - On macOS: `brew install ffmpeg`
  - On Ubuntu/Debian: `sudo apt-get install ffmpeg`
  - On Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
- yt-dlp (required for YouTube video downloads)
  - Install with pip: `pip install yt-dlp`
  - Or on macOS: `brew install yt-dlp`

### Install from source

1. Clone the repository:
   ```
   git clone https://github.com/flyingforce/youtube-wechat.git
   cd youtube-wechat
   ```

2. Install the package:
   ```
   pip install -e .
   ```

## Usage

### Configuration

The application uses a YAML configuration file (default: `config.yaml`) with the following structure:

```yaml
youtube:
  channels:
    - name: Example Channel
      url: https://www.youtube.com/c/ExampleChannel
      days_to_check: 7
      max_videos: 3
  download_dir: downloads
  preferred_resolution: 720p
  convert_to_mp3: true
  keep_video_after_conversion: true

wechat:
  recipients:
    - name: Friend Name
      is_group: false
  cache_path: wxpy.pkl
  send_message_with_video: true
  message_template: "New video from {channel}: {title}"

app:
  check_interval_hours: 24
  log_level: INFO
  log_file: youtube_wechat.log
```

### Command-line Interface

Run the application:

```
youtube-wechat [options]
```

Options:

- `--config`, `-c`: Path to configuration file (default: `config.yaml`)
- `--run-once`, `-r`: Run once and exit
- `--daemon`, `-d`: Run continuously at configured intervals
- `--skip-wechat`, `-sw`: Skip WeChat login and messaging (download only)
- `--max-workers`, `-mw`: Maximum number of worker threads for parallel downloads (default: 4)

Add a YouTube channel:

```
youtube-wechat --add-channel --channel-name "Channel Name" --channel-url "https://www.youtube.com/c/ChannelName" [--days 7] [--max-videos 3]
```

Add a WeChat recipient:

```
youtube-wechat --add-recipient --recipient-name "Recipient Name" [--is-group]
```

### Python Module Usage

You can also use the application as a Python module:

```python
from youtube_wechat.src.app import YouTubeWeChatApp

# Initialize the application
app = YouTubeWeChatApp(config_path="config.yaml")

# Add a YouTube channel
app.add_youtube_channel(
    name="Channel Name",
    url="https://www.youtube.com/c/ChannelName",
    days=7,
    max_videos=3
)

# Add a WeChat recipient
app.add_wechat_recipient(
    name="Recipient Name",
    is_group=False
)

# Run the application once
app.run_once()

# Or run continuously
# app.run_continuously()
```

## WeChat Login

The application uses the WeChat Web API through the `wxpy` library. When you run the application for the first time, it will display a QR code that you need to scan with your WeChat mobile app to log in.

**Important Note**: WeChat Web has been restricted for many users, and this method may not work for all accounts. If you encounter issues, consider using alternative methods like WeChat Work (企业微信) API if you have access to it.

## Download-Only Mode

If you only want to download videos and convert them to MP3 without sending them through WeChat, you can use the `--skip-wechat` option:

```
youtube-wechat --run-once --skip-wechat
```

This will:
1. Download videos from the configured YouTube channels
2. Convert them to MP3 format (if enabled)
3. Skip the WeChat login and messaging steps

This is useful if:
- You don't have a WeChat account
- WeChat Web API is not working for your account
- You just want to use the application as a YouTube downloader/converter

## Performance Optimization

### Multi-threaded Downloads

The application uses multiple threads to download videos in parallel, which significantly improves performance when downloading multiple videos. You can control the number of concurrent downloads using the `--max-workers` option:

```
youtube-wechat --run-once --max-workers 8
```

This will use 8 threads for parallel downloads. The default is 4 threads, which works well for most systems. If you have a faster internet connection, you can increase this number for better performance.

### Audio-Only Downloads

When MP3 conversion is enabled, the application will only download the audio stream of videos, which is much smaller than the full video. This saves bandwidth and speeds up the download process.

### Duplicate Detection

The application maintains a record of all downloaded video titles in a file called `downloaded_titles.txt` in the downloads directory. Before downloading a video, it checks if the title is already in this file to avoid downloading duplicates. This is especially useful when running the application periodically, as it ensures you don't waste bandwidth re-downloading videos you already have.

### Date-Based Organization

Downloaded files are automatically organized into date-based directories (format: YYYYMMDD) within the downloads folder. This makes it easy to find videos from a specific date and keeps your downloads organized.

## Limitations

- WeChat Web API has limitations and may not work for all accounts
- YouTube may rate-limit requests if you download too many videos in a short period
- Large video files may take a long time to download and send
- WeChat may have file size limitations for sending videos
- MP3 conversion requires FFmpeg to be installed on your system

## Troubleshooting

### YouTube Download Issues

If you encounter issues with YouTube video downloads:

1. Ensure yt-dlp is installed and up-to-date: `pip install -U yt-dlp`
2. If yt-dlp fails, the application will attempt to use alternative download methods
3. You may need to update yt-dlp periodically as YouTube changes its systems: `pip install -U yt-dlp`

### MP3 Conversion Issues

If you encounter issues with MP3 conversion:

1. Ensure FFmpeg is installed and available in your PATH
2. Check that all moviepy dependencies are installed: `pip install -r requirements.txt`
3. If you still have issues, you can disable MP3 conversion by setting `convert_to_mp3: false` in your config.yaml

## License

This project is licensed under the MIT License - see the LICENSE file for details.
