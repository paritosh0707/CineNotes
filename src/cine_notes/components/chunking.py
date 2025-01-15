from langchain_experimental.text_splitter import SemanticChunker
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_text_splitters.base import TextSplitter
from langchain_core.documents import BaseDocumentTransformer
from typing import List, Union

from cine_notes.components.embedder import Embedder
from cine_notes.exception import CineNotesException
import sys

class Chunker:
    def __init__(self, text_splitter: str = "semantic", chunk_size: int = 1000, chunk_overlap: int = 200, **kwargs) -> None:
        """
        Initializes the Chunking component.

        Args:
            text_splitter (str): The type of text splitter to use. Options are "semantic" or "recursive". Defaults to "semantic".
            chunk_size (int): The size of each chunk. Defaults to 1000.
            chunk_overlap (int): The overlap size between chunks. Defaults to 200.

            provider (str): The embedding model provider. Supported: "google".
            api_key (str): The API key for the embedding model.
            model (str): The model name for the embedding model.
            **kwargs: Additional keyword arguments passed to the Embedder if "semantic" text splitter is used.

        Raises:
            CineNotesException: If an invalid text splitter is provided.
        """
        text_splitters = ["semantic", "recursive"]
        if text_splitter not in text_splitters:
            raise CineNotesException(f"Invalid text splitter: {text_splitter}. Options are {text_splitters}")

        if text_splitter == "semantic":
            if "provider" not in kwargs:
                kwargs.setdefault("provider", "google")
            self.embedder = Embedder(**kwargs)

        self.text_splitter = self._initialize_text_splitter(text_splitter, chunk_size=chunk_size, chunk_overlap=chunk_overlap, **kwargs)

    def _initialize_text_splitter(self, text_splitter: str, **kwargs) -> Union[TextSplitter, BaseDocumentTransformer]:
        """
        Initialize the text splitter based on the provided type.

        Args:
            text_splitter (str): The type of text splitter.
            **kwargs: Additional arguments for initializing the text splitter.

        Returns:
            Union[TextSplitter, BaseDocumentTransformer]: The initialized text splitter.

        Raises:
            CineNotesException: If initialization fails or the splitter type is invalid.
        """
        if text_splitter == "semantic":
            try:
                return SemanticChunker(self.embedder.model)
            except Exception as e:
                raise CineNotesException(f"Failed to initialize Semantic Chunker. Error: {e}", sys)
        elif text_splitter == "recursive":
            try:
                return RecursiveCharacterTextSplitter(**kwargs)
            except Exception as e:
                raise CineNotesException(f"Failed to initialize Recursive Character Text Splitter. Error: {e}", sys)

    def create_documents(self, docs: List[str], **kwargs) -> List[Document]:
        """
        Create documents from a list of strings.

        Args:
            docs (List[str]): A list of strings to convert into documents.
            **kwargs: Additional arguments passed to the text splitter.

        Returns:
            List[Document]: A list of Document objects.

        Raises:
            CineNotesException: If the input is not a list of strings or document creation fails.
        """
        if not isinstance(docs, list):
            raise CineNotesException("Input must be a list of strings.", sys)

        try:
            documents = self.text_splitter.create_documents(docs, **kwargs)
            return documents
        except Exception as e:
            raise CineNotesException(f"Failed to create documents. Error: {e}", sys)

    def split_documents(self, docs: List[Document], **kwargs) -> List[Document]:
        """
        Split a list of documents into smaller chunks.

        Args:
            docs (List[Document]): A list of Document objects.
            **kwargs: Additional arguments passed to the text splitter.

        Returns:
            List[Document]: A list of split Document objects.

        Raises:
            CineNotesException: If input validation or splitting fails.
        """
        if not isinstance(docs, list):
            raise CineNotesException("Input must be a list of documents.", sys)

        try:
            documents = self.text_splitter.split_documents(docs, **kwargs)
            return documents
        except Exception as e:
            raise CineNotesException(f"Failed to split documents. Error: {e}", sys)

    def split_text(self, text: str, **kwargs) -> List[str]:
        """
        Split a single string of text into smaller chunks.

        Args:
            text (str): The text to split.
            **kwargs: Additional arguments passed to the text splitter.

        Returns:
            List[str]: A list of text chunks.

        Raises:
            CineNotesException: If input validation or splitting fails.
        """
        if not isinstance(text, str):
            raise CineNotesException("Input must be a string.", sys)

        try:
            documents = self.text_splitter.split_text(text, **kwargs)
            return documents
        except Exception as e:
            raise CineNotesException(f"Failed to split text. Error: {e}", sys)


