"""Module for sending messages and files through WeChat."""

import os
import logging
from typing import List, Optional
from wxpy import Bot, Friend, Group, ATTACHMENT

logger = logging.getLogger(__name__)

class WeChatMessenger:
    """Class to handle sending messages and files through WeChat."""
    
    def __init__(self, cache_path: str = "wxpy.pkl"):
        """
        Initialize the WeChat messenger.
        
        Args:
            cache_path: Path to save the login session cache
        """
        self.bot = None
        self.cache_path = cache_path
        
    def login(self) -> bool:
        """
        Log in to WeChat by scanning QR code.
        
        Returns:
            True if login successful, False otherwise
        """
        try:
            # Enable caching to avoid scanning QR code every time
            self.bot = Bot(cache_path=self.cache_path)
            logger.info("Successfully logged in to WeChat")
            return True
        except Exception as e:
            logger.error(f"Failed to log in to WeChat: {e}")
            return False
            
    def find_friend(self, name: str) -> Optional[Friend]:
        """
        Find a friend by name.
        
        Args:
            name: Name of the friend to find
            
        Returns:
            Friend object if found, None otherwise
        """
        if not self.bot:
            logger.error("Not logged in to WeChat")
            return None
            
        try:
            friends = self.bot.friends().search(name)
            if friends:
                return friends[0]
            else:
                logger.warning(f"Friend '{name}' not found")
                return None
        except Exception as e:
            logger.error(f"Error finding friend: {e}")
            return None
            
    def find_group(self, name: str) -> Optional[Group]:
        """
        Find a group by name.
        
        Args:
            name: Name of the group to find
            
        Returns:
            Group object if found, None otherwise
        """
        if not self.bot:
            logger.error("Not logged in to WeChat")
            return None
            
        try:
            groups = self.bot.groups().search(name)
            if groups:
                return groups[0]
            else:
                logger.warning(f"Group '{name}' not found")
                return None
        except Exception as e:
            logger.error(f"Error finding group: {e}")
            return None
            
    def send_message(self, recipient_name: str, message: str, is_group: bool = False) -> bool:
        """
        Send a text message to a friend or group.
        
        Args:
            recipient_name: Name of the recipient (friend or group)
            message: Message text to send
            is_group: Whether the recipient is a group
            
        Returns:
            True if message sent successfully, False otherwise
        """
        if not self.bot:
            logger.error("Not logged in to WeChat")
            return False
            
        try:
            recipient = self.find_group(recipient_name) if is_group else self.find_friend(recipient_name)
            
            if not recipient:
                return False
                
            recipient.send(message)
            logger.info(f"Message sent to {recipient_name}")
            return True
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
            
    def send_file(self, recipient_name: str, file_path: str, is_group: bool = False) -> bool:
        """
        Send a file to a friend or group.
        
        Args:
            recipient_name: Name of the recipient (friend or group)
            file_path: Path to the file to send
            is_group: Whether the recipient is a group
            
        Returns:
            True if file sent successfully, False otherwise
        """
        if not self.bot:
            logger.error("Not logged in to WeChat")
            return False
            
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False
            
        try:
            recipient = self.find_group(recipient_name) if is_group else self.find_friend(recipient_name)
            
            if not recipient:
                return False
                
            recipient.send_file(file_path)
            logger.info(f"File sent to {recipient_name}: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error sending file: {e}")
            return False
            
    def send_video(self, recipient_name: str, video_path: str, is_group: bool = False) -> bool:
        """
        Send a video to a friend or group.
        
        Args:
            recipient_name: Name of the recipient (friend or group)
            video_path: Path to the video file to send
            is_group: Whether the recipient is a group
            
        Returns:
            True if video sent successfully, False otherwise
        """
        # This is essentially the same as send_file, but we're creating a separate
        # method for clarity and potential future enhancements specific to videos
        return self.send_file(recipient_name, video_path, is_group)
        
    def send_videos(self, recipient_name: str, video_paths: List[str], is_group: bool = False) -> List[str]:
        """
        Send multiple videos to a friend or group.
        
        Args:
            recipient_name: Name of the recipient (friend or group)
            video_paths: List of paths to video files
            is_group: Whether the recipient is a group
            
        Returns:
            List of paths of successfully sent videos
        """
        successful_sends = []
        
        for video_path in video_paths:
            if self.send_video(recipient_name, video_path, is_group):
                successful_sends.append(video_path)
                
        return successful_sends
        
    def logout(self):
        """Log out from WeChat."""
        if self.bot:
            self.bot.logout()
            logger.info("Logged out from WeChat")
            self.bot = None
