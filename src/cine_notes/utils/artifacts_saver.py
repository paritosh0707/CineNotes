"""
 * author Paritoh Sharma
 * created on 07-01-2025-16h-35m
 * github: https://github.com/paritosh0707
 * copyright 2025
"""

import os
import datetime
import json
import sys
from typing import Union, Dict, List
from cine_notes.logger import logging
from cine_notes.exception import CineNotesException

class ArtifactsSaver:
    """
    A class to save artifacts such as text files in a structured directory.
    Attributes:
        _run_dir (Union[str, None]): The directory for the current run, shared across all instances.
        base_dir (str): The base directory to store artifacts.
    Methods:
        __init__(base_dir: str = "artifacts") -> None:
        save_text(filename: str, content: str) -> None:
        save_json(filename: str, data: Union[Dict, List]) -> None:
        save_binary(filename: str, data: bytes) -> None:
        get_run_dir() -> str:
    """
    _run_dir: Union[str, None] = None  # Shared across all instances
    # _global_attributes: Dict[str, Union[str, int, float, bool]] = {}  # Global attributes shared across all instances
    
    def __init__(self, base_dir: str = "artifacts") -> None:
        """
        Initialize the ArtifactsSaver. If a run directory already exists (global),
        it will reuse the same directory.
        
        Args:
            base_dir (str): The base directory to store artifacts.
        """
        self.base_dir = base_dir

        if ArtifactsSaver._run_dir is None:
            try:
                # Create a new run directory with a timestamp
                run_timestamp = datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S")
                ArtifactsSaver._run_dir = os.path.join(self.base_dir, run_timestamp)
                os.makedirs(ArtifactsSaver._run_dir, exist_ok=True)
                logging.info(f"Run directory created: {ArtifactsSaver._run_dir}")
            except Exception as e:
                raise CineNotesException(f"Failed to create run directory: {e}")

    def save_text(self, filename: str, content: str) -> None:
        """
        Save a string as a text file.
        
        Args:
            filename (str): Name of the file (without directory).
            content (str): Text content to save.
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
        Save data as a JSON file.
        
        Args:
            filename (str): Name of the file (without directory).
            data (dict or list): Data to save as JSON.
        """
        try:
            file_path = os.path.join(ArtifactsSaver._run_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            logging.info(f"JSON file saved: {file_path}")
        except Exception as e:
            raise CineNotesException(f"Failed to save JSON file {filename}: {e}")

    def save_binary(self, filename: str, data: bytes) -> None:
        """
        Save binary data (e.g., images, models).
        
        Args:
            filename (str): Name of the file (without directory).
            data (bytes): Binary data to save.
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
        Get the directory for the current run.
        
        Returns:
            str: The path of the run directory.
        """
        return self._run_dir

    # @classmethod
    # def set_global_attribute(cls, key: str, value: Union[str, int, float, bool]) -> None:
    #     """
    #     Set a global attribute.
        
    #     Args:
    #         key (str): The attribute key.
    #         value (str, int, float, bool): The attribute value.
    #     """
    #     cls._global_attributes[key] = value
    #     logging.info(f"Global attribute set: {key} = {value}")

    # @classmethod
    # def get_global_attribute(cls, key: str) -> Union[str, int, float, bool, None]:
    #     """
    #     Get a global attribute.
        
    #     Args:
    #         key (str): The attribute key.
        
    #     Returns:
    #         str, int, float, bool, None: The attribute value or None if not found.
    #     """
    #     return cls._global_attributes.get(key)

# Example usage in two files
if __name__ == "__main__":
    try:
        # File 1
        saver1 = ArtifactsSaver()
        saver1.save_text("file1.txt", "Content from file 1")
        logging.info(f"All artifacts saved in: {saver1.get_run_dir}")
        
        # File 2
        saver2 = ArtifactsSaver()
        saver2.save_text("file2.txt", "Content from file 2")
        logging.info(f"All artifacts saved in: {saver2.get_run_dir}")
    except Exception as e:
        CineNotesException(f"Failed to save artifacts: {e}", sys)