"""Basic tests for YouTube to WeChat application."""

import os
import unittest
from unittest.mock import patch, MagicMock

from youtube_wechat.src.config import Config
from youtube_wechat.src.youtube_downloader import YouTubeDownloader
# Import VideoFileClip from the module directly for mocking
try:
    from moviepy.editor import VideoFileClip
except ImportError:
    try:
        from moviepy.video.io.VideoFileClip import VideoFileClip
    except ImportError:
        # Mock VideoFileClip for testing if moviepy is not installed
        class VideoFileClip:
            pass
from youtube_wechat.src.wechat_messenger import WeChatMessenger
from youtube_wechat.src.app import YouTubeWeChatApp


class TestBasicFunctionality(unittest.TestCase):
    """Test basic functionality of the application."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for testing
        self.test_dir = "test_downloads"
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        """Clean up test environment."""
        # Remove test directory if it exists
        if os.path.exists(self.test_dir):
            # In a real test, you would remove the directory
            # but for this example, we'll just print a message
            print(f"Would remove directory: {self.test_dir}")

    @patch('youtube_wechat.src.youtube_downloader.Channel')
    @patch('youtube_wechat.src.youtube_downloader.VideoFileClip')
    def test_youtube_downloader(self, mock_video_clip, mock_channel):
        """Test YouTube downloader functionality."""
        # Mock Channel to avoid actual API calls
        mock_channel_instance = MagicMock()
        mock_channel_instance.video_urls = ["https://www.youtube.com/watch?v=example1"]
        mock_channel.return_value = mock_channel_instance

        # Mock YouTube to avoid actual API calls
        with patch('youtube_wechat.src.youtube_downloader.YouTube') as mock_youtube:
            mock_youtube_instance = MagicMock()
            mock_youtube_instance.title = "Test Video"
            mock_youtube_instance.publish_date = None
            mock_youtube_instance.views = 1000
            mock_youtube_instance.length = 60
            mock_youtube_instance.author = "Test Channel"
            mock_youtube_instance.video_id = "example1"
            mock_youtube.return_value = mock_youtube_instance

            # Mock VideoFileClip for MP3 conversion
            mock_video_clip_instance = MagicMock()
            mock_audio_clip = MagicMock()
            mock_video_clip_instance.audio = mock_audio_clip
            mock_video_clip.return_value = mock_video_clip_instance
            
            # Create downloader
            downloader = YouTubeDownloader(download_dir=self.test_dir, convert_to_mp3=True)

            # Test get_channel_videos
            videos = downloader.get_channel_videos("https://www.youtube.com/c/TestChannel")
            self.assertEqual(len(videos), 1)
            self.assertEqual(videos[0]["title"], "Test Video")
            
            # Test convert_video_to_mp3
            mp3_path = downloader.convert_video_to_mp3("test_video.mp4")
            self.assertIsNotNone(mp3_path)
            mock_audio_clip.write_audiofile.assert_called_once()

    @patch('youtube_wechat.src.wechat_messenger.Bot')
    def test_wechat_messenger(self, mock_bot):
        """Test WeChat messenger functionality."""
        # Mock Bot to avoid actual API calls
        mock_bot_instance = MagicMock()
        mock_bot.return_value = mock_bot_instance

        # Create messenger
        messenger = WeChatMessenger(cache_path="test_cache.pkl")

        # Test login
        self.assertTrue(messenger.login())

    def test_config(self):
        """Test configuration functionality."""
        # Create a config with default values
        config = Config()

        # Test getters
        self.assertEqual(config.get_download_dir(), "downloads")
        self.assertEqual(config.get_preferred_resolution(), "720p")
        self.assertEqual(config.get_check_interval_hours(), 24)
        self.assertTrue(config.should_convert_to_mp3())
        self.assertTrue(config.should_keep_video_after_conversion())

    @patch('youtube_wechat.src.app.Config')
    @patch('youtube_wechat.src.app.YouTubeDownloader')
    @patch('youtube_wechat.src.app.WeChatMessenger')
    def test_app(self, mock_messenger, mock_downloader, mock_config):
        """Test application functionality."""
        # Mock Config to avoid file operations
        mock_config_instance = MagicMock()
        mock_config_instance.get_download_dir.return_value = self.test_dir
        mock_config_instance.get_wechat_cache_path.return_value = "test_cache.pkl"
        mock_config_instance.get_log_file.return_value = None
        mock_config_instance.get_log_level.return_value = "INFO"
        mock_config_instance.get_youtube_channels.return_value = [
            {"name": "Test Channel", "url": "https://www.youtube.com/c/TestChannel"}
        ]
        mock_config_instance.get_wechat_recipients.return_value = [
            {"name": "Test Friend", "is_group": False}
        ]
        mock_config.return_value = mock_config_instance

        # Mock YouTubeDownloader to avoid actual downloads
        mock_downloader_instance = MagicMock()
        mock_downloader_instance.download_recent_videos.return_value = [("test_video.mp4", "test_video.mp3")]
        mock_downloader.return_value = mock_downloader_instance

        # Mock WeChatMessenger to avoid actual WeChat operations
        mock_messenger_instance = MagicMock()
        mock_messenger_instance.login.return_value = True
        mock_messenger_instance.send_videos.return_value = ["test_video.mp4"]
        mock_messenger.return_value = mock_messenger_instance

        # Create app
        app = YouTubeWeChatApp(config_path="test_config.yaml")

        # Test run_once
        result = app.run_once()
        self.assertEqual(result, 1)  # One video sent


if __name__ == "__main__":
    unittest.main()
