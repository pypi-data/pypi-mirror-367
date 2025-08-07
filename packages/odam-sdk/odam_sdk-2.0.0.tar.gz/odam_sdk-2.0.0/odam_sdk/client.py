"""
ODAM V4 SDK Client
==================

Основний клієнт для роботи з ODAM V4 API.
"""

import time
import json
import logging
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from functools import lru_cache

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .models import (
    ChatRequest, ChatResponse, MemoryRequest, MemoryResponse,
    EntityRequest, EntityResponse, GraphRequest, GraphResponse,
    BatchChatRequest, BatchChatResponse, HealthCheck,
    ODAMException, AuthenticationError, RateLimitError, ValidationError, ServerError,
    Language, MemoryType, EntityType
)
from .config import ODAMConfig, create_config
from .utils import (
    validate_api_key, format_timestamp, detect_language, extract_entities,
    normalize_text, generate_cache_key, retry_on_failure, setup_logging,
    log_request, log_response, validate_url, sanitize_user_id,
    create_session_id, merge_contexts, is_medical_context,
    calculate_response_time, validate_language, create_error_message
)


class ODAMClient:
    """
    Основний клієнт для роботи з ODAM V4 API
    
    Приклад використання:
    
        from odam_sdk import ODAMClient
        
        # Створення клієнта
        client = ODAMClient(api_key="your_api_key")
        
        # Відправка повідомлення
        response = client.chat(
            message="Привіт! Як справи?",
            user_id="user_123"
        )
        
        print(response.response)
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        config: Optional[ODAMConfig] = None,
        **kwargs
    ):
        """
        Ініціалізація клієнта
        
        Args:
            api_key: API ключ ODAM
            base_url: Базовий URL API
            config: Конфігурація клієнта
            **kwargs: Додаткові параметри конфігурації
        """
        # Створення конфігурації
        if config:
            self.config = config
        else:
            self.config = create_config(api_key=api_key, base_url=base_url, **kwargs)
        
        # Валідація API ключа
        if not validate_api_key(self.config.api_key):
            raise AuthenticationError("Невірний API ключ")
        
        # Налаштування сесії
        self.session = self._create_session()
        
        # Налаштування логування
        self.logger = setup_logging(
            level=self.config.log_level,
            enable_requests=self.config.log_requests,
            enable_responses=self.config.log_responses
        )
        
        # Кеш для відповідей
        self._cache = {}
        
        self.logger.info("ODAM Client ініціалізовано")
    
    def _create_session(self) -> requests.Session:
        """Створення HTTP сесії з retry логікою"""
        session = requests.Session()
        
        # Налаштування retry стратегії
        retry_strategy = Retry(
            total=self.config.max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "POST", "PUT", "DELETE"],
            backoff_factor=self.config.backoff_factor
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Налаштування заголовків
        session.headers.update(self.config.headers)
        
        return session
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Виконання HTTP запиту
        
        Args:
            method: HTTP метод
            endpoint: Endpoint API
            data: Дані запиту
            params: Параметри запиту
            timeout: Таймаут запиту
            
        Returns:
            Відповідь API
            
        Raises:
            AuthenticationError: Помилка автентифікації
            RateLimitError: Помилка ліміту запитів
            ValidationError: Помилка валідації
            ServerError: Помилка сервера
        """
        url = f"{self.config.api_url}/{endpoint.lstrip('/')}"
        timeout = timeout or self.config.timeout
        
        start_time = time.time()
        
        try:
            # Логування запиту
            if self.config.log_requests:
                log_request(self.logger, method, url, data)
            
            # Виконання запиту
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=timeout,
                verify=self.config.verify_ssl
            )
            
            # Логування відповіді
            if self.config.log_responses:
                log_response(self.logger, response.status_code, response.json() if response.content else None)
            
            # Обробка помилок
            if response.status_code == 401:
                raise AuthenticationError("Невірний API ключ")
            elif response.status_code == 429:
                raise RateLimitError("Перевищено ліміт запитів")
            elif response.status_code == 422:
                raise ValidationError(f"Помилка валідації: {response.text}")
            elif response.status_code >= 500:
                raise ServerError(f"Помилка сервера: {response.status_code}")
            elif response.status_code >= 400:
                raise ValidationError(f"Помилка запиту: {response.status_code} - {response.text}")
            
            # Парсинг відповіді
            response_data = response.json() if response.content else {}
            
            # Додавання метаданих
            response_data['_processing_time'] = calculate_response_time(start_time)
            response_data['_status_code'] = response.status_code
            
            return response_data
            
        except requests.exceptions.RequestException as e:
            error_msg = create_error_message(e, f"HTTP запит до {url}")
            self.logger.error(error_msg)
            raise ServerError(error_msg) from e
    
    @retry_on_failure(max_retries=3, delay=1.0, backoff_factor=2.0)
    def chat(
        self,
        message: str,
        user_id: str,
        session_id: Optional[str] = None,
        language: Optional[Union[str, Language]] = None,
        use_memory: bool = True,
        use_medical_nlp: bool = True,
        use_graph_search: bool = True,
        fast_mode: bool = True,
        enterprise_v7: bool = False,
        fallback_enabled: bool = False,
        medical_safety: bool = False,
        memory_enforcement: bool = False,
        context: Optional[Dict[str, Any]] = None
    ) -> ChatResponse:
        """
        Відправка повідомлення до ODAM AI
        
        Args:
            message: Повідомлення користувача
            user_id: Унікальний ID користувача
            session_id: ID сесії (опційно)
            language: Мова повідомлення
            use_memory: Використовувати пам'ять користувача
            use_medical_nlp: Використовувати медичні NLP
            use_graph_search: Використовувати граф пошук
            fast_mode: Швидкий режим обробки
            enterprise_v7: Enterprise V7 функціонал
            fallback_enabled: Senior Fallback логіка
            medical_safety: Medical Safety Enforcement
            memory_enforcement: Memory Enforcement
            context: Додатковий контекст
            
        Returns:
            ChatResponse об'єкт з відповіддю AI
            
        Raises:
            ValidationError: Помилка валідації даних
            AuthenticationError: Помилка автентифікації
            ServerError: Помилка сервера
        """
        # Валідація та нормалізація вхідних даних
        if not message or not message.strip():
            raise ValidationError("Повідомлення не може бути порожнім")
        
        if not user_id or not user_id.strip():
            raise ValidationError("User ID не може бути порожнім")
        
        message = normalize_text(message)
        user_id = sanitize_user_id(user_id)
        
        # Автоматичне визначення мови
        if language is None or language == "auto":
            language = detect_language(message)
        elif isinstance(language, Language):
            language = language.value
        
        # Створення session_id якщо не вказано
        if not session_id:
            session_id = create_session_id()
        
        # Підготовка даних запиту
        request_data = {
            "message": message,
            "user_id": user_id,
            "session_id": session_id,
            "language": language,
            "use_memory": use_memory,
            "use_medical_nlp": use_medical_nlp,
            "use_graph_search": use_graph_search,
            "fast_mode": fast_mode,
            "enterprise_v7": enterprise_v7,
            "fallback_enabled": fallback_enabled,
            "medical_safety": medical_safety,
            "memory_enforcement": memory_enforcement,
            "context": context or {}
        }
        
        # Виконання запиту
        response_data = self._make_request("POST", "chat", data=request_data)
        
        # Конвертація в ChatResponse
        return ChatResponse(**response_data)
    
    def chat_batch(
        self,
        messages: List[Dict[str, Any]]
    ) -> BatchChatResponse:
        """
        Batch обробка повідомлень
        
        Args:
            messages: Список повідомлень для обробки
            
        Returns:
            BatchChatResponse з результатами обробки
        """
        if not messages:
            raise ValidationError("Список повідомлень не може бути порожнім")
        
        if len(messages) > 100:
            raise ValidationError("Максимальна кількість повідомлень - 100")
        
        # Валідація та нормалізація повідомлень
        validated_messages = []
        for msg in messages:
            if not msg.get("message") or not msg.get("user_id"):
                raise ValidationError("Кожне повідомлення повинно містити message та user_id")
            
            validated_messages.append({
                "message": normalize_text(msg["message"]),
                "user_id": sanitize_user_id(msg["user_id"]),
                "session_id": msg.get("session_id") or create_session_id(),
                "language": msg.get("language", "auto"),
                "use_memory": msg.get("use_memory", True),
                "use_medical_nlp": msg.get("use_medical_nlp", True),
                "use_graph_search": msg.get("use_graph_search", True),
                "fast_mode": msg.get("fast_mode", True),
                "context": msg.get("context", {})
            })
        
        # Виконання запиту
        request_data = {"messages": validated_messages}
        response_data = self._make_request("POST", "chat/batch", data=request_data)
        
        return BatchChatResponse(**response_data)
    
    def get_memory(
        self,
        user_id: str,
        memory_type: Optional[Union[str, MemoryType]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> MemoryResponse:
        """
        Отримання пам'яті користувача
        
        Args:
            user_id: ID користувача
            memory_type: Тип пам'яті
            limit: Кількість записів
            offset: Зміщення
            start_date: Початкова дата
            end_date: Кінцева дата
            
        Returns:
            MemoryResponse з спогадами користувача
        """
        if not user_id:
            raise ValidationError("User ID не може бути порожнім")
        
        user_id = sanitize_user_id(user_id)
        
        # Підготовка параметрів
        params = {}
        if memory_type:
            if isinstance(memory_type, MemoryType):
                params["memory_type"] = memory_type.value
            else:
                params["memory_type"] = str(memory_type)
        
        if limit is not None:
            params["limit"] = min(max(limit, 1), 1000)
        
        if offset is not None:
            params["offset"] = max(offset, 0)
        
        if start_date:
            params["start_date"] = start_date.isoformat()
        
        if end_date:
            params["end_date"] = end_date.isoformat()
        
        # Виконання запиту
        response_data = self._make_request("GET", f"memory/{user_id}", params=params)
        
        return MemoryResponse(**response_data)
    
    def extract_entities(
        self,
        text: str,
        entity_types: Optional[List[Union[str, EntityType]]] = None,
        language: Optional[Union[str, Language]] = None,
        medical_mode: bool = False
    ) -> EntityResponse:
        """
        Витягування сутностей з тексту
        
        Args:
            text: Текст для аналізу
            entity_types: Типи сутностей для пошуку
            language: Мова тексту
            medical_mode: Медичний режим
            
        Returns:
            EntityResponse з знайденими сутностями
        """
        if not text or not text.strip():
            raise ValidationError("Текст не може бути порожнім")
        
        text = normalize_text(text)
        
        # Підготовка entity_types
        if entity_types:
            processed_types = []
            for entity_type in entity_types:
                if isinstance(entity_type, EntityType):
                    processed_types.append(entity_type.value)
                else:
                    processed_types.append(str(entity_type))
        else:
            processed_types = None
        
        # Автоматичне визначення мови
        if language is None or language == "auto":
            language = detect_language(text)
        elif isinstance(language, Language):
            language = language.value
        
        # Підготовка даних запиту
        request_data = {
            "text": text,
            "entity_types": processed_types,
            "language": language,
            "medical_mode": medical_mode
        }
        
        # Виконання запиту
        response_data = self._make_request("POST", "entities", data=request_data)
        
        return EntityResponse(**response_data)
    
    def search_graph(
        self,
        query: str,
        user_id: Optional[str] = None,
        depth: Optional[int] = None,
        limit: Optional[int] = None
    ) -> GraphResponse:
        """
        Пошук в графі знань
        
        Args:
            query: Запит до графу
            user_id: ID користувача для персоналізації
            depth: Глибина пошуку
            limit: Ліміт результатів
            
        Returns:
            GraphResponse з результатами пошуку
        """
        if not query or not query.strip():
            raise ValidationError("Запит не може бути порожнім")
        
        query = normalize_text(query)
        
        if user_id:
            user_id = sanitize_user_id(user_id)
        
        # Підготовка даних запиту
        request_data = {
            "query": query,
            "user_id": user_id,
            "depth": min(max(depth or 3, 1), 10),
            "limit": min(max(limit or 50, 1), 1000)
        }
        
        # Виконання запиту
        response_data = self._make_request("POST", "graph", data=request_data)
        
        return GraphResponse(**response_data)
    
    def health_check(self) -> HealthCheck:
        """
        Перевірка здоров'я системи
        
        Returns:
            HealthCheck з інформацією про стан системи
        """
        response_data = self._make_request("GET", "health")
        return HealthCheck(**response_data)
    
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Отримання профілю користувача
        
        Args:
            user_id: ID користувача
            
        Returns:
            Словник з інформацією про користувача
        """
        if not user_id:
            raise ValidationError("User ID не може бути порожнім")
        
        user_id = sanitize_user_id(user_id)
        response_data = self._make_request("GET", f"users/{user_id}/profile")
        
        return response_data
    
    def update_user_profile(
        self,
        user_id: str,
        profile_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Оновлення профілю користувача
        
        Args:
            user_id: ID користувача
            profile_data: Дані профілю для оновлення
            
        Returns:
            Оновлений профіль користувача
        """
        if not user_id:
            raise ValidationError("User ID не може бути порожнім")
        
        user_id = sanitize_user_id(user_id)
        response_data = self._make_request("PUT", f"users/{user_id}/profile", data=profile_data)
        
        return response_data
    
    def delete_user_memory(
        self,
        user_id: str,
        memory_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Видалення пам'яті користувача
        
        Args:
            user_id: ID користувача
            memory_id: ID конкретного спогаду (опційно)
            
        Returns:
            Результат видалення
        """
        if not user_id:
            raise ValidationError("User ID не може бути порожнім")
        
        user_id = sanitize_user_id(user_id)
        
        if memory_id:
            endpoint = f"memory/{user_id}/{memory_id}"
        else:
            endpoint = f"memory/{user_id}"
        
        response_data = self._make_request("DELETE", endpoint)
        
        return response_data
    
    def get_analytics(
        self,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Отримання аналітики
        
        Args:
            user_id: ID користувача (опційно)
            start_date: Початкова дата
            end_date: Кінцева дата
            metrics: Список метрик
            
        Returns:
            Аналітичні дані
        """
        params = {}
        
        if user_id:
            params["user_id"] = sanitize_user_id(user_id)
        
        if start_date:
            params["start_date"] = start_date.isoformat()
        
        if end_date:
            params["end_date"] = end_date.isoformat()
        
        if metrics:
            params["metrics"] = ",".join(metrics)
        
        response_data = self._make_request("GET", "analytics", params=params)
        
        return response_data
    
    def clear_cache(self):
        """Очищення кешу"""
        self._cache.clear()
        self.logger.info("Кеш очищено")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Отримання статистики кешу"""
        return {
            "cache_size": len(self._cache),
            "max_cache_size": self.config.max_cache_size,
            "cache_enabled": self.config.enable_cache
        }
    
    def close(self):
        """Закриття клієнта та очищення ресурсів"""
        self.session.close()
        self.clear_cache()
        self.logger.info("ODAM Client закрито")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    def __repr__(self) -> str:
        """String representation"""
        return f"ODAMClient(base_url='{self.config.base_url}', api_key='{self.config.api_key[:8]}...')" 