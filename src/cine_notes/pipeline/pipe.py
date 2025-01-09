from cine_notes.components.audio_transcript import HuggingFaceWhisperAPI
from cine_notes.components.video_processor import VideoProcessor
from cine_notes.utils.artifacts_saver import ArtifactsSaver

from cine_notes.logger import logging
from cine_notes.exception import CineNotesException
import sys

try:
    video_processor = VideoProcessor(
        youtube_url="https://www.youtube.com/watch?v=qhomKbL-mHw",
        output_base_dir="./my_videos"
    )
    # video_processor.extract_audio(video_processor.download_video())

    video_processor.download_video()

    response = HuggingFaceWhisperAPI().query(video_processor.extract_audio())
    artifacts_saver = ArtifactsSaver()
    artifacts_saver.save_json(response, "response.json")
    logging.info(f"Response saved to json file: {artifacts_saver.get_run_dir}")

except Exception as e:
    raise CineNotesException(f"Failed to execute the pipeline\nDetailed error:\n{e}", sys)