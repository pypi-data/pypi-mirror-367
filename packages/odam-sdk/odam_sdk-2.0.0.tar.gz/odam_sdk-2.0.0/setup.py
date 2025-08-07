"""
Setup script for ODAM V4 Python SDK
===================================

Цей файл містить конфігурацію для встановлення SDK через pip.
"""

from setuptools import setup, find_packages
import os

# Читаємо README файл
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "ODAM V4 Python SDK - Офіційний SDK для інтеграції з ODAM V4"


# Читаємо requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(requirements_path):
        with open(requirements_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []


setup(
    name="odam-sdk",
    version="2.0.0",
    author="ODAM Technologies",
    author_email="support@odam.dev",
    description="Офіційний Python SDK для інтеграції з ODAM V4 - системою штучного інтелекту з людською пам'яттю",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://api.odam.dev",
    project_urls={
        "Bug Tracker": "https://api.odam.dev/issues",
        "Documentation": "https://docs.odam.dev",
        "Source Code": "https://api.odam.dev",
        "Website": "https://odam.dev",
    },
    packages=find_packages(include=['odam_sdk', 'odam_sdk.*']),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Communications :: Chat",
        "Topic :: Database",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: System :: Distributed Computing",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Networking :: Monitoring",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "typing-extensions>=4.5.0",
        "structlog>=23.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-mock>=3.10.0",
            "responses>=0.23.0",
            "freezegun>=1.2.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
            "sphinx-autodoc-typehints>=1.19.0",
            "myst-parser>=1.0.0",
        ],
        "examples": [
            "fastapi>=0.100.0",
            "uvicorn>=0.23.0",
            "streamlit>=1.25.0",
            "gradio>=3.35.0",
            "dash>=2.10.0",
            "plotly>=5.15.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "odam-cli=odam_sdk.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "odam_sdk": [
            "*.md",
            "*.txt",
            "*.yml",
            "*.yaml",
            "*.json",
        ],
    },
    keywords=[
        "ai",
        "artificial-intelligence",
        "chatbot",
        "nlp",
        "natural-language-processing",
        "memory",
        "conversation",
        "chat",
        "api",
        "sdk",
        "machine-learning",
        "deep-learning",
        "neural-networks",
        "language-model",
        "text-generation",
        "entity-extraction",
        "knowledge-graph",
        "semantic-search",
        "vector-search",
        "embeddings",
        "medical-nlp",
        "healthcare",
        "multilingual",
        "ukrainian",
        "enterprise",
        "saas",
        "cloud",
        "rest-api",
        "fastapi",
        "python",
        "typescript",
        "javascript",
        "java",
        "dotnet",
    ],
    license="MIT",
    platforms=["any"],
    zip_safe=False,
) 