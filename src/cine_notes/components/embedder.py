from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.embeddings.embeddings import Embeddings
from cine_notes.exception import CineNotesException
import sys
import os
from dotenv import load_dotenv
load_dotenv()

class Embedder:
    def __init__(self, provider: str, **kwargs) -> None:

        """
        Initialize the Embedder class.

        Args:
            provider (str): The embedding model provider. Supported: "google".
            api_key (str): The API key for the embedding model.
            model (str): The model name for the embedding model.
            **kwargs: Additional arguments for the embedding model.

        Raises:
            CineNotesException: If the provider is invalid or not specified.
        """
        if provider is None:
            raise CineNotesException("Provider is required for Embedder. Please provide a valid provider.", sys)

        self.provider = provider

        providers = ["google"]
        if self.provider not in providers:
            raise CineNotesException(f"Invalid provider: {self.provider}. Options are {providers}")

        if self.provider == "google":
            self.model = self._create_google_genai_embeddings_model(**kwargs)

    def _create_google_genai_embeddings_model(self, api_key: str = None, model: str = "models/embedding-001", **kwargs) -> Embeddings:
        """
        Create a Google Generative AI Embeddings model.

        Args:
            api_key (str): The API key for the Google embedding model.
            model (str): The model name. Defaults to "models/embedding-001".
            **kwargs: Additional arguments for the model.

        Returns:
            Embeddings: The initialized embedding model.

        Raises:
            CineNotesException: If the API key is not provided or initialization fails.
        """
        if api_key is None and os.getenv("GOOGLE_API_KEY") is None:
            raise CineNotesException(
                "Google API key is required for Google Generative AI Embeddings. "
                "Either pass `api_key` or set the environment variable `GOOGLE_API_KEY`.",
                sys
            )
        
        api_key = api_key if api_key else os.getenv("GOOGLE_API_KEY")
        try:
            return GoogleGenerativeAIEmbeddings(google_api_key=api_key, model=model, **kwargs)
        except Exception as e:
            raise CineNotesException(f"Failed to initialize Google Generative AI Embeddings. Error: {e}", sys)
