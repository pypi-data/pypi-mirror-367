"""
Моделі даних для ODAM V4 SDK
============================

Цей модуль містить всі Pydantic моделі для типізації запитів та відповідей API.
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator
import uuid


class Language(str, Enum):
    """Підтримувані мови"""
    UKRAINIAN = "uk"
    ENGLISH = "en"
    RUSSIAN = "ru"
    POLISH = "pl"
    GERMAN = "de"
    FRENCH = "fr"
    SPANISH = "es"
    ITALIAN = "it"
    AUTO = "auto"


class MemoryType(str, Enum):
    """Типи пам'яті"""
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    EMOTIONAL = "emotional"
    PROCEDURAL = "procedural"
    PROMISE = "promise"
    ALL = "all"


class EntityType(str, Enum):
    """Типи сутностей"""
    PERSON = "Person"
    AGE = "Age"
    CONDITION = "Condition"
    MEDICATION = "Medication"
    SYMPTOM = "Symptom"
    TEST = "Test"
    TREATMENT = "Treatment"
    ALLERGY = "Allergy"
    FAMILY_HISTORY = "FamilyHistory"
    LOCATION = "Location"
    ORGANIZATION = "Organization"
    DATE = "Date"
    TIME = "Time"
    MONEY = "Money"
    PERCENT = "Percent"
    QUANTITY = "Quantity"


class EmotionalState(str, Enum):
    """Емоційні стани"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    EXCITED = "excited"
    ANGRY = "angry"
    SAD = "sad"
    ANXIOUS = "anxious"
    CONFIDENT = "confident"


class MedicalSafetyLevel(str, Enum):
    """Рівні медичної безпеки"""
    STRICT = "strict"
    MODERATE = "moderate"
    RELAXED = "relaxed"


# ============================================================================
# БАЗОВІ КЛАСИ ВИНЯТКІВ
# ============================================================================

class ODAMException(Exception):
    """Базовий клас для всіх винятків ODAM SDK"""
    pass


class AuthenticationError(ODAMException):
    """Помилка автентифікації"""
    pass


class RateLimitError(ODAMException):
    """Помилка перевищення ліміту запитів"""
    pass


class ValidationError(ODAMException):
    """Помилка валідації даних"""
    pass


class ServerError(ODAMException):
    """Помилка сервера"""
    pass


# ============================================================================
# МОДЕЛІ ЗАПИТІВ
# ============================================================================

class ChatRequest(BaseModel):
    """Модель запиту для чату"""
    
    message: str = Field(..., min_length=1, max_length=10000, description="Повідомлення користувача")
    user_id: str = Field(..., min_length=1, max_length=100, description="Унікальний ID користувача")
    session_id: Optional[str] = Field(None, max_length=100, description="ID сесії")
    language: Optional[Language] = Field(Language.AUTO, description="Мова повідомлення")
    
    # Параметри функціональності
    use_memory: bool = Field(True, description="Використовувати пам'ять користувача")
    use_medical_nlp: bool = Field(True, description="Використовувати медичні NLP")
    use_graph_search: bool = Field(True, description="Використовувати граф пошук")
    fast_mode: bool = Field(True, description="Швидкий режим обробки")
    
    # Enterprise V7 параметри
    enterprise_v7: bool = Field(False, description="Використовувати Enterprise V7 функціонал")
    fallback_enabled: bool = Field(False, description="Увімкнути Senior Fallback логіку")
    medical_safety: bool = Field(False, description="Увімкнути Medical Safety Enforcement")
    memory_enforcement: bool = Field(False, description="Увімкнути Memory Enforcement")
    
    # Контекст
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Додатковий контекст")
    
    @validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError("Повідомлення не може бути порожнім")
        return v.strip()
    
    @validator('user_id')
    def validate_user_id(cls, v):
        if not v.strip():
            raise ValueError("User ID не може бути порожнім")
        return v.strip()
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Привіт! Як справи?",
                "user_id": "user_123",
                "session_id": "session_456",
                "language": "uk",
                "use_memory": True,
                "use_medical_nlp": True,
                "context": {"source": "mobile_app", "location": "kyiv"}
            }
        }


class MemoryRequest(BaseModel):
    """Модель запиту для роботи з пам'яттю"""
    
    user_id: str = Field(..., min_length=1, max_length=100, description="ID користувача")
    memory_type: Optional[MemoryType] = Field(MemoryType.ALL, description="Тип пам'яті")
    limit: Optional[int] = Field(50, ge=1, le=1000, description="Кількість записів")
    offset: Optional[int] = Field(0, ge=0, description="Зміщення")
    start_date: Optional[datetime] = Field(None, description="Початкова дата")
    end_date: Optional[datetime] = Field(None, description="Кінцева дата")
    
    @validator('user_id')
    def validate_user_id(cls, v):
        if not v.strip():
            raise ValueError("User ID не може бути порожнім")
        return v.strip()


class EntityRequest(BaseModel):
    """Модель запиту для витягування сутностей"""
    
    text: str = Field(..., min_length=1, max_length=10000, description="Текст для аналізу")
    entity_types: Optional[List[EntityType]] = Field(None, description="Типи сутностей для пошуку")
    language: Optional[Language] = Field(Language.AUTO, description="Мова тексту")
    medical_mode: bool = Field(False, description="Медичний режим")
    
    @validator('text')
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError("Текст не може бути порожнім")
        return v.strip()


class GraphRequest(BaseModel):
    """Модель запиту для роботи з графом знань"""
    
    query: str = Field(..., min_length=1, max_length=1000, description="Запит до графу")
    user_id: Optional[str] = Field(None, max_length=100, description="ID користувача для персоналізації")
    depth: Optional[int] = Field(3, ge=1, le=10, description="Глибина пошуку")
    limit: Optional[int] = Field(50, ge=1, le=1000, description="Ліміт результатів")
    
    @validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError("Запит не може бути порожнім")
        return v.strip()


# ============================================================================
# МОДЕЛІ ВІДПОВІДЕЙ
# ============================================================================

class Entity(BaseModel):
    """Модель сутності"""
    
    text: str = Field(..., description="Текст сутності")
    type: EntityType = Field(..., description="Тип сутності")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Впевненість")
    start: int = Field(..., ge=0, description="Початкова позиція")
    end: int = Field(..., ge=0, description="Кінцева позиція")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Додаткові властивості")


class TypedEntity(BaseModel):
    """Модель типізованої сутності (V7)"""
    
    name: str = Field(..., description="Назва сутності")
    type: str = Field(..., description="Тип сутності")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Впевненість")
    extraction_method: str = Field(..., description="Метод витягування")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Додаткові властивості")


class LanguageInfo(BaseModel):
    """Інформація про мову"""
    
    language: str = Field(..., description="Код мови")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Впевненість визначення")


class MemoryStats(BaseModel):
    """Статистика пам'яті"""
    
    memories_found: int = Field(..., ge=0, description="Знайдено спогадів")
    memories_created: int = Field(..., ge=0, description="Створено спогадів")
    memory_layers: List[str] = Field(default_factory=list, description="Використані шари пам'яті")
    memory_strength: float = Field(..., ge=0.0, le=1.0, description="Сила пам'яті")


class SearchResults(BaseModel):
    """Результати пошуку"""
    
    vector_results: int = Field(..., ge=0, description="Результати векторного пошуку")
    bm25_results: int = Field(..., ge=0, description="Результати BM25 пошуку")
    graph_results: int = Field(..., ge=0, description="Результати граф пошуку")


class V7Metrics(BaseModel):
    """Метрики Enterprise V7"""
    
    memory_utilization_score: float = Field(..., ge=0.0, le=1.0, description="Використання пам'яті")
    medical_safety_level: MedicalSafetyLevel = Field(..., description="Рівень медичної безпеки")
    fallback_used: bool = Field(..., description="Використано fallback")
    context_injection_success: float = Field(..., ge=0.0, le=1.0, description="Успішність ін'єкції контексту")


class ChatResponse(BaseModel):
    """Модель відповіді чату"""
    
    response: str = Field(..., description="Відповідь AI")
    user_id: str = Field(..., description="ID користувача")
    session_id: Optional[str] = Field(None, description="ID сесії")
    processing_time: float = Field(..., ge=0.0, description="Час обробки в секундах")
    
    # Мова
    language_info: LanguageInfo = Field(..., description="Інформація про мову")
    
    # Сутності
    entities: List[Entity] = Field(default_factory=list, description="Витягнуті сутності")
    typed_entities: List[TypedEntity] = Field(default_factory=list, description="Типізовані сутності (V7)")
    extracted_entities: List[TypedEntity] = Field(default_factory=list, description="Витягнуті сутності (V7)")
    
    # Пам'ять
    memory_stats: MemoryStats = Field(..., description="Статистика пам'яті")
    
    # Пошук
    search_results: SearchResults = Field(..., description="Результати пошуку")
    
    # Персоналізація
    personalization_score: float = Field(..., ge=0.0, le=1.0, description="Оцінка персоналізації")
    
    # V7 метрики
    v7_metrics: Optional[V7Metrics] = Field(None, description="Метрики Enterprise V7")
    
    # Метадані
    timestamp: datetime = Field(..., description="Час відповіді")
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="ID запиту")


class Memory(BaseModel):
    """Модель спогаду"""
    
    id: str = Field(..., description="Унікальний ID спогаду")
    type: MemoryType = Field(..., description="Тип пам'яті")
    content: str = Field(..., description="Зміст спогаду")
    entities: List[str] = Field(default_factory=list, description="Сутності в спогаді")
    emotional_state: Optional[EmotionalState] = Field(None, description="Емоційний стан")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Впевненість")
    timestamp: datetime = Field(..., description="Час створення")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Контекст")


class MemoryResponse(BaseModel):
    """Модель відповіді для пам'яті"""
    
    user_id: str = Field(..., description="ID користувача")
    memories: List[Memory] = Field(default_factory=list, description="Спогади")
    total_count: int = Field(..., ge=0, description="Загальна кількість")
    memory_type: MemoryType = Field(..., description="Тип пам'яті")
    processing_time: float = Field(..., ge=0.0, description="Час обробки")


class EntityResponse(BaseModel):
    """Модель відповіді для сутностей"""
    
    entities: List[Entity] = Field(default_factory=list, description="Знайдені сутності")
    typed_entities: List[TypedEntity] = Field(default_factory=list, description="Типізовані сутності")
    language: str = Field(..., description="Визначена мова")
    processing_time: float = Field(..., ge=0.0, description="Час обробки")
    medical_mode: bool = Field(..., description="Використовувався медичний режим")


class GraphNode(BaseModel):
    """Модель вузла графу"""
    
    id: str = Field(..., description="ID вузла")
    label: str = Field(..., description="Мітка вузла")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Властивості вузла")


class GraphRelationship(BaseModel):
    """Модель зв'язку графу"""
    
    id: str = Field(..., description="ID зв'язку")
    type: str = Field(..., description="Тип зв'язку")
    start_node: str = Field(..., description="ID початкового вузла")
    end_node: str = Field(..., description="ID кінцевого вузла")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Властивості зв'язку")


class GraphResponse(BaseModel):
    """Модель відповіді для графу"""
    
    nodes: List[GraphNode] = Field(default_factory=list, description="Вузли графу")
    relationships: List[GraphRelationship] = Field(default_factory=list, description="Зв'язки графу")
    query: str = Field(..., description="Виконаний запит")
    processing_time: float = Field(..., ge=0.0, description="Час обробки")
    depth: int = Field(..., description="Глибина пошуку")


# ============================================================================
# ДОПОМІЖНІ МОДЕЛІ
# ============================================================================

class BatchChatRequest(BaseModel):
    """Модель для batch запитів чату"""
    
    messages: List[ChatRequest] = Field(..., min_items=1, max_items=100, description="Список запитів")


class BatchChatResponse(BaseModel):
    """Модель для batch відповідей чату"""
    
    results: List[ChatResponse] = Field(default_factory=list, description="Результати обробки")
    total_processed: int = Field(..., ge=0, description="Загальна кількість оброблених")
    total_successful: int = Field(..., ge=0, description="Успішно оброблених")
    total_failed: int = Field(..., ge=0, description="Неуспішно оброблених")
    processing_time: float = Field(..., ge=0.0, description="Загальний час обробки")


class HealthCheck(BaseModel):
    """Модель перевірки здоров'я системи"""
    
    status: str = Field(..., description="Статус системи")
    version: str = Field(..., description="Версія API")
    timestamp: datetime = Field(..., description="Час перевірки")
    components: Dict[str, str] = Field(default_factory=dict, description="Статус компонентів")
    uptime: float = Field(..., ge=0.0, description="Час роботи в секундах") 