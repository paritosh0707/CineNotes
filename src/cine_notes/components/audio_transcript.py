import requests
import os

from cine_notes.logger import logging
from cine_notes.exception import CineNotesException
from cine_notes.utils.artifacts_saver import ArtifactsSaver 

import sys
from typing import Dict, Any, List, Tuple, Union
 
from pydub import AudioSegment
from pydub.utils import make_chunks

from tempfile import mkdtemp

import asyncio
import aiohttp

class APIClient:
    """
    A class to handle API requests.

    Attributes:
        api_url (str): The URL endpoint for the API.
        headers (dict): The headers to include in the API requests.

    Methods:
        __init__(api_url: str, headers: dict) -> None:
            Initializes the APIClient with the given URL and headers.
        send_request(session: aiohttp.ClientSession, data: dict) -> dict:
            Sends a POST request with the given payload and returns the response.
        execute_requests(payloads: List[dict]) -> List[dict]:
            Executes multiple POST requests in parallel and returns the responses.
    """
    def __init__(self, api_url, headers):
        self.api_url = api_url
        self.headers = headers

    async def send_request(self, session, data):
        """Send a POST request with the given payload."""
        try:
            async with session.post(self.api_url, headers=self.headers, data=data) as response:
                response.raise_for_status()
                result = await response.json()
                return {"status": response.status, "data": result}
        except aiohttp.ClientError as e:
            return {"error": str(e)}

    async def execute_requests(self, payloads):
        """Execute multiple POST requests in parallel."""
        async with aiohttp.ClientSession() as session:
            tasks = [self.send_request(session, payload) for payload in payloads]
            return await asyncio.gather(*tasks)

class HuggingFaceWhisperAPI:
    """
    A class to interact with the Hugging Face Whisper API for audio transcription.
    Attributes:
        api_key (str): The API key for authenticating with the Hugging Face API.
        api_url (str): The URL endpoint for the Hugging Face API.
        headers (dict): The headers to include in the API requests.
    """

    def __init__(self, api_key: str = '' , model_name: str = "openai/whisper-large-v3-turbo") -> None:
        """
        Initializes the HuggingFaceWhisperAPI class with the specified model name.

        Args:
            api_key (str): The API key for Hugging Face authentication.
            model_name (str): The name of the model to use for transcription.
        """
        try:
            self.api_key = api_key or os.getenv("HUGGINGFACE_WHISPER_TOKEN")
            if not self.api_key:
                logging.error("HUGGINGFACE_WHISPER_TOKEN not found in environment variables.")
                raise ValueError("HUGGINGFACE_WHISPER_TOKEN not found in environment variables.")
            self.api_url = f"https://api-inference.huggingface.co/models/{model_name}"
            self.headers = {"Authorization": f"Bearer {self.api_key}"}
            logging.info(f"Initialized HuggingFaceWhisperAPI with model {model_name}")
        except Exception as e:
            raise CineNotesException(f"Failed to initialize HuggingFaceWhisperAPI\nDetailed Exception :\n{e}", sys)

    def query(self, filename: str, **kwargs) -> Dict[str, Any]:
        """
        Processes an audio file, sends it for transcription, and saves the output to a specified file.

        Args:
            filename (str): Path to the audio file to process.
            
            **kwargs: Optional parameters for customization:

                output_file (str): Base name for the output file (default is "output"). The extension is automatically added.
                file_type (str): Type of the output file ("text", "json", or "binary"). Default is "json".
                split_time_min (int): Duration in minutes to split the audio into chunks (default is 5 minutes).

        Returns:
            Dict[str, Any]: A dictionary containing the transcription results, including combined text and any errors.

        Raises:
            CineNotesException: If any errors occur during processing, transcription, or file saving.
        """
        logging.info(f"Querying Hugging Face API with file {filename}")
        temp_dir = None  # Initialize to ensure it can be cleaned up later

        try:
            # Load the audio file
            audio = AudioSegment.from_file(filename)
            logging.info(f"Successfully read audio file: {filename}")

            # Split the audio into chunks
            split_time_min = kwargs.get("split_time_min", 5)
            chunks_dir_list, temp_dir = self._spilt_audio_into_chunks(audio=audio, split_time_min=split_time_min)
            logging.info(f"Audio file split into {len(chunks_dir_list)} chunks of {split_time_min} minutes each")

            # Send the audio chunks to the API asynchronously
            logging.info("Sending audio chunks to Hugging Face API")
            loop = asyncio.get_event_loop()
            task = loop.create_task(self._excecute_api_requests(chunks_dir_list))
            responses = loop.run_until_complete(task)

            # Combine responses
            combined_response = self._combine_responses(responses)
            logging.info("Successfully processed all audio chunks")

            # Save the output to a file
            file_name = kwargs.get("output_file", "output")
            file_type = kwargs.get("file_type", "json")  # Default to JSON if file_type is not provided
            self._save_output(combined_response, file_name=file_name, file_type=file_type)
            logging.info(f"Query completed successfully. Output saved to {file_name}")
            return combined_response
        except FileNotFoundError:
            logging.error(f"File {filename} not found.")
            raise FileNotFoundError(f"File {filename} not found.")
        except asyncio.exceptions.InvalidStateError as e:
            logging.error(f"Error with asynchronous execution: {e}")
            raise RuntimeError(f"Asynchronous execution failed: {e}")
        except Exception as e:
            logging.error(f"Error querying Hugging Face API: {e}")
            raise CineNotesException(f"Failed to query Hugging Face API\nDetailed Exception:\n{e}", sys)
        finally:
            # Ensure temporary directory is cleaned up
            if temp_dir and os.path.exists(temp_dir):
                try:
                    import shutil
                    shutil.rmtree(temp_dir)
                    logging.info(f"Temporary directory {temp_dir} successfully removed.")
                except Exception as cleanup_error:
                    logging.warning(f"Failed to remove temporary directory {temp_dir}: {cleanup_error}")
    
    def _spilt_audio_into_chunks(self, audio: AudioSegment, split_time_min: int = 5) -> Tuple[List[str], str]:
        """
        Split the audio data into chunks of specified duration.

        Args:
            audio (AudioSegment): The audio data to split.
            split_time_min (int): The time duration in minutes to split the audio. Defaults to 5 minutes.

        Returns:
            Tuple[List[str], str]: A tuple containing:
                - List of paths to the audio chunk files.
                - Path to the temporary directory containing the chunks.

        Raises:
            CineNotesException: If there is an issue with audio splitting, file export, or invalid input.
        """
        try:
            if not audio or len(audio) == 0:
                logging.error("Audio data is empty. Cannot split into chunks.")
                raise CineNotesException("Audio data is empty. Ensure a valid audio file is provided.")

            if split_time_min <= 0:
                logging.error("Invalid split time. It must be greater than 0.")
                raise CineNotesException("Invalid split time. Must be a positive integer greater than 0.")

            chunk_size_ms = split_time_min * 60 * 1000
            # Split the audio into chunks
            chunks = make_chunks(audio, chunk_size_ms)
            logging.info(f"Audio split into {len(chunks)} chunks of {split_time_min} minutes each.")

            # Create a temporary directory to save chunks
            temp_dir = mkdtemp()
            audio_dir = os.path.join(temp_dir, "audio")
            os.makedirs(audio_dir, exist_ok=True)

            chunks_dir_list = []
            # Export chunks as separate files
            for i, chunk in enumerate(chunks):
                chunk_name = os.path.join(audio_dir, f"chunk{i}.mp3")
                chunk.export(chunk_name, format="mp3")
                chunks_dir_list.append(chunk_name)
                logging.debug(f"Exported chunk: {chunk_name}")

            logging.info(f"Successfully split and saved {len(chunks)} audio chunks.")
            return chunks_dir_list, temp_dir

        except CineNotesException:
            # Re-raise CineNotesException to preserve context
            raise
        except Exception as e:
            logging.error(f"Failed to split audio into chunks: {e}")
            raise CineNotesException(f"Error during audio splitting or chunk export: {e}")
    
    async def _excecute_api_requests(self, chunks_dir_list: List[str]) -> List[Dict[str, Any]]:
        """
        Execute API requests in parallel.

        Args:
            chunks_dir_list (List[str]): List of paths to the audio chunk files.

        Returns:
            List[Dict[str, Any]]: List of responses from the API.
        """
        api_client = APIClient(self.api_url, self.headers)
        payloads = [{"inputs": open(chunk, "rb").read()} for chunk in chunks_dir_list]
        responses = await api_client.execute_requests(payloads)
        return responses
    
    def _combine_responses(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Combines API responses from multiple transcripts into a single structured dictionary.

        Args:
            responses (List[Dict[str, Any]]): List of API responses.

        Returns:
            dict: Combined response including all transcripts.
        """
        combined_output = {
            "status": "success",
            "transcripts": [],
            "error_logs": [],
            "word_count": 0,
            "combined_text": ""
        }

        for response in responses:
            if "error" in response:
                # Log errors separately for review
                combined_output["error_logs"].append(response["error"])
            elif "data" in response and "text" in response["data"]:
                # Append the text to the combined transcript
                transcript = response["data"]["text"]
                combined_output["transcripts"].append(transcript)
                combined_output["combined_text"] += f" {transcript}"
            else:
                # Handle unexpected data format
                combined_output["error_logs"].append("Unexpected response format.")

        # Calculate the total word count
        combined_output["word_count"] = len(combined_output["combined_text"].split())

        if combined_output["error_logs"]:
            combined_output["status"] = "partial_success"
            logging.warning(f"Some errors occurred during transcription: {combined_output['error_logs']}")
        else:
            logging.info("All transcripts successfully combined without errors.")

        return combined_output

    

    def _save_output(self, output: Union[Dict[str, Any], str, bytes], file_name: str, file_type: str = "text") -> None:
        """
        Saves the output to a file using ArtifactsSaver with support for text, JSON, and binary files.
        Automatically appends the appropriate file extension.

        Args:
            output (Union[Dict[str, Any], str, bytes]): The output data to save.
            file_name (str): The base name of the output file (without extension).
            file_type (str): Type of the file to save ("text", "json", or "binary").

        Raises:
            CineNotesException: If there is an error during the save operation.
        """
        try:
            # Determine the file extension based on file_type
            file_extensions = {"text": ".txt", "json": ".json", "binary": ".bin"}
            if file_type not in file_extensions:
                raise ValueError(f"Unsupported file type: {file_type}")

            output_file = file_name + file_extensions[file_type]

            logging.info(f"Saving output to file {output_file} as {file_type} using ArtifactsSaver")

            # Initialize ArtifactsSaver to manage directory structure
            saver = ArtifactsSaver()

            # Save the file based on the file type
            if file_type == "text":
                if not isinstance(output, (str, Dict)):
                    raise TypeError("Output must be a string or dictionary for text files.")
                content = output if isinstance(output, str) else str(output)
                saver.save_text(output_file, content)

            elif file_type == "json":
                if not isinstance(output, (Dict, list)):
                    raise TypeError("Output must be a dictionary or list for JSON files.")
                saver.save_json(output_file, output)

            elif file_type == "binary":
                if not isinstance(output, bytes):
                    raise TypeError("Output must be bytes for binary files.")
                saver.save_binary(output_file, output)

            logging.info(f"Output successfully saved in: {saver.get_run_dir}/{output_file}")

        except TypeError as te:
            logging.error(f"Type error while saving {file_type} file: {te}")
            raise CineNotesException(f"Invalid data type for saving as {file_type}: {te}", sys)
        except ValueError as ve:
            logging.error(f"Value error: {ve}")
            raise CineNotesException(f"Invalid file type: {ve}", sys)
        except Exception as e:
            logging.error(f"Error saving output to {output_file}: {e}")
            raise CineNotesException(f"Failed to save output to file {output_file}\nDetailed Exception: {e}", sys)