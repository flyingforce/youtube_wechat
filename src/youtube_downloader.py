"""Module for downloading YouTube videos from channels."""

import os
import sys
import logging
import requests
import subprocess
import concurrent.futures
from typing import List, Dict, Optional, Tuple, Set
from datetime import datetime, timedelta, date
import scrapetube


# Fix for ModuleNotFoundError: No module named 'moviepy.editor'
try:
    from moviepy.editor import VideoFileClip
except ImportError:
    # Try alternative import path
    try:
        from moviepy.video.io.VideoFileClip import VideoFileClip
    except ImportError:
        # Define a placeholder for VideoFileClip if moviepy is not installed
        class VideoFileClip:
            def __init__(self, *args, **kwargs):
                raise ImportError("moviepy is not installed. Please install it with 'pip install moviepy'")

# Configure logger
logger = logging.getLogger(__name__)

class YouTubeDownloader:
    """Class to handle downloading videos from YouTube channels."""
    
    def __init__(self, download_dir: str = "downloads", convert_to_mp3: bool = True, max_workers: int = 4):
        """
        Initialize the YouTube downloader.
        
        Args:
            download_dir: Directory to save downloaded videos
            convert_to_mp3: Whether to convert videos to MP3 format
            max_workers: Maximum number of worker threads for parallel downloads
        """
        self.download_dir = download_dir
        self.convert_to_mp3 = convert_to_mp3
        self.max_workers = max_workers
        os.makedirs(download_dir, exist_ok=True)
        
        # Path to the downloaded titles file
        self.downloaded_titles_file = os.path.join(download_dir, "downloaded_titles.txt")
        
        # Load previously downloaded titles
        self.downloaded_titles = self._load_downloaded_titles()
        
        logger.info(f"Loaded {len(self.downloaded_titles)} previously downloaded titles")
    
    def _load_downloaded_titles(self) -> Set[str]:
        """
        Load the list of previously downloaded video titles.
        
        Returns:
            Set of downloaded video titles
        """
        downloaded_titles = set()
        
        if os.path.exists(self.downloaded_titles_file):
            try:
                with open(self.downloaded_titles_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        title = line.strip()
                        if title:
                            downloaded_titles.add(title)
                logger.info(f"Loaded downloaded titles from {self.downloaded_titles_file}")
            except Exception as e:
                logger.error(f"Error loading downloaded titles: {e}")
        
        return downloaded_titles
    
    def _save_downloaded_title(self, title: str) -> None:
        """
        Save a downloaded video title to the downloaded titles file.
        
        Args:
            title: Video title to save
        """
        if not title:
            return
            
        try:
            with open(self.downloaded_titles_file, 'a', encoding='utf-8') as f:
                f.write(f"{title}\n")
            self.downloaded_titles.add(title)
            logger.info(f"Saved title to downloaded titles file: {title}")
        except Exception as e:
            logger.error(f"Error saving downloaded title: {e}")
        
    def get_channel_videos(self, channel_url: str, limit: int = 5) -> List[Dict]:
        """
        Get recent videos from a YouTube channel.
        
        Args:
            channel_url: URL of the YouTube channel
            limit: Maximum number of videos to retrieve
            
        Returns:
            List of video information dictionaries
        """


        logger.info(f"Fetching videos from channel: {channel_url}")
        try:
            videoIds = scrapetube.get_channel(channel_url=channel_url,limit = limit,sort_by="newest")
            videos = []
            
            for video in videoIds:
                url = "https://www.youtube.com/watch?v="+video['videoId']
                
                # Extract title from the title object
                title = "Unknown"
                if 'title' in video and 'runs' in video['title'] and len(video['title']['runs']) > 0:
                    if 'text' in video['title']['runs'][0]:
                        title = video['title']['runs'][0]['text']
                    else:
                        title = str(video['title']['runs'])
                
                logger.info(f"Found video: {title} (ID: {video['videoId']}) (line {sys._getframe().f_lineno})")
                
                # Skip upcoming videos
                if 'upcomingEventData' in video and video['upcomingEventData']:
                    logger.info(f"Skipping upcoming video: {title} (line {sys._getframe().f_lineno})")
                    continue
                
                # Try to get publish date if available
                publish_date = None
                if 'publishedTimeText' in video and 'simpleText' in video['publishedTimeText']:
                    publish_date_text = video['publishedTimeText']['simpleText']
                    logger.info(f"Video published: {publish_date_text} (line {sys._getframe().f_lineno})")
                    # For simplicity, we'll just use current timestamp
                    if "month" in publish_date_text or "week" in publish_date_text:
                        logger.info(f"ignore the file {title} as it is too old")
                        continue
                    else:
                        # For simplicity, we'll just use current timestamp if the condition is not met
                        publish_date = datetime.now().timestamp()
                                
                # Check if this video has already been downloaded
                if title in self.downloaded_titles:
                    logger.info(f"Skipping video {title} - already downloaded (line {sys._getframe().f_lineno})")
                    continue
                
                video_info = {
                    "title": title,
                    "url": url,
                    "video_id": video['videoId'],
                    "publish_date": publish_date
                }
                
                logger.info(f"Adding video to download list: {title} (line {sys._getframe().f_lineno})")
                videos.append(video_info)
                
            return videos
        except Exception as e:
            logger.error(f"Error fetching channel videos: {e}")
            return []
    
    def download_video_direct(self, video_id: str, title: str = "Unknown") -> Optional[Tuple[str, Optional[str]]]:
        """
        Download a YouTube video directly using the video ID.
        If convert_to_mp3 is enabled, only download audio to save bandwidth.
        
        Args:
            video_id: YouTube video ID
            title: Video title for the filename
            
        Returns:
            Tuple containing (video_path, mp3_path) or (video_path, None) if MP3 conversion is disabled
            or None if download failed
        """
        try:
            # Create a subdirectory for videos/audio
            channel_dir = os.path.join(self.download_dir, date.today().strftime("%Y%m%d"))
            os.makedirs(channel_dir, exist_ok=True)
            
            # Clean the title to use as filename
            safe_title = "".join([c if c.isalnum() or c in " -_" else "_" for c in title])
            safe_title = safe_title.strip()
            if not safe_title:
                safe_title = video_id
            
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            
            # If MP3 conversion is enabled, download audio only
            if self.convert_to_mp3:
                # Path for the audio file
                mp3_path = os.path.join(channel_dir, f"{safe_title}.mp3")
                
                logger.info(f"Downloading audio only for title: {title} video ID: {video_id} (audio-only mode)")
                
                try:
                    # Use yt-dlp to download audio directly in MP3 format
                    cmd = [
                        "yt-dlp",
                        "-f", "bestaudio",  # Get best audio
                        "-x",  # Extract audio
                        "--audio-format", "mp3",  # Convert to MP3
                        "--audio-quality", "0",  # Best quality
                        "-o", mp3_path,  # Output filename
                        youtube_url  # URL to download
                    ]
                    
                    subprocess.run(cmd, check=True, capture_output=True)
                    logger.info(f"Audio downloaded directly to MP3: {mp3_path} (using yt-dlp)")
                    
                    # Since we already have the MP3, we'll create a dummy video path
                    # This is just to maintain compatibility with the rest of the code
                    video_path = mp3_path.replace(".mp3", ".mp4_dummy")
                    
                    # Save the title to the downloaded titles file
                    self._save_downloaded_title(title)
                    
                    return (video_path, mp3_path)
                    
                except (subprocess.SubprocessError, FileNotFoundError) as e:
                    logger.warning(f"yt-dlp audio download failed: {e}, falling back to video download (line {sys._getframe().f_lineno})")
                    # Fall back to video download if audio-only fails
            
            # If MP3 conversion is disabled or audio-only download failed, download video
            video_path = os.path.join(channel_dir, f"{safe_title}_{video_id}.mp4")
            
            logger.info(f"Downloading video ID: {video_id} (video mode)")
            
            try:
                # Try using yt-dlp command line tool
                cmd = [
                    "yt-dlp",
                    "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",  # Format selection
                    "-o", video_path,  # Output filename
                    youtube_url  # URL to download
                ]
                
                subprocess.run(cmd, check=True, capture_output=True)
                logger.info(f"Video downloaded to: {video_path} using yt-dlp (line {sys._getframe().f_lineno})")
                
                # Save the title to the downloaded titles file
                self._save_downloaded_title(title)
                
            except (subprocess.SubprocessError, FileNotFoundError) as e:
                logger.warning(f"yt-dlp download failed: {e}, trying alternative method (line {sys._getframe().f_lineno})")
                
                # Alternative method: Use a direct download service API
                # This is a placeholder - in a real implementation, you would need to use a service
                # that provides direct download URLs or implement a more sophisticated method
                direct_url = f"https://www.youtube.com/watch?v={video_id}"
                
                response = requests.get(direct_url, stream=True)
                response.raise_for_status()
                
                with open(video_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            
                logger.info(f"Video downloaded to: {video_path} using direct download (line {sys._getframe().f_lineno})")
                
                # Save the title to the downloaded titles file
                self._save_downloaded_title(title)
            
            # Convert to MP3 if enabled (and we didn't already download as MP3)
            mp3_path = None
            if self.convert_to_mp3:
                mp3_path = self.convert_video_to_mp3(video_path)
                
            return (video_path, mp3_path)
            
        except Exception as e:
            logger.error(f"Error downloading video directly: {e}")
            return None
    
    def download_video(self, video_url: str, video_title: str, resolution: str = "720p") -> Optional[Tuple[str, Optional[str]]]:
        """
        Download a YouTube video and optionally convert to MP3.
        
        Args:
            video_url: URL of the YouTube video
            resolution: Preferred video resolution
            
        Returns:
            Tuple containing (video_path, mp3_path) or (video_path, None) if MP3 conversion is disabled
            or None if download failed
        """
        try:
            # Extract video ID from URL
            # Format: https://www.youtube.com/watch?v=VIDEO_ID
            video_id = video_url.split("v=")[-1]
            if "&" in video_id:
                video_id = video_id.split("&")[0]
                
            logger.info(f"Extracted video ID: {video_id}")
        
            # Download the video directly using the ID
            return self.download_video_direct(video_id, video_title)
            
        except Exception as e:
            logger.error(f"Error downloading video: {e}")
            return None
    
    def convert_video_to_mp3(self, video_path: str) -> Optional[str]:
        """
        Convert a video file to MP3 format.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Path to the MP3 file or None if conversion failed
        """
        try:
            # Get the output path by replacing the extension with .mp3
            mp3_path = os.path.splitext(video_path)[0] + '.mp3'
            
            logger.info(f"Converting video to MP3: {video_path}")
            
            # Convert video to MP3
            video_clip = VideoFileClip(video_path)
            audio_clip = video_clip.audio
            audio_clip.write_audiofile(mp3_path)
            
            # Close the clips to release resources
            audio_clip.close()
            video_clip.close()
            
            logger.info(f"MP3 conversion complete: {mp3_path}")
            return mp3_path
        except Exception as e:
            logger.error(f"Error converting video to MP3: {e}")
            return None
    
    def download_recent_videos(self, channel_url: str, days: int = 7, limit: int = 5) -> List[Tuple[str, Optional[str]]]:
        """
        Download recent videos from a channel and optionally convert to MP3 using multiple threads.
        
        Args:
            channel_url: URL of the YouTube channel
            days: Only download videos published within this many days
            limit: Maximum number of videos to download
            
        Returns:
            List of tuples containing (video_path, mp3_path) for each downloaded video
        """
        videos = self.get_channel_videos(channel_url, limit=limit)
        downloaded_files = []
        
        cutoff_date = datetime.now() - timedelta(days=days)
        timestamp = cutoff_date.timestamp()
        logger.info(f"Cutoff date: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')} (timestamp: {timestamp}) (line {sys._getframe().f_lineno})")
        
        # Filter videos by date
        videos_to_download = []
        for video in videos:
            # Skip videos older than the cutoff date
            if video["publish_date"] and video["publish_date"] < cutoff_date.timestamp():
                logger.info(f"Skipping video {video['title']} - too old (line {sys._getframe().f_lineno})")
                continue
            videos_to_download.append(video)
        
        if not videos_to_download:
            logger.info(f"No videos to download from channel (line {sys._getframe().f_lineno})")
            return []
            
        logger.info(f"Downloading {len(videos_to_download)} videos using {self.max_workers} threads (line {sys._getframe().f_lineno})")
        
        # Use ThreadPoolExecutor to download videos in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit download tasks
            future_to_video = {
                executor.submit(self.download_video, video["url"], video["title"]): video
                for video in videos_to_download
            }
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_video):
                video = future_to_video[future]
                try:
                    result = future.result()
                    if result:
                        logger.info(f"Successfully downloaded video: {video['title']} (line {sys._getframe().f_lineno})")
                        downloaded_files.append(result)
                    else:
                        logger.warning(f"Failed to download video: {video['title']} (line {sys._getframe().f_lineno})")
                except Exception as e:
                    logger.error(f"Error downloading video {video['title']}: {e} (line {sys._getframe().f_lineno})")
        
        logger.info(f"Downloaded {len(downloaded_files)} videos in total (line {sys._getframe().f_lineno})")
        return downloaded_files
