"""
ODAM V4 Python SDK
==================

Офіційний Python SDK для інтеграції з ODAM V4 - системою штучного інтелекту з людською пам'яттю.

Основні можливості:
- 🧠 Розумні чат-відповіді з пам'яттю
- 💾 Система людської пам'яті
- 🏥 Медичні NLP сутності
- 🌐 Багатомовність (15+ мов)
- 🕸️ Граф знань
- 🎨 Персоналізація
- ⚡ Real-time обробка

Приклад використання:

    from odam_sdk import ODAMClient
    
    # Ініціалізація клієнта
    client = ODAMClient(api_key="your_api_key")
    
    # Відправка повідомлення
    response = client.chat(
        message="Привіт! Як справи?",
        user_id="user_123"
    )
    
    print(response.response)
    print(response.entities)
    print(response.memory_stats)

Версія: 1.0.0
Автор: ODAM Technologies
Ліцензія: MIT
"""

from .client import ODAMClient
from .models import (
    ChatRequest,
    ChatResponse,
    MemoryRequest,
    MemoryResponse,
    EntityRequest,
    EntityResponse,
    GraphRequest,
    GraphResponse,
    ODAMException,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    ServerError
)
from .config import ODAMConfig
from .utils import (
    validate_api_key,
    format_timestamp,
    detect_language,
    extract_entities,
    normalize_text
)

__version__ = "2.0.0"
__author__ = "ODAM Technologies"
__license__ = "MIT"

__all__ = [
    "ODAMClient",
    "ChatRequest",
    "ChatResponse", 
    "MemoryRequest",
    "MemoryResponse",
    "EntityRequest",
    "EntityResponse",
    "GraphRequest",
    "GraphResponse",
    "ODAMException",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
    "ServerError",
    "ODAMConfig",
    "validate_api_key",
    "format_timestamp",
    "detect_language",
    "extract_entities",
    "normalize_text"
] 