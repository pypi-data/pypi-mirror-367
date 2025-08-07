# 🧠 ODAM V4 Python SDK

[![PyPI version](https://badge.fury.io/py/odam-sdk.svg)](https://badge.fury.io/py/odam-sdk)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://docs.odam.dev)

Офіційний Python SDK для інтеграції з **ODAM V4** - революційною системою штучного інтелекту з людською пам'яттю.

## 🌟 Особливості

- **🧠 Розумні чат-відповіді** з контекстуальною пам'яттю
- **💾 Система людської пам'яті** - запам'ятовує кожного користувача назавжди
- **🏥 Медичні NLP сутності** з точністю 90%+
- **🌐 Багатомовність** - підтримка 15+ мов з автоматичним визначенням
- **🕸️ Граф знань** - складні взаємозв'язки між сутностями
- **🎨 Персоналізація** - унікальний досвід для кожного користувача
- **⚡ Real-time обробка** - відповідь за < 100мс
- **🚀 Enterprise V7** - 98-100% персоналізація з Memory Enforcement
- **🛡️ Medical Safety** - гарантована медична безпека

## 📦 Встановлення

```bash
# Встановлення з PyPI
pip install odam-sdk

# Або з GitHub
pip install git+https://github.com/odam-ai/odam-sdk-python.git
```

## 🚀 Швидкий старт

### Базовий приклад

```python
from odam_sdk import ODAMClient

# Створення клієнта
client = ODAMClient(api_key="your_api_key")

# Відправка повідомлення
response = client.chat(
    message="Привіт! Як справи?",
    user_id="user_123"
)

print(response.response)
print(f"Сутності: {response.entities}")
print(f"Пам'ять оновлена: {response.memory_stats.memories_created}")
```

### Розширений приклад

```python
from odam_sdk import ODAMClient, Language, MemoryType

# Створення клієнта з налаштуваннями
client = ODAMClient(
    api_key="your_api_key",
    base_url="https://api.odam.dev",
    timeout=30,
    enable_logging=True
)

# Відправка повідомлення з усіма опціями
response = client.chat(
    message="Я хочу записатися до лікаря на наступний тиждень",
    user_id="user_maria_456",
    session_id="session_789",
    language=Language.UKRAINIAN,
    use_memory=True,
    use_medical_nlp=True,
    use_graph_search=True,
    enterprise_v7=True,
    medical_safety=True,
    context={
        "source": "mobile_app",
        "location": "kyiv",
        "user_type": "patient"
    }
)

# Аналіз відповіді
print(f"Відповідь: {response.response}")
print(f"Мова: {response.language_info.language}")
print(f"Сутності: {len(response.entities)} знайдено")
print(f"Пам'ять: {response.memory_stats.memories_found} спогадів знайдено")
print(f"Персоналізація: {response.personalization_score:.2%}")

# Отримання пам'яті користувача
memories = client.get_memory(
    user_id="user_maria_456",
    memory_type=MemoryType.EPISODIC,
    limit=10
)

print(f"Спогади користувача: {len(memories.memories)}")
```

## 📚 Основні методи

### 💬 Чат

```python
# Простий чат
response = client.chat("Привіт!", "user_123")

# Чат з контекстом
response = client.chat(
    message="Нагадай мені про зустріч",
    user_id="user_123",
    context={"app": "calendar", "priority": "high"}
)

# Batch обробка
messages = [
    {"message": "Привіт!", "user_id": "user_1"},
    {"message": "Як справи?", "user_id": "user_2"}
]
batch_response = client.chat_batch(messages)
```

### 🧠 Пам'ять

```python
# Отримання всіх спогадів
memories = client.get_memory("user_123")

# Отримання конкретного типу пам'яті
episodic_memories = client.get_memory(
    user_id="user_123",
    memory_type=MemoryType.EPISODIC,
    limit=20
)

# Отримання пам'яті за період
recent_memories = client.get_memory(
    user_id="user_123",
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 12, 31)
)
```

### 🏥 Сутності

```python
# Витягування сутностей
entities = client.extract_entities(
    text="Доктор Петренко призначив аспірин 500мг 2 рази на день",
    medical_mode=True
)

print(f"Знайдено сутностей: {len(entities.entities)}")
for entity in entities.entities:
    print(f"- {entity.text} ({entity.type})")
```

### 🕸️ Граф знань

```python
# Пошук в графі знань
graph_results = client.search_graph(
    query="лікарі в Києві",
    user_id="user_123",
    depth=3,
    limit=50
)

print(f"Знайдено вузлів: {len(graph_results.nodes)}")
print(f"Знайдено зв'язків: {len(graph_results.relationships)}")
```

### 📊 Аналітика

```python
# Отримання аналітики
analytics = client.get_analytics(
    user_id="user_123",
    start_date=datetime(2024, 1, 1),
    metrics=["conversations", "entities", "memory_usage"]
)

print(f"Аналітика: {analytics}")
```

## ⚙️ Конфігурація

### Environment Variables

```bash
# .env файл
ODAM_API_KEY=your_api_key_here
ODAM_BASE_URL=https://api.odam.dev
ODAM_TIMEOUT=30
ODAM_LOG_LEVEL=INFO
ODAM_ENABLE_CACHE=true
```

### Програмна конфігурація

```python
from odam_sdk import ODAMClient, ODAMConfig

# Створення конфігурації
config = ODAMConfig(
    api_key="your_api_key",
    base_url="https://api.odam.dev",
    timeout=30,
    max_retries=3,
    enable_logging=True,
    enable_cache=True,
    enterprise_v7_enabled=True,
    medical_safety_enabled=True
)

# Створення клієнта з конфігурацією
client = ODAMClient(config=config)
```

## 🔧 Розширені можливості

### Context Manager

```python
# Автоматичне закриття ресурсів
with ODAMClient(api_key="your_key") as client:
    response = client.chat("Привіт!", "user_123")
    print(response.response)
```

### Retry логіка

```python
# Автоматичні повторні спроби при помилках
@retry_on_failure(max_retries=5, delay=2.0)
def send_message(client, message, user_id):
    return client.chat(message, user_id)
```

### Кешування

```python
# Отримання статистики кешу
cache_stats = client.get_cache_stats()
print(f"Розмір кешу: {cache_stats['cache_size']}")

# Очищення кешу
client.clear_cache()
```

### Логування

```python
import logging

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("odam_sdk")

# Логування запитів та відповідей
client = ODAMClient(
    api_key="your_key",
    log_requests=True,
    log_responses=True
)
```

## 🏥 Медичні можливості

### Медичні сутності

```python
# Автоматичне витягування медичних сутностей
medical_text = """
Пацієнт: Іван Петренко, 45 років
Діагноз: Гіпертонія
Лікування: Еналаприл 10мг 1 раз на день
Алергії: Пеніцилін
"""

entities = client.extract_entities(
    text=medical_text,
    medical_mode=True
)

for entity in entities.entities:
    if entity.type in ["Person", "Medication", "Condition"]:
        print(f"Медична сутність: {entity.text} ({entity.type})")
```

### Medical Safety

```python
# Безпечна медична обробка
response = client.chat(
    message="У мене біль у грудях",
    user_id="patient_123",
    medical_safety=True,
    enterprise_v7=True
)

# Система автоматично додасть медичні попередження
print(response.response)
```

## 🌐 Багатомовність

### Автоматичне визначення мови

```python
# Автоматичне визначення мови
response = client.chat(
    message="Hello, how are you?",  # Англійська
    user_id="user_123"
)
print(f"Визначена мова: {response.language_info.language}")

response = client.chat(
    message="Привіт, як справи?",  # Українська
    user_id="user_123"
)
print(f"Визначена мова: {response.language_info.language}")
```

### Явне вказання мови

```python
from odam_sdk import Language

response = client.chat(
    message="Bonjour, comment allez-vous?",
    user_id="user_123",
    language=Language.FRENCH
)
```

## 🚀 Enterprise V7

### Memory Enforcement

```python
# Примусова персоналізація
response = client.chat(
    message="Нагадай мені про мої уподобання",
    user_id="user_123",
    memory_enforcement=True,
    enterprise_v7=True
)

print(f"Використання пам'яті: {response.v7_metrics.memory_utilization_score:.2%}")
```

### Senior Fallback

```python
# Примусова конвертація сутностей
response = client.chat(
    message="Я бачу лікаря",
    user_id="user_123",
    fallback_enabled=True,
    enterprise_v7=True
)

print(f"Використано fallback: {response.v7_metrics.fallback_used}")
```

## 📊 Моніторинг та метрики

### Health Check

```python
# Перевірка здоров'я системи
health = client.health_check()
print(f"Статус: {health.status}")
print(f"Версія: {health.version}")
print(f"Uptime: {health.uptime:.2f} секунд")
```

### Метрики продуктивності

```python
response = client.chat("Привіт!", "user_123")

print(f"Час обробки: {response.processing_time:.3f}с")
print(f"Персоналізація: {response.personalization_score:.2%}")
print(f"Результати пошуку: {response.search_results}")
```

## 🔒 Безпека

### Валідація API ключа

```python
from odam_sdk import validate_api_key

# Перевірка API ключа
if validate_api_key("your_api_key"):
    print("API ключ валідний")
else:
    print("API ключ невалідний")
```

### Безпечне зберігання

```python
import os

# Рекомендований спосіб зберігання API ключа
api_key = os.getenv("ODAM_API_KEY")
client = ODAMClient(api_key=api_key)
```

## 🧪 Тестування

### Unit тести

```python
import pytest
from unittest.mock import Mock
from odam_sdk import ODAMClient

def test_chat_response():
    # Мок відповіді
    mock_response = {
        "response": "Привіт! Як справи?",
        "user_id": "user_123",
        "processing_time": 0.1,
        "language_info": {"language": "uk", "confidence": 0.99},
        "entities": [],
        "memory_stats": {"memories_found": 0, "memories_created": 1},
        "search_results": {"vector_results": 0, "bm25_results": 0, "graph_results": 0},
        "personalization_score": 0.5,
        "timestamp": "2024-01-01T00:00:00Z"
    }
    
    # Тестування
    client = ODAMClient(api_key="test_key")
    client._make_request = Mock(return_value=mock_response)
    
    response = client.chat("Привіт!", "user_123")
    assert response.response == "Привіт! Як справи?"
    assert response.user_id == "user_123"
```

## 📖 Повна документація

- 📚 [API Reference](https://docs.odam.dev/api)
- 🚀 [Quick Start Guide](https://docs.odam.dev/quickstart)
- 🏥 [Medical NLP Guide](https://docs.odam.dev/medical)
- 🌐 [Multilingual Support](https://docs.odam.dev/multilingual)
- 🚀 [Enterprise V7 Features](https://docs.odam.dev/enterprise)
- 🔧 [Configuration Guide](https://docs.odam.dev/configuration)
- 🧪 [Testing Guide](https://docs.odam.dev/testing)
- 📊 [Analytics & Monitoring](https://docs.odam.dev/analytics)

## 🤝 Підтримка

- 📧 Email: support@odam.dev
- 💬 Discord: [ODAM Community](https://discord.gg/odam)
- 📖 Documentation: [docs.odam.dev](https://docs.odam.dev)
- 🐛 Issues: [GitHub Issues](https://github.com/odam-ai/odam-sdk-python/issues)
- 💡 Discussions: [GitHub Discussions](https://github.com/odam-ai/odam-sdk-python/discussions)

## 📄 Ліцензія

Цей проект ліцензовано під MIT License - дивіться файл [LICENSE](LICENSE) для деталей.

## 🙏 Подяки

Дякуємо всім спільноті ODAM за внесок у розвиток цього SDK!

---

**🧠 ODAM V4 - Майбутнє штучного інтелекту вже тут!** 