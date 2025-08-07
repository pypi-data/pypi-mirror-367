"""
Тести для ODAM V4 SDK Client
============================

Unit тести для перевірки функціональності SDK.
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Додаємо шлях до SDK
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from odam_sdk import ODAMClient, Language, MemoryType, EntityType
from odam_sdk.models import (
    ChatResponse, MemoryResponse, EntityResponse, GraphResponse,
    AuthenticationError, ValidationError, ServerError
)


class TestODAMClient:
    """Тести для ODAMClient"""
    
    def setup_method(self):
        """Налаштування перед кожним тестом"""
        self.api_key = "test_api_key_123"
        self.base_url = "https://api.odam.dev"
        
        # Мок відповіді для чату
        self.mock_chat_response = {
            "response": "Привіт! Як справи?",
            "user_id": "test_user_123",
            "session_id": "session_456",
            "processing_time": 0.1,
            "language_info": {
                "language": "uk",
                "confidence": 0.99
            },
            "entities": [
                {
                    "text": "Привіт",
                    "type": "GREETING",
                    "confidence": 0.95,
                    "start": 0,
                    "end": 6
                }
            ],
            "typed_entities": [],
            "extracted_entities": [],
            "memory_stats": {
                "memories_found": 2,
                "memories_created": 1,
                "memory_layers": ["episodic", "semantic"],
                "memory_strength": 0.85
            },
            "search_results": {
                "vector_results": 5,
                "bm25_results": 3,
                "graph_results": 1
            },
            "personalization_score": 0.78,
            "v7_metrics": {
                "memory_utilization_score": 0.85,
                "medical_safety_level": "strict",
                "fallback_used": False,
                "context_injection_success": 0.95
            },
            "timestamp": "2024-01-01T00:00:00Z",
            "request_id": "req_123"
        }
        
        # Мок відповіді для пам'яті
        self.mock_memory_response = {
            "user_id": "test_user_123",
            "memories": [
                {
                    "id": "mem_1",
                    "type": "episodic",
                    "content": "Користувач привітався",
                    "entities": ["GREETING"],
                    "emotional_state": "positive",
                    "confidence": 0.95,
                    "timestamp": "2024-01-01T00:00:00Z",
                    "context": {}
                }
            ],
            "total_count": 1,
            "memory_type": "episodic",
            "processing_time": 0.05
        }
        
        # Мок відповіді для сутностей
        self.mock_entity_response = {
            "entities": [
                {
                    "text": "Іван Петренко",
                    "type": "Person",
                    "confidence": 0.95,
                    "start": 0,
                    "end": 13
                }
            ],
            "typed_entities": [],
            "language": "uk",
            "processing_time": 0.03,
            "medical_mode": True
        }
        
        # Мок відповіді для графу
        self.mock_graph_response = {
            "nodes": [
                {
                    "id": "node_1",
                    "label": "Лікар",
                    "properties": {"type": "profession"}
                }
            ],
            "relationships": [
                {
                    "id": "rel_1",
                    "type": "WORKS_AT",
                    "start_node": "node_1",
                    "end_node": "node_2",
                    "properties": {}
                }
            ],
            "query": "лікарі в Києві",
            "processing_time": 0.1,
            "depth": 3
        }
    
    def test_client_initialization(self):
        """Тест ініціалізації клієнта"""
        client = ODAMClient(api_key=self.api_key)
        
        assert client.config.api_key == self.api_key
        assert client.config.base_url == "https://api.odam.dev"
        assert client.config.timeout == 30
    
    def test_client_initialization_with_config(self):
        """Тест ініціалізації клієнта з конфігурацією"""
        from odam_sdk.config import ODAMConfig
        
        config = ODAMConfig(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=60,
            enterprise_v7_enabled=True
        )
        
        client = ODAMClient(config=config)
        
        assert client.config.api_key == self.api_key
        assert client.config.base_url == self.base_url
        assert client.config.timeout == 60
        assert client.config.enterprise_v7_enabled is True
    
    def test_client_initialization_without_api_key(self):
        """Тест ініціалізації без API ключа"""
        with pytest.raises(AuthenticationError):
            ODAMClient(api_key="")
    
    @patch('odam_sdk.client.requests.Session')
    def test_chat_success(self, mock_session):
        """Тест успішного чату"""
        # Налаштування моку
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_chat_response
        mock_response.content = b'{"response": "test"}'
        
        mock_session_instance = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        client = ODAMClient(api_key=self.api_key)
        
        # Виконання тесту
        response = client.chat(
            message="Привіт!",
            user_id="test_user_123"
        )
        
        # Перевірки
        assert isinstance(response, ChatResponse)
        assert response.response == "Привіт! Як справи?"
        assert response.user_id == "test_user_123"
        assert response.language_info.language == "uk"
        assert len(response.entities) == 1
        assert response.entities[0].text == "Привіт"
        assert response.memory_stats.memories_found == 2
        assert response.personalization_score == 0.78
        
        # Перевірка виклику API
        mock_session_instance.request.assert_called_once()
        call_args = mock_session_instance.request.call_args
        assert call_args[1]['method'] == 'POST'
        assert 'chat' in call_args[1]['url']
    
    @patch('odam_sdk.client.requests.Session')
    def test_chat_validation_error(self, mock_session):
        """Тест помилки валідації в чаті"""
        mock_response = Mock()
        mock_response.status_code = 422
        mock_response.text = "Validation error"
        
        mock_session_instance = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        client = ODAMClient(api_key=self.api_key)
        
        with pytest.raises(ValidationError):
            client.chat(message="", user_id="test_user_123")
    
    @patch('odam_sdk.client.requests.Session')
    def test_chat_authentication_error(self, mock_session):
        """Тест помилки автентифікації в чаті"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        
        mock_session_instance = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        client = ODAMClient(api_key=self.api_key)
        
        with pytest.raises(AuthenticationError):
            client.chat(message="Привіт!", user_id="test_user_123")
    
    @patch('odam_sdk.client.requests.Session')
    def test_get_memory_success(self, mock_session):
        """Тест успішного отримання пам'яті"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_memory_response
        mock_response.content = b'{"memories": []}'
        
        mock_session_instance = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        client = ODAMClient(api_key=self.api_key)
        
        response = client.get_memory(
            user_id="test_user_123",
            memory_type=MemoryType.EPISODIC
        )
        
        assert isinstance(response, MemoryResponse)
        assert response.user_id == "test_user_123"
        assert len(response.memories) == 1
        assert response.memories[0].content == "Користувач привітався"
        assert response.memory_type == MemoryType.EPISODIC
    
    @patch('odam_sdk.client.requests.Session')
    def test_extract_entities_success(self, mock_session):
        """Тест успішного витягування сутностей"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_entity_response
        mock_response.content = b'{"entities": []}'
        
        mock_session_instance = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        client = ODAMClient(api_key=self.api_key)
        
        response = client.extract_entities(
            text="Іван Петренко прийшов на прийом",
            medical_mode=True
        )
        
        assert isinstance(response, EntityResponse)
        assert len(response.entities) == 1
        assert response.entities[0].text == "Іван Петренко"
        assert response.entities[0].type == "Person"
        assert response.medical_mode is True
    
    @patch('odam_sdk.client.requests.Session')
    def test_search_graph_success(self, mock_session):
        """Тест успішного пошуку в графі"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_graph_response
        mock_response.content = b'{"nodes": []}'
        
        mock_session_instance = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        client = ODAMClient(api_key=self.api_key)
        
        response = client.search_graph(
            query="лікарі в Києві",
            user_id="test_user_123",
            depth=3
        )
        
        assert isinstance(response, GraphResponse)
        assert response.query == "лікарі в Києві"
        assert len(response.nodes) == 1
        assert len(response.relationships) == 1
        assert response.depth == 3
    
    def test_chat_validation(self):
        """Тест валідації вхідних даних для чату"""
        client = ODAMClient(api_key=self.api_key)
        
        # Тест порожнього повідомлення
        with pytest.raises(ValidationError):
            client.chat(message="", user_id="test_user_123")
        
        # Тест порожнього user_id
        with pytest.raises(ValidationError):
            client.chat(message="Привіт!", user_id="")
        
        # Тест занадто довгого повідомлення
        long_message = "a" * 10001
        with pytest.raises(ValidationError):
            client.chat(message=long_message, user_id="test_user_123")
    
    def test_memory_validation(self):
        """Тест валідації для пам'яті"""
        client = ODAMClient(api_key=self.api_key)
        
        with pytest.raises(ValidationError):
            client.get_memory(user_id="")
    
    def test_entities_validation(self):
        """Тест валідації для сутностей"""
        client = ODAMClient(api_key=self.api_key)
        
        with pytest.raises(ValidationError):
            client.extract_entities(text="")
    
    def test_graph_validation(self):
        """Тест валідації для графу"""
        client = ODAMClient(api_key=self.api_key)
        
        with pytest.raises(ValidationError):
            client.search_graph(query="")
    
    def test_context_manager(self):
        """Тест context manager"""
        with ODAMClient(api_key=self.api_key) as client:
            assert client.config.api_key == self.api_key
            # Клієнт автоматично закриється після виходу з контексту
    
    def test_repr(self):
        """Тест string representation"""
        client = ODAMClient(api_key=self.api_key)
        repr_str = repr(client)
        
        assert "ODAMClient" in repr_str
        assert "test_api_key_123" in repr_str
        assert "https://api.odam.dev" in repr_str
    
    def test_cache_operations(self):
        """Тест операцій з кешем"""
        client = ODAMClient(api_key=self.api_key)
        
        # Тест статистики кешу
        cache_stats = client.get_cache_stats()
        assert "cache_size" in cache_stats
        assert "max_cache_size" in cache_stats
        assert "cache_enabled" in cache_stats
        
        # Тест очищення кешу
        client.clear_cache()
        cache_stats_after = client.get_cache_stats()
        assert cache_stats_after["cache_size"] == 0


class TestODAMClientErrors:
    """Тести для обробки помилок"""
    
    def test_network_error(self):
        """Тест обробки мережевої помилки"""
        with patch('odam_sdk.client.requests.Session') as mock_session:
            mock_session_instance = Mock()
            mock_session_instance.request.side_effect = Exception("Network error")
            mock_session.return_value = mock_session_instance
            
            client = ODAMClient(api_key="test_key")
            
            with pytest.raises(ServerError):
                client.chat(message="Привіт!", user_id="test_user_123")
    
    def test_rate_limit_error(self):
        """Тест обробки помилки ліміту запитів"""
        with patch('odam_sdk.client.requests.Session') as mock_session:
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.text = "Rate limit exceeded"
            
            mock_session_instance = Mock()
            mock_session_instance.request.return_value = mock_response
            mock_session.return_value = mock_session_instance
            
            client = ODAMClient(api_key="test_key")
            
            with pytest.raises(ServerError):  # RateLimitError наслідується від ServerError
                client.chat(message="Привіт!", user_id="test_user_123")
    
    def test_server_error(self):
        """Тест обробки помилки сервера"""
        with patch('odam_sdk.client.requests.Session') as mock_session:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Internal server error"
            
            mock_session_instance = Mock()
            mock_session_instance.request.return_value = mock_response
            mock_session.return_value = mock_session_instance
            
            client = ODAMClient(api_key="test_key")
            
            with pytest.raises(ServerError):
                client.chat(message="Привіт!", user_id="test_user_123")


class TestODAMClientConfiguration:
    """Тести для конфігурації клієнта"""
    
    def test_config_from_environment(self):
        """Тест завантаження конфігурації з environment variables"""
        with patch.dict(os.environ, {
            'ODAM_API_KEY': 'env_test_key',
            'ODAM_BASE_URL': 'https://test.odam.dev',
            'ODAM_TIMEOUT': '60'
        }):
            client = ODAMClient()
            assert client.config.api_key == 'env_test_key'
            assert client.config.base_url == 'https://test.odam.dev'
            assert client.config.timeout == 60
    
    def test_config_validation(self):
        """Тест валідації конфігурації"""
        # Тест невалідного API ключа
        with pytest.raises(AuthenticationError):
            ODAMClient(api_key="")
        
        # Тест невалідного URL
        with pytest.raises(ValueError):
            ODAMClient(api_key="test_key", base_url="invalid_url")
        
        # Тест невалідного таймауту
        with pytest.raises(ValueError):
            ODAMClient(api_key="test_key", timeout=0)


if __name__ == "__main__":
    pytest.main([__file__]) 