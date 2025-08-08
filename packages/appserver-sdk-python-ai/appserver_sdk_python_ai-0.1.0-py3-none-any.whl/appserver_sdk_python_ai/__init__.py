"""AppServer SDK Python AI - SDK para serviços de IA."""

from __future__ import annotations

# Version
__version__ = "0.0.1"

# LLM exports - usando imports relativos corretos
from .llm.core.enums import (
    HuggingFaceModelEnum,
    OpenAIModelEnum,
    TokenizerTypeEnum,
)
from .llm.service.token_service import (
    get_model_info,
    get_portuguese_models,
    get_token_count,
    get_token_count_with_model,
    is_model_registered,
    list_available_models,
    register_custom_model,
)

__all__ = [
    "HuggingFaceModelEnum",
    # Enums
    "OpenAIModelEnum",
    "TokenizerTypeEnum",
    # Version
    "__version__",
    "get_model_info",
    "get_portuguese_models",
    # Core LLM functionality
    "get_token_count",
    "get_token_count_with_model",
    "is_model_registered",
    "list_available_models",
    "register_custom_model",
]

# Metadata
__author__ = "AppServer Team"
__email__ = "suporte@appserver.com.br"
__description__ = "SDK Python para serviços de IA da AppServer"
__url__ = "https://appserver.com.br"


def get_user_agent() -> str:
    """Retorna User-Agent para requisições."""
    return f"appserver-sdk-python-ai/{__version__}"
