"""Main application module for YouTube to WeChat video sharing."""

import os
import sys
import time
import logging
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from .config import Config
from .youtube_downloader import YouTubeDownloader
from .wechat_messenger import WeChatMessenger
from .telegram_messenger import TelegramMessenger

# Set up logging
def setup_logging(log_file: str = None, log_level: str = "INFO"):
    """
    Set up logging configuration.
    
    Args:
        log_file: Path to log file (if None, log to console only)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        handlers=handlers
    )

class YouTubeWeChatApp:
    """Main application class for YouTube to WeChat video sharing."""
    
    def __init__(self, config_path: str = "config.yaml", skip_wechat: bool = False, skip_telegram: bool = False, max_workers: int = 4):
        """
        Initialize the application.
        
        Args:
            config_path: Path to configuration file
            skip_wechat: Whether to skip WeChat login and messaging
            skip_telegram: Whether to skip Telegram messaging
            max_workers: Maximum number of worker threads for parallel downloads
        """
        self.config = Config(config_path)
        self.skip_wechat = skip_wechat
        self.skip_telegram = skip_telegram
        self.max_workers = max_workers
        
        # Set up logging
        setup_logging(
            log_file=self.config.get_log_file(),
            log_level=self.config.get_log_level()
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing YouTube to WeChat application")
        
        # Initialize YouTube downloader
        self.downloader = YouTubeDownloader(
            download_dir=self.config.get_download_dir(),
            convert_to_mp3=self.config.should_convert_to_mp3(),
            max_workers=self.max_workers
        )
        
        # Initialize WeChat messenger if not skipped
        self.wechat_messenger = None
        if not self.skip_wechat:
            self.logger.info("Initializing WeChat messenger")
            self.wechat_messenger = WeChatMessenger(
                cache_path=self.config.get_wechat_cache_path()
            )
        else:
            self.logger.info("WeChat messaging is disabled")
            
        # Initialize Telegram messenger if not skipped
        self.telegram_messenger = None
        if not self.skip_telegram:
            self.logger.info("Initializing Telegram messenger")
            self.telegram_messenger = TelegramMessenger(
                token=self.config.get_telegram_bot_token()
            )
        else:
            self.logger.info("Telegram messaging is disabled")
        
    def process_channel(self, channel: Dict[str, Any]) -> List[Tuple[str, Optional[str]]]:
        """
        Process a YouTube channel: download videos and return file paths.
        
        Args:
            channel: Channel configuration dictionary
            
        Returns:
            List of tuples containing (video_path, mp3_path) for each downloaded video
        """
        self.logger.info(f"Processing channel: {channel['name']}")
        
        # Download recent videos
        downloaded_files = self.downloader.download_recent_videos(
            channel_url=channel["url"],
            days=channel.get("days_to_check", 7),
            limit=channel.get("max_videos", 3)
        )
        
        self.logger.info(f"Downloaded {len(downloaded_files)} videos from {channel['name']}")
        return downloaded_files
        
    def send_videos_to_wechat_recipient(self, recipient: Dict[str, Any], videos: List[Tuple[str, Optional[str]]], channel_name: str) -> int:
        """
        Send videos and/or MP3s to a WeChat recipient.
        
        Args:
            recipient: Recipient configuration dictionary
            videos: List of tuples containing (video_path, mp3_path) for each downloaded video
            channel_name: Name of the YouTube channel
            
        Returns:
            Number of successfully sent files (videos and/or MP3s)
        """
        if not videos:
            self.logger.info(f"No videos to send to WeChat recipient {recipient['name']}")
            return 0
            
        self.logger.info(f"Sending {len(videos)} videos/MP3s to WeChat recipient {recipient['name']}")
        
        total_successful_sends = 0
        
        # Process each video/MP3 pair
        for video_path, mp3_path in videos:
            # Send MP3 if available
            if mp3_path:
                self.logger.info(f"Sending MP3: {mp3_path}")
                if self.wechat_messenger.send_file(
                    recipient_name=recipient["name"],
                    file_path=mp3_path,
                    is_group=recipient.get("is_group", False)
                ):
                    total_successful_sends += 1
            
            # Send video if we should keep it or if MP3 conversion failed
            if self.config.should_keep_video_after_conversion() or not mp3_path:
                self.logger.info(f"Sending video: {video_path}")
                if self.wechat_messenger.send_file(
                    recipient_name=recipient["name"],
                    file_path=video_path,
                    is_group=recipient.get("is_group", False)
                ):
                    total_successful_sends += 1
        
        self.logger.info(f"Successfully sent {total_successful_sends} files to WeChat recipient {recipient['name']}")
        return total_successful_sends
        
    def send_videos_to_telegram_recipient(self, recipient: Dict[str, Any], videos: List[Tuple[str, Optional[str]]], channel_name: str) -> int:
        """
        Send videos and/or MP3s to a Telegram recipient.
        
        Args:
            recipient: Recipient configuration dictionary
            videos: List of tuples containing (video_path, mp3_path) for each downloaded video
            channel_name: Name of the YouTube channel
            
        Returns:
            Number of successfully sent files (videos and/or MP3s)
        """
        if not videos:
            self.logger.info(f"No videos to send to Telegram recipient {recipient.get('name', recipient['chat_id'])}")
            return 0
            
        self.logger.info(f"Sending {len(videos)} videos/MP3s to Telegram recipient {recipient.get('name', recipient['chat_id'])}")
        
        total_successful_sends = 0
        
        # Process each video/MP3 pair
        for video_path, mp3_path in videos:
            # Send MP3 if available
            if mp3_path:
                self.logger.info(f"Sending MP3: {mp3_path}")
                if self.telegram_messenger.send_file(
                    chat_id=recipient["chat_id"],
                    file_path=mp3_path
                ):
                    total_successful_sends += 1
            
            # Send video if we should keep it or if MP3 conversion failed
            if self.config.should_keep_video_after_conversion() or not mp3_path:
                self.logger.info(f"Sending video: {video_path}")
                if self.telegram_messenger.send_video(
                    chat_id=recipient["chat_id"],
                    video_path=video_path
                ):
                    total_successful_sends += 1
        
        self.logger.info(f"Successfully sent {total_successful_sends} files to Telegram recipient {recipient.get('name', recipient['chat_id'])}")
        return total_successful_sends
        
    def run_once(self) -> int:
        """
        Run the application once: download videos and optionally send them.
        
        Returns:
            Number of videos downloaded or sent
        """
        self.logger.info("Starting application run")
        
        # Login to WeChat if not skipped
        wechat_logged_in = False
        if not self.skip_wechat and self.wechat_messenger:
            wechat_logged_in = self.wechat_messenger.login()
            if not wechat_logged_in:
                self.logger.warning("Failed to log in to WeChat, will only download videos")
                
        # Login to Telegram if not skipped
        telegram_logged_in = False
        if not self.skip_telegram and self.telegram_messenger:
            telegram_logged_in = self.telegram_messenger.login()
            if not telegram_logged_in:
                self.logger.warning("Failed to log in to Telegram, will only download videos")
            
        total_processed = 0
        
        try:
            # Process each channel
            for channel in self.config.get_youtube_channels():
                self.logger.info(f"operate channel {channel}")
                # Download videos
                videos = self.process_channel(channel)
                
                if not videos:
                    continue
                
                # Count downloaded videos
                total_processed += len(videos)
                
                # Send videos if WeChat is enabled and logged in
                if wechat_logged_in and self.wechat_messenger:
                    self.logger.info(f"Sending videos to WeChat recipients")
                    for recipient in self.config.get_wechat_recipients():
                        # Send a message with the video if configured
                        if self.config.should_send_message_with_video():
                            for video_path, mp3_path in videos:
                                # Get video title from filename
                                video_title = os.path.basename(video_path)
                                
                                # Format message
                                message = self.config.get_wechat_message_template().format(
                                    channel=channel["name"],
                                    title=video_title
                                )
                                
                                # Send message
                                self.wechat_messenger.send_message(
                                    recipient_name=recipient["name"],
                                    message=message,
                                    is_group=recipient.get("is_group", False)
                                )
                        
                        # Send videos and/or MP3s
                        sent = self.send_videos_to_wechat_recipient(recipient, videos, channel["name"])
                        total_processed += sent
                        
                # Send videos if Telegram is enabled and logged in
                if telegram_logged_in and self.telegram_messenger:
                    self.logger.info(f"Sending videos to Telegram recipients")
                    for recipient in self.config.get_telegram_recipients():
                        # Send a message with the video if configured
                        if self.config.should_send_telegram_message_with_video():
                            for video_path, mp3_path in videos:
                                # Get video title from filename
                                video_title = os.path.basename(video_path)
                                
                                # Format message
                                message = self.config.get_telegram_message_template().format(
                                    channel=channel["name"],
                                    title=video_title
                                )
                                
                                # Send message
                                self.telegram_messenger.send_message(
                                    chat_id=recipient["chat_id"],
                                    message=message
                                )
                        
                        # Send videos and/or MP3s
                        sent = self.send_videos_to_telegram_recipient(recipient, videos, channel["name"])
                        total_processed += sent
                        
                if not (wechat_logged_in or telegram_logged_in):
                    self.logger.info(f"Downloaded {len(videos)} videos/MP3s (messaging disabled)")
                    # Log the paths of downloaded files
                    for video_path, mp3_path in videos:
                        if mp3_path:
                            self.logger.info(f"Downloaded MP3: {mp3_path}")
                        if video_path and not video_path.endswith(".mp4_dummy"):
                            self.logger.info(f"Downloaded video: {video_path}")
        finally:
            # Logout from WeChat if logged in
            if wechat_logged_in and self.wechat_messenger:
                self.wechat_messenger.logout()
            
        if wechat_logged_in or telegram_logged_in:
            self.logger.info(f"Application run completed. Sent {total_processed} files.")
        else:
            self.logger.info(f"Application run completed. Downloaded {total_processed} files.")
            
        return total_processed
        
    def run_continuously(self) -> None:
        """Run the application continuously at configured intervals."""
        self.logger.info("Starting continuous run mode")
        
        interval_hours = self.config.get_check_interval_hours()
        interval_seconds = interval_hours * 3600
        
        self.logger.info(f"Check interval: {interval_hours} hours")
        
        try:
            while True:
                start_time = time.time()
                
                try:
                    self.run_once()
                except Exception as e:
                    self.logger.error(f"Error in application run: {e}")
                
                # Calculate sleep time
                elapsed = time.time() - start_time
                sleep_time = max(0, interval_seconds - elapsed)
                
                if sleep_time > 0:
                    next_run = datetime.now().timestamp() + sleep_time
                    next_run_str = datetime.fromtimestamp(next_run).strftime('%Y-%m-%d %H:%M:%S')
                    self.logger.info(f"Next run scheduled at {next_run_str}")
                    time.sleep(sleep_time)
        except KeyboardInterrupt:
            self.logger.info("Application stopped by user")
            
    def add_youtube_channel(self, name: str, url: str, days: int = 7, max_videos: int = 3) -> bool:
        """
        Add a YouTube channel to monitor.
        
        Args:
            name: Channel name
            url: Channel URL
            days: Number of days to check for new videos
            max_videos: Maximum number of videos to download per run
            
        Returns:
            True if channel added successfully, False otherwise
        """
        return self.config.add_youtube_channel(name, url, days, max_videos)
        
    def add_wechat_recipient(self, name: str, is_group: bool = False) -> bool:
        """
        Add a WeChat recipient.
        
        Args:
            name: Recipient name
            is_group: Whether the recipient is a group
            
        Returns:
            True if recipient added successfully, False otherwise
        """
        return self.config.add_wechat_recipient(name, is_group)
        
    def add_telegram_recipient(self, chat_id: str, name: str = None) -> bool:
        """
        Add a Telegram recipient.
        
        Args:
            chat_id: Telegram chat ID
            name: Optional name for reference
            
        Returns:
            True if recipient added successfully, False otherwise
        """
        return self.config.add_telegram_recipient(chat_id, name)

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="YouTube to WeChat video sharing application")
    parser.add_argument("--config", default="config.yaml", help="Path to configuration file")
    parser.add_argument("--skip-wechat", action="store_true", help="Skip WeChat login and messaging")
    parser.add_argument("--skip-telegram", action="store_true", help="Skip Telegram messaging")
    parser.add_argument("--max-workers", type=int, default=4, help="Maximum number of worker threads")
    parser.add_argument("--continuous", action="store_true", help="Run continuously")
    
    args = parser.parse_args()
    
    app = YouTubeWeChatApp(
        config_path=args.config,
        skip_wechat=args.skip_wechat,
        skip_telegram=args.skip_telegram,
        max_workers=args.max_workers
    )
    
    if args.continuous:
        app.run_continuously()
    else:
        app.run_once()

if __name__ == "__main__":
    main()
