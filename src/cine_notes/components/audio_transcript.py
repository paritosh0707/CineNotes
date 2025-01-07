"""
 * author Paritoh Sharma
 * created on 07-01-2025-16h-13m
 * github: https://github.com/paritosh0707
 * copyright 2025
"""

import requests
import os
from cine_notes.logger import logging
from cine_notes.exception import CineNotesException
import sys
from typing import Dict, Any


class HuggingFaceWhisperAPI:
    """
    A class to interact with the Hugging Face Whisper API for audio transcription.
    Attributes:
        api_key (str): The API key for authenticating with the Hugging Face API.
        api_url (str): The URL endpoint for the Hugging Face API.
        headers (dict): The headers to include in the API requests.
    Methods:
        __init__(model_name: str = "openai/whisper-large-v3-turbo") -> None:
        query(filename: str) -> Dict[str, Any]: Sends a file to the Hugging Face API for transcription and returns the JSON response.
        _save_output(output: Dict[str, Any], output_file: str = "output.txt") -> None: Saves the output data to a text file.
    """

    def __init__(self, model_name: str = "openai/whisper-large-v3-turbo") -> None:
        """
        Initializes the HuggingFaceWhisperAPI class with the specified model name.

        Args:
            model_name (str): The name of the model to use for transcription.
        """
        try:
            self.api_key = os.getenv("HUGGINGFACE_WHISPER_TOKEN")
            if not self.api_key:
                logging.error("HUGGINGFACE_WHISPER_TOKEN not found in environment variables.")
                raise ValueError("HUGGINGFACE_WHISPER_TOKEN not found in environment variables.")
            self.api_url = f"https://api-inference.huggingface.co/models/{model_name}"
            self.headers = {"Authorization": f"Bearer {self.api_key}"}
            logging.info(f"Initialized HuggingFaceWhisperAPI with model {model_name}")
        except Exception as e:
            raise CineNotesException(f"Failed to initialize HuggingFaceWhisperAPI\nDetailed Exception :\n{e}", sys)

    def query(self, filename: str) -> Dict[str, Any]:
        """
        Sends a file to the Hugging Face API for transcription.

        Args:
            filename (str): Path to the audio file.

        Returns:
            dict: JSON response from the API.
        """
        logging.info(f"Querying Hugging Face API with file {filename}")
        try:
            with open(filename, "rb") as file:
                data = file.read()
            response = requests.post(self.api_url, headers=self.headers, data=data)
            response.raise_for_status()
            logging.info("Successfully queried Hugging Face API")
            self._save_output(response.json())
            return response.json()
        except FileNotFoundError:
            raise FileNotFoundError(f"File {filename} not found.")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"API request failed: {e}")
        except Exception as e:
            raise CineNotesException(f"Failed to query Hugging Face API\nDetailed Exception :\n{e}", sys)

    def _save_output(self, output: Dict[str, Any], output_file: str = "output.txt") -> None:
        """
        Saves the output to a text file.

        Args:
            output (dict): The output data to save.
            output_file (str): Path to the output file.
        """
        logging.info(f"Saving output to file {output_file}")
        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                file.write(str(output))
            logging.info(f"Successfully saved output to {output_file}")
        except Exception as e:
            raise CineNotesException(f"Failed to save output to file\nDetailed Exception :\n{e}", sys)