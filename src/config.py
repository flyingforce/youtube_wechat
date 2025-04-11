"""Configuration module for YouTube to WeChat application."""

import os
import yaml
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    "youtube": {
        "channels": [
            # Example channel configuration
            {
                "name": "Example Channel",
                "url": "https://www.youtube.com/@wongkim728",
                "days_to_check": 7,
                "max_videos": 3
            }
        ],
        "download_dir": "downloads",
        "preferred_resolution": "720p",
        "convert_to_mp3": True,
        "keep_video_after_conversion": True
    },
    "wechat": {
        "recipients": [
            # Example recipient configuration
            {
                "name": "Friend Name",
                "is_group": False
            }
        ],
        "cache_path": "wxpy.pkl",
        "send_message_with_video": True,
        "message_template": "New video from {channel}: {title}"
    },
    "telegram": {
        "bot_token": "YOUR_BOT_TOKEN",
        "recipients": [
            # Example recipient configuration
            {
                "chat_id": "CHAT_ID_1",
                "name": "Chat Name"
            }
        ],
        "send_message_with_video": True,
        "message_template": "New video from {channel}: {title}"
    },
    "app": {
        "check_interval_hours": 24,
        "log_level": "INFO",
        "log_file": "youtube_wechat.log"
    }
}

class Config:
    """Configuration handler for the application."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the configuration handler.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file or create default if not exists.
        
        Returns:
            Configuration dictionary
        """
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = yaml.safe_load(f)
                logger.info(f"Configuration loaded from {self.config_path}")
                return config
            except Exception as e:
                logger.error(f"Error loading configuration: {e}")
                logger.info("Using default configuration")
                return DEFAULT_CONFIG
        else:
            logger.info(f"Configuration file not found at {self.config_path}")
            logger.info("Creating default configuration file")
            self._save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG
            
    def _save_config(self, config: Dict[str, Any]) -> bool:
        """
        Save configuration to file.
        
        Args:
            config: Configuration dictionary to save
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            logger.info(f"Configuration saved to {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
            
    def save(self) -> bool:
        """
        Save current configuration to file.
        
        Returns:
            True if saved successfully, False otherwise
        """
        return self._save_config(self.config)
        
    def get_youtube_channels(self) -> List[Dict[str, Any]]:
        """
        Get list of configured YouTube channels.
        
        Returns:
            List of channel configurations
        """
        return self.config.get("youtube", {}).get("channels", [])
        
    def get_wechat_recipients(self) -> List[Dict[str, Any]]:
        """
        Get list of configured WeChat recipients.
        
        Returns:
            List of recipient configurations
        """
        return self.config.get("wechat", {}).get("recipients", [])
        
    def get_telegram_recipients(self) -> List[Dict[str, Any]]:
        """
        Get list of configured Telegram recipients.
        
        Returns:
            List of recipient configurations
        """
        return self.config.get("telegram", {}).get("recipients", [])
        
    def get_telegram_bot_token(self) -> str:
        """
        Get configured Telegram bot token.
        
        Returns:
            Telegram bot token
        """
        return self.config.get("telegram", {}).get("bot_token", "")
        
    def get_download_dir(self) -> str:
        """
        Get configured download directory.
        
        Returns:
            Path to download directory
        """
        return self.config.get("youtube", {}).get("download_dir", "downloads")
        
    def get_preferred_resolution(self) -> str:
        """
        Get configured preferred video resolution.
        
        Returns:
            Preferred resolution (e.g., "720p")
        """
        return self.config.get("youtube", {}).get("preferred_resolution", "720p")
        
    def should_convert_to_mp3(self) -> bool:
        """
        Check if videos should be converted to MP3.
        
        Returns:
            True if videos should be converted to MP3, False otherwise
        """
        return self.config.get("youtube", {}).get("convert_to_mp3", True)
        
    def should_keep_video_after_conversion(self) -> bool:
        """
        Check if videos should be kept after MP3 conversion.
        
        Returns:
            True if videos should be kept, False otherwise
        """
        return self.config.get("youtube", {}).get("keep_video_after_conversion", True)
        
    def get_wechat_cache_path(self) -> str:
        """
        Get configured WeChat cache path.
        
        Returns:
            Path to WeChat cache file
        """
        return self.config.get("wechat", {}).get("cache_path", "wxpy.pkl")
        
    def get_check_interval_hours(self) -> int:
        """
        Get configured check interval in hours.
        
        Returns:
            Check interval in hours
        """
        return self.config.get("app", {}).get("check_interval_hours", 24)
        
    def get_log_level(self) -> str:
        """
        Get configured log level.
        
        Returns:
            Log level (e.g., "INFO")
        """
        return self.config.get("app", {}).get("log_level", "INFO")
        
    def get_log_file(self) -> str:
        """
        Get configured log file path.
        
        Returns:
            Path to log file
        """
        return self.config.get("app", {}).get("log_file", "youtube_wechat.log")
        
    def get_wechat_message_template(self) -> str:
        """
        Get configured WeChat message template.
        
        Returns:
            Message template string
        """
        return self.config.get("wechat", {}).get("message_template", "New video from {channel}: {title}")
        
    def get_telegram_message_template(self) -> str:
        """
        Get configured Telegram message template.
        
        Returns:
            Message template string
        """
        return self.config.get("telegram", {}).get("message_template", "New video from {channel}: {title}")
        
    def should_send_message_with_video(self) -> bool:
        """
        Check if a message should be sent with each video in WeChat.
        
        Returns:
            True if a message should be sent, False otherwise
        """
        return self.config.get("wechat", {}).get("send_message_with_video", True)
        
    def should_send_telegram_message_with_video(self) -> bool:
        """
        Check if a message should be sent with each video in Telegram.
        
        Returns:
            True if a message should be sent, False otherwise
        """
        return self.config.get("telegram", {}).get("send_message_with_video", True)
        
    def add_youtube_channel(self, name: str, url: str, days_to_check: int = 7, max_videos: int = 3) -> bool:
        """
        Add a new YouTube channel to the configuration.
        
        Args:
            name: Name of the channel
            url: URL of the channel
            days_to_check: Number of days to check for new videos
            max_videos: Maximum number of videos to download
            
        Returns:
            True if added successfully, False otherwise
        """
        channel = {
            "name": name,
            "url": url,
            "days_to_check": days_to_check,
            "max_videos": max_videos
        }
        
        if "youtube" not in self.config:
            self.config["youtube"] = {}
            
        if "channels" not in self.config["youtube"]:
            self.config["youtube"]["channels"] = []
            
        # Check if channel already exists
        for existing_channel in self.config["youtube"]["channels"]:
            if existing_channel.get("url") == url:
                logger.warning(f"Channel with URL {url} already exists")
                return False
                
        self.config["youtube"]["channels"].append(channel)
        return self.save()
        
    def add_wechat_recipient(self, name: str, is_group: bool = False) -> bool:
        """
        Add a new WeChat recipient to the configuration.
        
        Args:
            name: Name of the recipient
            is_group: Whether the recipient is a group
            
        Returns:
            True if added successfully, False otherwise
        """
        recipient = {
            "name": name,
            "is_group": is_group
        }
        
        if "wechat" not in self.config:
            self.config["wechat"] = {}
            
        if "recipients" not in self.config["wechat"]:
            self.config["wechat"]["recipients"] = []
            
        # Check if recipient already exists
        for existing_recipient in self.config["wechat"]["recipients"]:
            if existing_recipient.get("name") == name:
                logger.warning(f"Recipient with name {name} already exists")
                return False
                
        self.config["wechat"]["recipients"].append(recipient)
        return self.save()
        
    def add_telegram_recipient(self, chat_id: str, name: str = None) -> bool:
        """
        Add a new Telegram recipient to the configuration.
        
        Args:
            chat_id: Telegram chat ID
            name: Optional name for reference
            
        Returns:
            True if added successfully, False otherwise
        """
        recipient = {
            "chat_id": chat_id
        }
        if name:
            recipient["name"] = name
            
        if "telegram" not in self.config:
            self.config["telegram"] = {}
            
        if "recipients" not in self.config["telegram"]:
            self.config["telegram"]["recipients"] = []
            
        # Check if recipient already exists
        for existing_recipient in self.config["telegram"]["recipients"]:
            if existing_recipient.get("chat_id") == chat_id:
                logger.warning(f"Telegram recipient with chat ID {chat_id} already exists")
                return False
                
        self.config["telegram"]["recipients"].append(recipient)
        return self.save()
