try:
    import os
    import subprocess
    from moviepy.video.io.VideoFileClip import VideoFileClip
    import sys
    from cine_notes.logger import logging
    from cine_notes.exception import CineNotesException
    import json
    from cine_notes.utils.artifacts_saver import ArtifactsSaver
except ImportError as e:
    print(f"Error importing module: {e}")
    sys.exit(1)

class VideoProcessor:
    """
    A class to process YouTube videos by downloading and extracting audio/frames.

    This class provides functionality to:
    - Download YouTube videos at highest available quality
    - Extract audio in WAV format
    - Extract video frames as images
    - Organize outputs in a structured directory format

    Attributes:
        youtube_url (str): URL of the YouTube video to process
        output_base_dir (str): Base directory for all outputs
        video_filename (str): Path to downloaded video file
        video_dir (str): Directory containing the video
        audio_dir (str): Directory for extracted audio
        frames_dir (str): Directory for extracted frames

    Methods:
        __init__(youtube_url: str, output_base_dir: str = "./output_videos") -> None: Initialize the processor.
        download_video() -> str: Download the YouTube video.
        extract_audio(audio_filename: str = "audio.mp3") -> str: Extract audio from the video.
        extract_frames(image_prefix: str = "frame_", image_format: str = "jpg") -> str: Extract frames from the video.
        _sanitize_filename(name: str) -> str: Sanitize the filename.
    """

    def __init__(self, youtube_url: str, output_base_dir: str = "./output_videos")->None:
        """
        Initialize the VideoProcessor.

        Args:
            youtube_url (str): URL of the YouTube video to process
            output_base_dir (str): Base directory for outputs (default: "./output_videos")
        """
        try:
            self.youtube_url = youtube_url
            self.output_base_dir = os.path.abspath(output_base_dir)
            os.makedirs(self.output_base_dir, exist_ok=True)
            logging.info(f"Initialized VideoProcessor with output directory: {self.output_base_dir}")
            
            # Initialize placeholder paths
            self.video_filename = None
            self.video_dir = None
            self.audio_dir = None
            self.frames_dir = None

            # Initialize ArtifactsSaver
            self.artifacts_saver = ArtifactsSaver()
        except Exception as e:
            raise CineNotesException(f"Failed to initialize VideoProcessor\nDetailed Exception :\n{e}", sys)

    def download_video(self) -> str:
        """
        Download the YouTube video using yt-dlp. This method fetches the video's metadata first, creates directories based on the video's title, and then downloads the video.

        Returns:
            str: Path to the downloaded video file

        Raises:
            CineNotesException: If video download or directory creation fails
        """
        try:
            logging.info(f"Starting download for video: {self.youtube_url}")
            
            # Fetch metadata as JSON
            cmd = [
                "yt-dlp",
                "--dump-single-json",
                "-f", "mp4",
                self.youtube_url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            metadata = json.loads(result.stdout)
            logging.info("Fetched video metadata successfully")
            
            # Save metadata
            self.artifacts_saver.save_json("metadata.json", metadata)
            
            # Extract video title and sanitize it
            video_title = self._sanitize_filename(metadata.get("title", "video"))
            logging.info(f"Sanitized video title: {video_title}")
            
            self.video_dir = os.path.join(self.output_base_dir, video_title)
            os.makedirs(self.video_dir, exist_ok=True)
            logging.info(f"Created video directory: {self.video_dir}")
            
            # Now download the video file to the specified directory
            # We'll specify the output template to ensure the file is named "video.mp4"
            download_cmd = [
                "yt-dlp",
                "-f", "mp4",
                "-o", os.path.join(self.video_dir, "video.%(ext)s"),
                self.youtube_url
            ]
            subprocess.run(download_cmd, check=True)
            logging.info("Video downloaded successfully")
            
            # After download, set the video filename
            self.video_filename = os.path.join(self.video_dir, "video.mp4")
            
            # Prepare directories for audio and frames
            self.audio_dir = os.path.join(self.video_dir, "audio")
            self.frames_dir = os.path.join(self.video_dir, "frames")
            os.makedirs(self.audio_dir, exist_ok=True)
            os.makedirs(self.frames_dir, exist_ok=True)
            logging.info(f"Prepared directories for audio and frames: {self.audio_dir}, {self.frames_dir}")
            
            return self.video_filename
        except Exception as e:
            raise CineNotesException(f"Failed to download video\nDetailed Exception :\n{e}", sys)

    def extract_audio(self, audio_filename:str="audio.mp3")->str:
        """
        Extract audio from the downloaded video using ffmpeg.

        Args:
            audio_filename (str): Name for the output audio file (default: "audio.wav")

        Returns:
            str: Path to the extracted audio file

        Raises:
            ValueError: If no video has been downloaded
            CineNotesException: If audio extraction fails
        """
        try:
            self.audio_path = os.path.join(self.audio_dir, audio_filename)
            video_clip = VideoFileClip(self.video_filename)
            audio_clip = video_clip.audio
            audio_clip.write_audiofile(self.audio_path)
            audio_clip.close()
            video_clip.close()
            logging.info(f"Converted {self.video_filename} to {self.audio_path}")
            
            # Save audio path
            # self.artifacts_saver.save_artifact("audio_path.txt", self.audio_path)
            
            return self.audio_path
        except Exception as e:
            raise CineNotesException(f"Failed to convert MP4 to MP3\nDetailed Exception :\n{e}", sys)

    def extract_frames(self, image_prefix="frame_", image_format="jpg")->str:
        """
        Extract frames from the video using ffmpeg.

        Args:
            image_prefix (str): Prefix for frame filenames (default: "frame_")
            image_format (str): Format for frame images (default: "jpg")

        Returns:
            str: Path to the directory containing extracted frames

        Raises:
            ValueError: If no video has been downloaded
            CineNotesException: If frame extraction fails
        """
        try:
            if not self.video_filename:
                raise ValueError("No video has been downloaded. Call download_video() first.")
            
            logging.info(f"Extracting frames to: {self.frames_dir}")
            frame_pattern = os.path.join(self.frames_dir, f"{image_prefix}%05d.{image_format}")
            
            cmd = [
                "ffmpeg",
                "-i", self.video_filename,
                frame_pattern,
                "-y"
            ]
            
            subprocess.run(cmd, check=True)
            logging.info("Frame extraction completed successfully")
            
            # Save frames directory
            # self.artifacts_saver.save_artifact("frames_dir.txt", self.frames_dir)
            
            return self.frames_dir
        except ValueError as ve:
            raise ve
        except Exception as e:
            raise CineNotesException(f"Failed to extract frames\nDetailed Exception :\n{e}", sys)

    @staticmethod
    def _sanitize_filename(name: str) -> str:
        """
        Sanitize filename by removing/escaping invalid filename characters.

        Args:
            name (str): Original filename

        Returns:
            str: Sanitized filename
        """
        return "".join(c for c in name if c.isalnum() or c in (' ', '.', '_', '-')).strip()

# Example usage:
if __name__ == "__main__":
    youtube_url = "https://www.youtube.com/watch?v=qhomKbL-mHw"
    processor = VideoProcessor(youtube_url, output_base_dir="./my_videos")
    processor.download_video()
    processor.extract_audio()
    # processor.extract_frames()
    print("Video processing complete!")
