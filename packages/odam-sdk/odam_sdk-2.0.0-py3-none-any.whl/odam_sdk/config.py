"""
Конфігурація ODAM V4 SDK
========================

Цей модуль містить налаштування та конфігурацію для SDK.
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from pydantic_settings import BaseSettings
from pydantic import Field


@dataclass
class ODAMConfig:
    """Конфігурація ODAM SDK"""
    
    # API налаштування
    api_key: str = field(default_factory=lambda: os.getenv("ODAM_API_KEY", ""))
    base_url: str = field(default_factory=lambda: os.getenv("ODAM_BASE_URL", "https://api.odam.dev"))
    api_version: str = field(default="v1")
    
    # Таймаути
    timeout: int = field(default=30)
    connect_timeout: int = field(default=10)
    read_timeout: int = field(default=30)
    
    # Retry налаштування
    max_retries: int = field(default=3)
    retry_delay: float = field(default=1.0)
    backoff_factor: float = field(default=2.0)
    
    # Логування
    log_level: str = field(default="INFO")
    enable_logging: bool = field(default=True)
    log_requests: bool = field(default=True)
    log_responses: bool = field(default=False)
    
    # Кешування
    enable_cache: bool = field(default=True)
    cache_ttl: int = field(default=300)  # 5 хвилин
    max_cache_size: int = field(default=1000)
    
    # Моніторинг
    enable_metrics: bool = field(default=True)
    metrics_prefix: str = field(default="odam_sdk")
    
    # Безпека
    verify_ssl: bool = field(default=True)
    allow_insecure: bool = field(default=False)
    
    # Enterprise V7 налаштування
    enterprise_v7_enabled: bool = field(default=False)
    medical_safety_enabled: bool = field(default=False)
    memory_enforcement_enabled: bool = field(default=False)
    fallback_enabled: bool = field(default=False)
    
    # За замовчуванням
    default_language: str = field(default="auto")
    default_memory_type: str = field(default="all")
    default_entity_types: list = field(default_factory=list)
    
    def __post_init__(self):
        """Валідація конфігурації після ініціалізації"""
        if not self.api_key:
            raise ValueError("ODAM_API_KEY не встановлено")
        
        if not self.base_url.startswith(("http://", "https://")):
            raise ValueError("base_url повинен починатися з http:// або https://")
        
        if self.timeout <= 0:
            raise ValueError("timeout повинен бути більше 0")
        
        if self.max_retries < 0:
            raise ValueError("max_retries повинен бути >= 0")
    
    @property
    def api_url(self) -> str:
        """Повний URL API"""
        return f"{self.base_url}/api/{self.api_version}"
    
    @property
    def headers(self) -> Dict[str, str]:
        """Заголовки для запитів"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": f"ODAM-SDK-Python/1.0.0",
            "Accept": "application/json"
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертація в словник"""
        return {
            "api_key": self.api_key[:8] + "..." if self.api_key else None,
            "base_url": self.base_url,
            "api_version": self.api_version,
            "timeout": self.timeout,
            "connect_timeout": self.connect_timeout,
            "read_timeout": self.read_timeout,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "backoff_factor": self.backoff_factor,
            "log_level": self.log_level,
            "enable_logging": self.enable_logging,
            "log_requests": self.log_requests,
            "log_responses": self.log_responses,
            "enable_cache": self.enable_cache,
            "cache_ttl": self.cache_ttl,
            "max_cache_size": self.max_cache_size,
            "enable_metrics": self.enable_metrics,
            "metrics_prefix": self.metrics_prefix,
            "verify_ssl": self.verify_ssl,
            "allow_insecure": self.allow_insecure,
            "enterprise_v7_enabled": self.enterprise_v7_enabled,
            "medical_safety_enabled": self.medical_safety_enabled,
            "memory_enforcement_enabled": self.memory_enforcement_enabled,
            "fallback_enabled": self.fallback_enabled,
            "default_language": self.default_language,
            "default_memory_type": self.default_memory_type,
            "default_entity_types": self.default_entity_types
        }


class ODAMSettings(BaseSettings):
    """Налаштування з environment variables"""
    
    # API налаштування
    odam_api_key: str = Field(..., env="ODAM_API_KEY")
    odam_base_url: str = Field("https://api.odam.dev", env="ODAM_BASE_URL")
    odam_api_version: str = Field("v1", env="ODAM_API_VERSION")
    
    # Таймаути
    odam_timeout: int = Field(30, env="ODAM_TIMEOUT")
    odam_connect_timeout: int = Field(10, env="ODAM_CONNECT_TIMEOUT")
    odam_read_timeout: int = Field(30, env="ODAM_READ_TIMEOUT")
    
    # Retry налаштування
    odam_max_retries: int = Field(3, env="ODAM_MAX_RETRIES")
    odam_retry_delay: float = Field(1.0, env="ODAM_RETRY_DELAY")
    odam_backoff_factor: float = Field(2.0, env="ODAM_BACKOFF_FACTOR")
    
    # Логування
    odam_log_level: str = Field("INFO", env="ODAM_LOG_LEVEL")
    odam_enable_logging: bool = Field(True, env="ODAM_ENABLE_LOGGING")
    odam_log_requests: bool = Field(True, env="ODAM_LOG_REQUESTS")
    odam_log_responses: bool = Field(False, env="ODAM_LOG_RESPONSES")
    
    # Кешування
    odam_enable_cache: bool = Field(True, env="ODAM_ENABLE_CACHE")
    odam_cache_ttl: int = Field(300, env="ODAM_CACHE_TTL")
    odam_max_cache_size: int = Field(1000, env="ODAM_MAX_CACHE_SIZE")
    
    # Моніторинг
    odam_enable_metrics: bool = Field(True, env="ODAM_ENABLE_METRICS")
    odam_metrics_prefix: str = Field("odam_sdk", env="ODAM_METRICS_PREFIX")
    
    # Безпека
    odam_verify_ssl: bool = Field(True, env="ODAM_VERIFY_SSL")
    odam_allow_insecure: bool = Field(False, env="ODAM_ALLOW_INSECURE")
    
    # Enterprise V7 налаштування
    odam_enterprise_v7_enabled: bool = Field(False, env="ODAM_ENTERPRISE_V7_ENABLED")
    odam_medical_safety_enabled: bool = Field(False, env="ODAM_MEDICAL_SAFETY_ENABLED")
    odam_memory_enforcement_enabled: bool = Field(False, env="ODAM_MEMORY_ENFORCEMENT_ENABLED")
    odam_fallback_enabled: bool = Field(False, env="ODAM_FALLBACK_ENABLED")
    
    # За замовчуванням
    odam_default_language: str = Field("auto", env="ODAM_DEFAULT_LANGUAGE")
    odam_default_memory_type: str = Field("all", env="ODAM_DEFAULT_MEMORY_TYPE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def to_config(self) -> ODAMConfig:
        """Конвертація в ODAMConfig"""
        return ODAMConfig(
            api_key=self.odam_api_key,
            base_url=self.odam_base_url,
            api_version=self.odam_api_version,
            timeout=self.odam_timeout,
            connect_timeout=self.odam_connect_timeout,
            read_timeout=self.odam_read_timeout,
            max_retries=self.odam_max_retries,
            retry_delay=self.odam_retry_delay,
            backoff_factor=self.odam_backoff_factor,
            log_level=self.odam_log_level,
            enable_logging=self.odam_enable_logging,
            log_requests=self.odam_log_requests,
            log_responses=self.odam_log_responses,
            enable_cache=self.odam_enable_cache,
            cache_ttl=self.odam_cache_ttl,
            max_cache_size=self.odam_max_cache_size,
            enable_metrics=self.odam_enable_metrics,
            metrics_prefix=self.odam_metrics_prefix,
            verify_ssl=self.odam_verify_ssl,
            allow_insecure=self.odam_allow_insecure,
            enterprise_v7_enabled=self.odam_enterprise_v7_enabled,
            medical_safety_enabled=self.odam_medical_safety_enabled,
            memory_enforcement_enabled=self.odam_memory_enforcement_enabled,
            fallback_enabled=self.odam_fallback_enabled,
            default_language=self.odam_default_language,
            default_memory_type=self.odam_default_memory_type
        )


# Глобальна конфігурація за замовчуванням
DEFAULT_CONFIG = ODAMConfig()


def get_config() -> ODAMConfig:
    """Отримання конфігурації з environment variables"""
    try:
        settings = ODAMSettings()
        return settings.to_config()
    except Exception:
        # Якщо не вдалося завантажити з env, повертаємо дефолтну
        return DEFAULT_CONFIG


def create_config(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    **kwargs
) -> ODAMConfig:
    """Створення конфігурації з параметрів"""
    config = get_config()
    
    if api_key:
        config.api_key = api_key
    if base_url:
        config.base_url = base_url
    
    # Оновлення інших параметрів
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
    
    return config 