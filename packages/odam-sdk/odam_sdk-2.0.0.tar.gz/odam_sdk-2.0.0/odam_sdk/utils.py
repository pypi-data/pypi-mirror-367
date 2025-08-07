"""
Утиліти для ODAM V4 SDK
========================

Цей модуль містить допоміжні функції для роботи з SDK.
"""

import re
import hashlib
import json
import time
from typing import Optional, Dict, Any, List, Union
from datetime import datetime, timezone
from functools import wraps
import logging

from .models import Language, EntityType


def validate_api_key(api_key: str) -> bool:
    """
    Валідація API ключа
    
    Args:
        api_key: API ключ для перевірки
        
    Returns:
        True якщо ключ валідний, False інакше
    """
    if not api_key:
        return False
    
    # Базові перевірки
    if len(api_key) < 10:
        return False
    
    # Перевірка формату (приблизна)
    if not re.match(r'^[a-zA-Z0-9_-]+$', api_key):
        return False
    
    return True


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """
    Форматування timestamp в ISO формат
    
    Args:
        dt: datetime об'єкт або None для поточного часу
        
    Returns:
        ISO форматований timestamp
    """
    if dt is None:
        dt = datetime.now(timezone.utc)
    
    return dt.isoformat()


def detect_language(text: str) -> str:
    """
    Просте визначення мови тексту
    
    Args:
        text: Текст для аналізу
        
    Returns:
        Код мови (uk, en, ru, тощо)
    """
    if not text:
        return "auto"
    
    # Прості правила для визначення мови
    ukrainian_chars = set('абвгґдеєжзиіїйклмнопрстуфхцчшщьюя')
    russian_chars = set('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')
    
    text_lower = text.lower()
    uk_count = sum(1 for char in text_lower if char in ukrainian_chars)
    ru_count = sum(1 for char in text_lower if char in russian_chars)
    
    if uk_count > ru_count and uk_count > 0:
        return "uk"
    elif ru_count > uk_count and ru_count > 0:
        return "ru"
    else:
        # Якщо немає кириличних символів, вважаємо англійською
        return "en"


def extract_entities(text: str, entity_types: Optional[List[EntityType]] = None) -> List[Dict[str, Any]]:
    """
    Просте витягування сутностей з тексту
    
    Args:
        text: Текст для аналізу
        entity_types: Типи сутностей для пошуку
        
    Returns:
        Список знайдених сутностей
    """
    entities = []
    
    if not text:
        return entities
    
    # Прості патерни для визначення сутностей
    patterns = {
        EntityType.PERSON: r'\b[A-ZА-ЯІЇЄ][a-zа-яіїє]+\s+[A-ZА-ЯІЇЄ][a-zа-яіїє]+\b',
        EntityType.DATE: r'\b\d{1,2}[./]\d{1,2}[./]\d{2,4}\b',
        EntityType.TIME: r'\b\d{1,2}:\d{2}\b',
        EntityType.MONEY: r'\b\d+\.?\d*\s*(грн|USD|EUR|₴|$|€)\b',
        EntityType.PERCENT: r'\b\d+\.?\d*%\b',
        EntityType.QUANTITY: r'\b\d+\.?\d*\s*(кг|л|м|см|мм|км)\b',
    }
    
    # Якщо не вказані типи, використовуємо всі
    if entity_types is None:
        entity_types = list(patterns.keys())
    
    for entity_type in entity_types:
        if entity_type in patterns:
            matches = re.finditer(patterns[entity_type], text, re.IGNORECASE)
            for match in matches:
                entities.append({
                    "text": match.group(),
                    "type": entity_type.value,
                    "confidence": 0.8,  # Базова впевненість
                    "start": match.start(),
                    "end": match.end()
                })
    
    return entities


def normalize_text(text: str) -> str:
    """
    Нормалізація тексту
    
    Args:
        text: Текст для нормалізації
        
    Returns:
        Нормалізований текст
    """
    if not text:
        return ""
    
    # Видалення зайвих пробілів
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Нормалізація лапок
    text = re.sub(r'["""]', '"', text)
    text = re.sub(r"[''']", "'", text)
    
    # Нормалізація дефісів
    text = re.sub(r'–|—', '-', text)
    
    return text


def generate_cache_key(*args, **kwargs) -> str:
    """
    Генерація ключа кешу
    
    Args:
        *args: Позиційні аргументи
        **kwargs: Іменовані аргументи
        
    Returns:
        Унікальний ключ кешу
    """
    # Створюємо словник з усіх аргументів
    data = {
        'args': args,
        'kwargs': kwargs
    }
    
    # Конвертуємо в JSON та хешуємо
    json_str = json.dumps(data, sort_keys=True, default=str)
    return hashlib.md5(json_str.encode()).hexdigest()


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff_factor: float = 2.0):
    """
    Декоратор для повторних спроб при помилках
    
    Args:
        max_retries: Максимальна кількість спроб
        delay: Початкова затримка в секундах
        backoff_factor: Множник для збільшення затримки
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        time.sleep(current_delay)
                        current_delay *= backoff_factor
                    else:
                        raise last_exception
            
            return None
        return wrapper
    return decorator


def setup_logging(level: str = "INFO", enable_requests: bool = True, enable_responses: bool = False) -> logging.Logger:
    """
    Налаштування логування
    
    Args:
        level: Рівень логування
        enable_requests: Логувати запити
        enable_responses: Логувати відповіді
        
    Returns:
        Налаштований logger
    """
    logger = logging.getLogger("odam_sdk")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Якщо handler вже існує, не додаємо новий
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def log_request(logger: logging.Logger, method: str, url: str, data: Optional[Dict] = None):
    """
    Логування запиту
    
    Args:
        logger: Logger об'єкт
        method: HTTP метод
        url: URL запиту
        data: Дані запиту
    """
    if data:
        # Приховуємо API ключ в логах
        safe_data = data.copy()
        if 'api_key' in safe_data:
            safe_data['api_key'] = '***'
        logger.info(f"Request: {method} {url} - Data: {safe_data}")
    else:
        logger.info(f"Request: {method} {url}")


def log_response(logger: logging.Logger, status_code: int, response_data: Optional[Dict] = None):
    """
    Логування відповіді
    
    Args:
        logger: Logger об'єкт
        status_code: HTTP статус код
        response_data: Дані відповіді
    """
    if response_data:
        logger.info(f"Response: {status_code} - Data: {response_data}")
    else:
        logger.info(f"Response: {status_code}")


def validate_url(url: str) -> bool:
    """
    Валідація URL
    
    Args:
        url: URL для перевірки
        
    Returns:
        True якщо URL валідний, False інакше
    """
    if not url:
        return False
    
    # Проста перевірка формату URL
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url))


def sanitize_user_id(user_id: str) -> str:
    """
    Очищення user_id від небезпечних символів
    
    Args:
        user_id: ID користувача
        
    Returns:
        Очищений ID користувача
    """
    if not user_id:
        return ""
    
    # Видаляємо небезпечні символи
    sanitized = re.sub(r'[^\w\-_.]', '_', user_id)
    
    # Обмежуємо довжину
    if len(sanitized) > 100:
        sanitized = sanitized[:100]
    
    return sanitized


def create_session_id() -> str:
    """
    Створення унікального session_id
    
    Returns:
        Унікальний session_id
    """
    return f"session_{int(time.time())}_{hash(str(time.time())) % 10000}"


def merge_contexts(*contexts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Об'єднання контекстів
    
    Args:
        *contexts: Контексти для об'єднання
        
    Returns:
        Об'єднаний контекст
    """
    merged = {}
    
    for context in contexts:
        if context:
            merged.update(context)
    
    return merged


def is_medical_context(text: str) -> bool:
    """
    Визначення чи текст містить медичний контекст
    
    Args:
        text: Текст для аналізу
        
    Returns:
        True якщо текст містить медичний контекст
    """
    medical_keywords = [
        'лікар', 'лікування', 'хвороба', 'симптом', 'діагноз',
        'ліки', 'таблетки', 'укол', 'операція', 'рецепт',
        'doctor', 'treatment', 'disease', 'symptom', 'diagnosis',
        'medicine', 'pills', 'injection', 'surgery', 'prescription'
    ]
    
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in medical_keywords)


def calculate_response_time(start_time: float) -> float:
    """
    Розрахунок часу відповіді
    
    Args:
        start_time: Час початку запиту
        
    Returns:
        Час відповіді в секундах
    """
    return time.time() - start_time


def format_entity_type(entity_type: Union[str, EntityType]) -> str:
    """
    Форматування типу сутності
    
    Args:
        entity_type: Тип сутності
        
    Returns:
        Відформатований тип сутності
    """
    if isinstance(entity_type, EntityType):
        return entity_type.value
    return str(entity_type)


def validate_language(language: str) -> bool:
    """
    Валідація коду мови
    
    Args:
        language: Код мови
        
    Returns:
        True якщо код мови валідний
    """
    valid_languages = [lang.value for lang in Language]
    return language in valid_languages


def create_error_message(error: Exception, context: str = "") -> str:
    """
    Створення повідомлення про помилку
    
    Args:
        error: Об'єкт помилки
        context: Контекст помилки
        
    Returns:
        Форматуване повідомлення про помилку
    """
    error_msg = f"ODAM SDK Error: {str(error)}"
    if context:
        error_msg = f"{context} - {error_msg}"
    return error_msg 