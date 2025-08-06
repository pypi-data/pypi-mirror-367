"""
Setup configuration for uber-central-rest-client PyPI package.
"""

from setuptools import setup, find_packages
import os


def read_file(filename):
    """Read file contents for long description."""
    with open(os.path.join(os.path.dirname(__file__), filename), 'r', encoding='utf-8') as f:
        return f.read()


setup(
    name="uber-central-rest-client",
    version="1.1.0",
    author="Uber Central Team",
    author_email="support@uber-central.com",
    description="Official Python client for the Uber Central API - Enterprise Uber ride management",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/lymanlabs/uber-central",
    project_urls={
        "Documentation": "https://apparel-scraper--uber-central-api-serve.modal.run/docs",
        "Source Code": "https://github.com/lymanlabs/uber-central", 
        "Issue Tracker": "https://github.com/lymanlabs/uber-central/issues",
        "API Endpoint": "https://apparel-scraper--uber-central-api-serve.modal.run",
    },
    packages=find_packages(exclude=["tests*", "examples*"]),
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
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Office/Business",
        "Topic :: Communications",
        "Typing :: Typed",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "pydantic>=1.8.0,<3.0.0",
        "typing-extensions>=4.0.0; python_version<'3.10'",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
            "mypy>=0.800",
            "twine>=3.0.0",
            "build>=0.5.0",
        ],
        "async": [
            "aiohttp>=3.7.0",
            "asyncio-throttle>=1.0.0",
        ],
        "testing": [
            "responses>=0.12.0", 
            "pytest-mock>=3.0.0",
            "factory-boy>=3.0.0",
        ]
    },
    keywords=[
        "uber", "ride", "booking", "api", "client", "transportation", 
        "enterprise", "business", "ride-sharing", "mobility", "travel",
        "scheduling", "fleet", "corporate", "expense", "tracking"
    ],
    entry_points={
        "console_scripts": [
            "uber-central=uber_central_client.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "uber_central_client": ["py.typed"],
    },
    zip_safe=False,
)