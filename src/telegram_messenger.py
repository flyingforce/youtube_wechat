"""Module for sending messages and files through Telegram."""

import os
import logging
from typing import List, Optional
import telegram
from telegram import Bot
from telegram.error import TelegramError

class TelegramMessenger:
    """Class to handle sending messages and files through Telegram."""
    
    def __init__(self, token: str):
        """
        Initialize the Telegram messenger.
        
        Args:
            token: Telegram bot token
        """
        self.token = token
        self.bot = None
        self.logger = logging.getLogger(__name__)
        
    def login(self) -> bool:
        """
        Log in to Telegram using the bot token.
        
        Returns:
            True if login successful, False otherwise
        """
        try:
            self.bot = Bot(token=self.token)
            self.logger.info("Telegram login successful")
            return True
        except TelegramError as e:
            self.logger.error(f"Telegram login failed: {str(e)}")
            return False
            
    def send_message(self, chat_id: str, message: str) -> bool:
        """
        Send a text message to a chat.
        
        Args:
            chat_id: ID of the chat to send message to
            message: Message text to send
            
        Returns:
            True if message sent successfully, False otherwise
        """
        try:
            if not self.bot:
                self.logger.error("Telegram bot not initialized")
                return False
            
            self.bot.send_message(chat_id=chat_id, text=message)
            self.logger.info(f"Message sent to chat {chat_id}")
            return True
        except TelegramError as e:
            self.logger.error(f"Failed to send message to chat {chat_id}: {str(e)}")
            return False
            
    def send_file(self, chat_id: str, file_path: str) -> bool:
        """
        Send a file to a chat.
        
        Args:
            chat_id: ID of the chat to send file to
            file_path: Path to the file to send
            
        Returns:
            True if file sent successfully, False otherwise
        """
        try:
            if not self.bot:
                self.logger.error("Telegram bot not initialized")
                return False
            
            with open(file_path, 'rb') as file:
                self.bot.send_document(chat_id=chat_id, document=file)
            self.logger.info(f"File sent to chat {chat_id}: {file_path}")
            return True
        except FileNotFoundError:
            self.logger.error(f"File not found: {file_path}")
            return False
        except TelegramError as e:
            self.logger.error(f"Failed to send file to chat {chat_id}: {str(e)}")
            return False
            
    def send_video(self, chat_id: str, video_path: str) -> bool:
        """
        Send a video to a chat.
        
        Args:
            chat_id: ID of the chat to send video to
            video_path: Path to the video file to send
            
        Returns:
            True if video sent successfully, False otherwise
        """
        try:
            if not self.bot:
                self.logger.error("Telegram bot not initialized")
                return False
            
            with open(video_path, 'rb') as video:
                self.bot.send_video(chat_id=chat_id, video=video)
            self.logger.info(f"Video sent to chat {chat_id}: {video_path}")
            return True
        except FileNotFoundError:
            self.logger.error(f"Video file not found: {video_path}")
            return False
        except TelegramError as e:
            self.logger.error(f"Failed to send video to chat {chat_id}: {str(e)}")
            return False
            
    def send_videos(self, chat_id: str, video_paths: List[str]) -> List[str]:
        """
        Send multiple videos to a chat.
        
        Args:
            chat_id: ID of the chat to send videos to
            video_paths: List of paths to video files
            
        Returns:
            List of paths of successfully sent videos
        """
        successful_sends = []
        
        for video_path in video_paths:
            if self.send_video(chat_id, video_path):
                successful_sends.append(video_path)
                
        return successful_sends 