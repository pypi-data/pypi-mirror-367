#!/usr/bin/env python3
"""
ODAM V4 SDK CLI
===============

Командний рядок інтерфейс для ODAM V4 SDK.
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Optional, Dict, Any

# Додаємо шлях до SDK
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from odam_sdk import ODAMClient, Language, MemoryType, EntityType


def setup_parser():
    """Налаштування парсера аргументів"""
    parser = argparse.ArgumentParser(
        description="ODAM V4 SDK Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Приклади використання:
  %(prog)s chat "Привіт!" --user-id user123
  %(prog)s entities "Текст для аналізу" --medical
  %(prog)s memory user123 --type episodic --limit 10
  %(prog)s graph "пошуковий запит" --depth 3
  %(prog)s health
        """
    )
    
    # Загальні опції
    parser.add_argument(
        "--api-key",
        default=os.getenv("ODAM_API_KEY"),
        help="API ключ ODAM (за замовчуванням з ODAM_API_KEY env)"
    )
    parser.add_argument(
        "--base-url",
        default="https://api.odam.dev",
        help="Базовий URL API (за замовчуванням: https://api.odam.dev)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Таймаут запиту в секундах (за замовчуванням: 30)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Детальний вивід"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Вивід в JSON форматі"
    )
    
    # Підкоманди
    subparsers = parser.add_subparsers(dest="command", help="Доступні команди")
    
    # Команда chat
    chat_parser = subparsers.add_parser("chat", help="Відправка повідомлення")
    chat_parser.add_argument("message", help="Повідомлення для відправки")
    chat_parser.add_argument("--user-id", required=True, help="ID користувача")
    chat_parser.add_argument("--session-id", help="ID сесії")
    chat_parser.add_argument("--language", choices=["uk", "en", "ru", "auto"], default="auto", help="Мова")
    chat_parser.add_argument("--no-memory", action="store_true", help="Не використовувати пам'ять")
    chat_parser.add_argument("--no-medical", action="store_true", help="Не використовувати медичні NLP")
    chat_parser.add_argument("--no-graph", action="store_true", help="Не використовувати граф пошук")
    chat_parser.add_argument("--enterprise", action="store_true", help="Використовувати Enterprise V7")
    chat_parser.add_argument("--medical-safety", action="store_true", help="Увімкнути Medical Safety")
    chat_parser.add_argument("--memory-enforcement", action="store_true", help="Увімкнути Memory Enforcement")
    chat_parser.add_argument("--context", help="JSON контекст")
    
    # Команда entities
    entities_parser = subparsers.add_parser("entities", help="Витягування сутностей")
    entities_parser.add_argument("text", help="Текст для аналізу")
    entities_parser.add_argument("--medical", action="store_true", help="Медичний режим")
    entities_parser.add_argument("--language", choices=["uk", "en", "ru", "auto"], default="auto", help="Мова")
    entities_parser.add_argument("--types", help="Типи сутностей (через кому)")
    
    # Команда memory
    memory_parser = subparsers.add_parser("memory", help="Робота з пам'яттю")
    memory_parser.add_argument("user_id", help="ID користувача")
    memory_parser.add_argument("--type", choices=["episodic", "semantic", "emotional", "all"], default="all", help="Тип пам'яті")
    memory_parser.add_argument("--limit", type=int, default=50, help="Кількість записів")
    memory_parser.add_argument("--offset", type=int, default=0, help="Зміщення")
    memory_parser.add_argument("--start-date", help="Початкова дата (YYYY-MM-DD)")
    memory_parser.add_argument("--end-date", help="Кінцева дата (YYYY-MM-DD)")
    
    # Команда graph
    graph_parser = subparsers.add_parser("graph", help="Пошук в графі знань")
    graph_parser.add_argument("query", help="Пошуковий запит")
    graph_parser.add_argument("--user-id", help="ID користувача для персоналізації")
    graph_parser.add_argument("--depth", type=int, default=3, help="Глибина пошуку")
    graph_parser.add_argument("--limit", type=int, default=50, help="Ліміт результатів")
    
    # Команда health
    health_parser = subparsers.add_parser("health", help="Перевірка здоров'я системи")
    
    # Команда analytics
    analytics_parser = subparsers.add_parser("analytics", help="Отримання аналітики")
    analytics_parser.add_argument("--user-id", help="ID користувача")
    analytics_parser.add_argument("--start-date", help="Початкова дата (YYYY-MM-DD)")
    analytics_parser.add_argument("--end-date", help="Кінцева дата (YYYY-MM-DD)")
    analytics_parser.add_argument("--metrics", help="Метрики (через кому)")
    
    return parser


def create_client(args) -> ODAMClient:
    """Створення клієнта"""
    if not args.api_key:
        print("❌ Помилка: API ключ не вказано. Встановіть ODAM_API_KEY environment variable або використайте --api-key")
        sys.exit(1)
    
    return ODAMClient(
        api_key=args.api_key,
        base_url=args.base_url,
        timeout=args.timeout,
        enterprise_v7_enabled=args.enterprise,
        medical_safety_enabled=args.medical_safety
    )


def print_result(data: Any, json_output: bool = False):
    """Вивід результату"""
    if json_output:
        print(json.dumps(data, indent=2, ensure_ascii=False, default=str))
    else:
        if isinstance(data, dict):
            for key, value in data.items():
                print(f"{key}: {value}")
        else:
            print(data)


def handle_chat(args):
    """Обробка команди chat"""
    client = create_client(args)
    
    # Парсинг контексту
    context = {}
    if args.context:
        try:
            context = json.loads(args.context)
        except json.JSONDecodeError:
            print("❌ Помилка: Невірний JSON формат контексту")
            return
    
    try:
        response = client.chat(
            message=args.message,
            user_id=args.user_id,
            session_id=args.session_id,
            language=args.language,
            use_memory=not args.no_memory,
            use_medical_nlp=not args.no_medical,
            use_graph_search=not args.no_graph,
            enterprise_v7=args.enterprise,
            medical_safety=args.medical_safety,
            memory_enforcement=args.memory_enforcement,
            context=context
        )
        
        if args.json:
            print_result(response.dict(), json_output=True)
        else:
            print(f"Відповідь: {response.response}")
            print(f"Мова: {response.language_info.language}")
            print(f"Час обробки: {response.processing_time:.3f}с")
            print(f"Персоналізація: {response.personalization_score:.2%}")
            print(f"Сутності: {len(response.entities)}")
            print(f"Пам'ять: {response.memory_stats.memories_found} знайдено, {response.memory_stats.memories_created} створено")
            
            if response.v7_metrics:
                print(f"V7 метрики:")
                print(f"  Використання пам'яті: {response.v7_metrics.memory_utilization_score:.2%}")
                print(f"  Медична безпека: {response.v7_metrics.medical_safety_level}")
                print(f"  Fallback використано: {response.v7_metrics.fallback_used}")
    
    except Exception as e:
        print(f"❌ Помилка: {e}")
    finally:
        client.close()


def handle_entities(args):
    """Обробка команди entities"""
    client = create_client(args)
    
    # Парсинг типів сутностей
    entity_types = None
    if args.types:
        entity_types = [t.strip() for t in args.types.split(",")]
    
    try:
        response = client.extract_entities(
            text=args.text,
            entity_types=entity_types,
            language=args.language,
            medical_mode=args.medical
        )
        
        if args.json:
            print_result(response.dict(), json_output=True)
        else:
            print(f"Знайдено сутностей: {len(response.entities)}")
            print(f"Мова: {response.language}")
            print(f"Час обробки: {response.processing_time:.3f}с")
            print(f"Медичний режим: {response.medical_mode}")
            
            # Групуємо сутності за типами
            entities_by_type = {}
            for entity in response.entities:
                if entity.type not in entities_by_type:
                    entities_by_type[entity.type] = []
                entities_by_type[entity.type].append(entity)
            
            for entity_type, entity_list in entities_by_type.items():
                print(f"\n{entity_type}:")
                for entity in entity_list:
                    print(f"  - {entity.text} (впевненість: {entity.confidence:.1%})")
    
    except Exception as e:
        print(f"❌ Помилка: {e}")
    finally:
        client.close()


def handle_memory(args):
    """Обробка команди memory"""
    client = create_client(args)
    
    # Парсинг дат
    start_date = None
    end_date = None
    
    if args.start_date:
        try:
            start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
        except ValueError:
            print("❌ Помилка: Невірний формат дати. Використовуйте YYYY-MM-DD")
            return
    
    if args.end_date:
        try:
            end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
        except ValueError:
            print("❌ Помилка: Невірний формат дати. Використовуйте YYYY-MM-DD")
            return
    
    try:
        response = client.get_memory(
            user_id=args.user_id,
            memory_type=args.type,
            limit=args.limit,
            offset=args.offset,
            start_date=start_date,
            end_date=end_date
        )
        
        if args.json:
            print_result(response.dict(), json_output=True)
        else:
            print(f"Спогади користувача: {args.user_id}")
            print(f"Тип пам'яті: {response.memory_type}")
            print(f"Загальна кількість: {response.total_count}")
            print(f"Час обробки: {response.processing_time:.3f}с")
            print(f"Знайдено спогадів: {len(response.memories)}")
            
            for i, memory in enumerate(response.memories, 1):
                print(f"\n{i}. {memory.content[:100]}...")
                print(f"   Тип: {memory.type}")
                print(f"   Час: {memory.timestamp}")
                print(f"   Впевненість: {memory.confidence:.1%}")
                if memory.emotional_state:
                    print(f"   Емоція: {memory.emotional_state}")
    
    except Exception as e:
        print(f"❌ Помилка: {e}")
    finally:
        client.close()


def handle_graph(args):
    """Обробка команди graph"""
    client = create_client(args)
    
    try:
        response = client.search_graph(
            query=args.query,
            user_id=args.user_id,
            depth=args.depth,
            limit=args.limit
        )
        
        if args.json:
            print_result(response.dict(), json_output=True)
        else:
            print(f"Результати пошуку в графі знань")
            print(f"Запит: {response.query}")
            print(f"Глибина: {response.depth}")
            print(f"Час обробки: {response.processing_time:.3f}с")
            print(f"Знайдено вузлів: {len(response.nodes)}")
            print(f"Знайдено зв'язків: {len(response.relationships)}")
            
            if response.nodes:
                print(f"\nВузли:")
                for node in response.nodes[:10]:  # Показуємо перші 10
                    print(f"  - {node.label} (ID: {node.id})")
            
            if response.relationships:
                print(f"\nЗв'язки:")
                for rel in response.relationships[:10]:  # Показуємо перші 10
                    print(f"  - {rel.start_node} --[{rel.type}]--> {rel.end_node}")
    
    except Exception as e:
        print(f"❌ Помилка: {e}")
    finally:
        client.close()


def handle_health(args):
    """Обробка команди health"""
    client = create_client(args)
    
    try:
        response = client.health_check()
        
        if args.json:
            print_result(response.dict(), json_output=True)
        else:
            print(f"Статус системи: {response.status}")
            print(f"Версія API: {response.version}")
            print(f"Час роботи: {response.uptime:.2f} секунд")
            print(f"Час перевірки: {response.timestamp}")
            
            if response.components:
                print(f"\nКомпоненти:")
                for component, status in response.components.items():
                    print(f"  - {component}: {status}")
    
    except Exception as e:
        print(f"❌ Помилка: {e}")
    finally:
        client.close()


def handle_analytics(args):
    """Обробка команди analytics"""
    client = create_client(args)
    
    # Парсинг дат
    start_date = None
    end_date = None
    
    if args.start_date:
        try:
            start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
        except ValueError:
            print("❌ Помилка: Невірний формат дати. Використовуйте YYYY-MM-DD")
            return
    
    if args.end_date:
        try:
            end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
        except ValueError:
            print("❌ Помилка: Невірний формат дати. Використовуйте YYYY-MM-DD")
            return
    
    # Парсинг метрик
    metrics = None
    if args.metrics:
        metrics = [m.strip() for m in args.metrics.split(",")]
    
    try:
        response = client.get_analytics(
            user_id=args.user_id,
            start_date=start_date,
            end_date=end_date,
            metrics=metrics
        )
        
        if args.json:
            print_result(response, json_output=True)
        else:
            print("Аналітичні дані:")
            for key, value in response.items():
                print(f"  {key}: {value}")
    
    except Exception as e:
        print(f"❌ Помилка: {e}")
    finally:
        client.close()


def main():
    """Основний функція CLI"""
    parser = setup_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Налаштування логування
    if args.verbose:
        import logging
        logging.basicConfig(level=logging.INFO)
    
    # Обробка команд
    if args.command == "chat":
        handle_chat(args)
    elif args.command == "entities":
        handle_entities(args)
    elif args.command == "memory":
        handle_memory(args)
    elif args.command == "graph":
        handle_graph(args)
    elif args.command == "health":
        handle_health(args)
    elif args.command == "analytics":
        handle_analytics(args)
    else:
        print(f"❌ Невідома команда: {args.command}")
        parser.print_help()


if __name__ == "__main__":
    main() 