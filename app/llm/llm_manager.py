from enum import Enum
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from app.config import settings


class LLMOptions(Enum):
    """Enum to define available model names."""
    GPT_MINI = "gpt-4o-mini"
    GEMINI_FLASH = "gemini-2.0-flash"


class LLM:
    _instance = None  # Class-level variable to store the singleton instance

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LLM, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):  # Ensure __init__ runs only once
            self.gpt_mini = ChatOpenAI(
                model="gpt-4o-mini", api_key=settings.openai_api_key
            )
            self.gemini = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                timeout=None,
                max_retries=2,
                google_api_key=settings.gemini_api_key,
            )
            self.default_model = self.gemini  # Default model to use
            self.initialized = True  # Mark as initialized to avoid re-initialization

    def get(self, model_name: LLMOptions):
        """
        Get the LLM instance by model name.

        Args:
            model_name (ModelName): The enum value representing the model to retrieve.

        Returns:
            The initialized instance of the requested model, or raises an exception if the model is not found.
        """
        model_mapping = {
            LLMOptions.GPT_MINI: self.gpt_mini,
            LLMOptions.GEMINI_FLASH: self.gemini,
        }

        if model_name in model_mapping:
            return model_mapping[model_name]
        else:
            return self.default_model
