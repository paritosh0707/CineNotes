import os
import datetime
import json
import sys
from typing import Union, Dict, List
from cine_notes.logger import logging  # Replace this with your logger
from cine_notes.exception import CineNotesException  # Replace this with your exception handler


class ArtifactsSaver:
    """
    A utility class for saving artifacts (e.g., text files, JSON files, binary files) 
    into a structured directory for organized storage.

    Attributes:
        _run_dir (Union[str, None]): The directory for the current run, shared across all instances.
    """

    _run_dir: Union[str, None] = None  # Shared across all instances of the class

    def __init__(self, base_dir: str = "artifacts") -> None:
        """
        Initializes the ArtifactsSaver and creates a unique directory for the current run.

        Args:
            base_dir (str): The base directory to store artifacts. Default is "artifacts".
        """
        self.base_dir = base_dir

        if ArtifactsSaver._run_dir is None:
            try:
                # Create a unique run directory based on the current timestamp
                run_timestamp = datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S")
                ArtifactsSaver._run_dir = os.path.join(self.base_dir, run_timestamp)
                os.makedirs(ArtifactsSaver._run_dir, exist_ok=True)
                logging.info(f"Run directory created: {ArtifactsSaver._run_dir}")
            except Exception as e:
                raise CineNotesException(f"Failed to create run directory: {e}")

    def save_text(self, filename: str, content: str) -> None:
        """
        Saves a string as a text file in the run directory.

        Args:
            filename (str): The name of the file (e.g., "example.txt").
            content (str): The text content to save.

        Raises:
            CineNotesException: If there is an error saving the file.
        """
        try:
            file_path = os.path.join(ArtifactsSaver._run_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logging.info(f"Text file saved: {file_path}")
        except Exception as e:
            raise CineNotesException(f"Failed to save text file {filename}: {e}")

    def save_json(self, filename: str, data: Union[Dict, List]) -> None:
        """
        Saves data as a JSON file in the run directory.

        Args:
            filename (str): The name of the file (e.g., "data.json").
            data (Union[Dict, List]): The data to save (dictionary or list).

        Raises:
            CineNotesException: If there is an error saving the file.
        """
        try:
            file_path = os.path.join(ArtifactsSaver._run_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logging.info(f"JSON file saved: {file_path}")
        except Exception as e:
            raise CineNotesException(f"Failed to save JSON file {filename}: {e}")

    def save_binary(self, filename: str, data: bytes) -> None:
        """
        Saves binary data (e.g., images, models) in the run directory.

        Args:
            filename (str): The name of the file (e.g., "image.png").
            data (bytes): The binary data to save.

        Raises:
            CineNotesException: If there is an error saving the file.
        """
        try:
            file_path = os.path.join(ArtifactsSaver._run_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(data)
            logging.info(f"Binary file saved: {file_path}")
        except Exception as e:
            raise CineNotesException(f"Failed to save binary file {filename}: {e}")

    @property
    def get_run_dir(self) -> str:
        """
        Gets the path of the current run directory.

        Returns:
            str: The full path to the run directory.
        """
        return self._run_dir


# Example Usage
if __name__ == "__main__":
    try:
        # Create an instance of ArtifactsSaver
        saver = ArtifactsSaver()

        # Save a text file
        saver.save_text("example.txt", "This is an example text.")

        # Save a JSON file
        example_data = {"name": "John Doe", "age": 30, "is_active": True}
        saver.save_json("example.json", example_data)

        # Save binary data (e.g., an image or model)
        example_binary_data = b"This is binary data."
        saver.save_binary("example.bin", example_binary_data)

        # Print the run directory
        print(f"All files saved in: {saver.get_run_dir}")
    except CineNotesException as e:
        print(f"Error: {e}")