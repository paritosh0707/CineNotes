from cine_notes.components.audio_transcript import HuggingFaceWhisperAPI
from cine_notes.components.video_processor import VideoProcessor
from cine_notes.utils.artifacts_saver import ArtifactsSaver

from cine_notes.logger import logging
from cine_notes.exception import CineNotesException
import sys

from dotenv import load_dotenv
load_dotenv()

try:
    video_processor = VideoProcessor(
        youtube_url="https://www.youtube.com/watch?v=X7iIKPoZ0Sw",
        output_base_dir="./my_videos"
    )
    # video_processor.extract_audio(video_processor.download_video())

    video_processor.download_video()

    response = HuggingFaceWhisperAPI().query(video_processor.extract_audio(),split_time_min=10)
    logging.info(f"Transcription response status: {response['status']}\nlength of transcript: {response['word_count']} words")
    print(f"Transcription response status: {response['status']}\nlength of transcript: {response['word_count']} words")
    
except Exception as e:
    raise CineNotesException(f"Failed to execute the pipeline\nDetailed error:\n{e}", sys)