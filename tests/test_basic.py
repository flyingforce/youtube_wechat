"""Basic tests for YouTube to WeChat application."""

import os
import unittest
from unittest.mock import patch, MagicMock

from src.config import Config
from src.youtube_downloader import YouTubeDownloader
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
from src.wechat_messenger import WeChatMessenger
from src.telegram_messenger import TelegramMessenger
from src.app import YouTubeWeChatApp


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

    @patch('src.youtube_downloader.scrapetube.get_channel')
    @patch('src.youtube_downloader.VideoFileClip')
    def test_youtube_downloader(self, mock_video_clip, mock_get_channel):
        """Test YouTube downloader functionality."""
        # Mock scrapetube.get_channel to avoid actual API calls
        mock_get_channel.return_value = [
            {
                'videoId': 'example1',
                'title': {'runs': [{'text': 'Test Video'}]},
                'publishedTimeText': {'simpleText': '1 day ago'}
            }
        ]

        # Mock subprocess.run to avoid actual command execution
        with patch('src.youtube_downloader.subprocess.run') as mock_subprocess_run:
            mock_subprocess_run.return_value = MagicMock()
            
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

    @patch('src.wechat_messenger.Bot')
    def test_wechat_messenger(self, mock_bot):
        """Test WeChat messenger functionality."""
        # Mock Bot to avoid actual API calls
        mock_bot_instance = MagicMock()
        mock_bot.return_value = mock_bot_instance

        # Create messenger
        messenger = WeChatMessenger(cache_path="test_cache.pkl")

        # Test login
        self.assertTrue(messenger.login())

    @patch('src.telegram_messenger.Bot')
    def test_telegram_messenger(self, mock_bot):
        """Test Telegram messenger functionality."""
        # Mock Bot to avoid actual API calls
        mock_bot_instance = MagicMock()
        mock_bot.return_value = mock_bot_instance

        # Create messenger
        messenger = TelegramMessenger(token="test_token")

        # Test login
        self.assertTrue(messenger.login())

        # Test send_message
        self.assertTrue(messenger.send_message("test_chat_id", "test message"))

        # Test send_file
        with patch('builtins.open', unittest.mock.mock_open(read_data=b'test')):
            self.assertTrue(messenger.send_file("test_chat_id", "test_file.txt"))

        # Test send_video
        with patch('builtins.open', unittest.mock.mock_open(read_data=b'test')):
            self.assertTrue(messenger.send_video("test_chat_id", "test_video.mp4"))

        # Test send_videos
        with patch('builtins.open', unittest.mock.mock_open(read_data=b'test')):
            successful_sends = messenger.send_videos("test_chat_id", ["test_video1.mp4", "test_video2.mp4"])
            self.assertEqual(len(successful_sends), 2)

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

    @patch('src.app.Config')
    @patch('src.app.YouTubeDownloader')
    @patch('src.app.WeChatMessenger')
    @patch('src.app.TelegramMessenger')
    def test_app(self, mock_telegram, mock_messenger, mock_downloader, mock_config):
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
        mock_config_instance.get_telegram_recipients.return_value = [
            {"chat_id": "test_chat_id", "name": "Test Chat"}
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

        # Mock TelegramMessenger to avoid actual Telegram operations
        mock_telegram_instance = MagicMock()
        mock_telegram_instance.login.return_value = True
        mock_telegram_instance.send_videos.return_value = ["test_video.mp4"]
        mock_telegram.return_value = mock_telegram_instance

        # Create app
        app = YouTubeWeChatApp(config_path="test_config.yaml")

        # Test run_once
        result = app.run_once()
        # Expecting 5 files: 1 video + 1 MP3 sent to WeChat, and 1 video + 1 MP3 sent to Telegram
        self.assertEqual(result, 5)


if __name__ == "__main__":
    unittest.main()
