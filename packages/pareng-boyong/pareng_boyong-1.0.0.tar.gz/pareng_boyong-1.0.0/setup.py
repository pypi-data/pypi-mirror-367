#!/usr/bin/env python3
"""
Setup script for Pareng Boyong - Your Intelligent Filipino AI Agent

This package provides a cost-optimized AI agent with Filipino cultural integration,
multimodal capabilities, and extensive tool ecosystem for development and automation.
"""

from setuptools import setup, find_packages
import os

# Read version from package
def get_version():
    """Get version from __init__.py"""
    version_file = os.path.join(os.path.dirname(__file__), 'pareng_boyong', '__init__.py')
    if os.path.exists(version_file):
        with open(version_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('__version__'):
                    return line.split('=')[1].strip().strip('"\'')
    return "1.0.0"

# Read long description from README
def get_long_description():
    """Get long description from README.md"""
    readme_file = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_file):
        with open(readme_file, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

if __name__ == "__main__":
    setup(
        name="pareng-boyong",
        version=get_version(),
        author="InnovateHub PH",
        author_email="info@innovatehub.ph",
        description="Pareng Boyong - Your Intelligent Filipino AI Agent and Coding Assistant",
        long_description=get_long_description(),
        long_description_content_type="text/markdown",
        url="https://github.com/innovatehub-ph/pareng-boyong",
        project_urls={
            "Bug Tracker": "https://github.com/innovatehub-ph/pareng-boyong/issues",
            "Documentation": "https://pareng-boyong.readthedocs.io",
            "Source Code": "https://github.com/innovatehub-ph/pareng-boyong",
            "Changelog": "https://github.com/innovatehub-ph/pareng-boyong/blob/main/CHANGELOG.md",
        },
        packages=find_packages(),
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "Intended Audience :: System Administrators",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
            "Topic :: Software Development :: Code Generators",
            "Topic :: Scientific/Engineering :: Artificial Intelligence",
            "Topic :: System :: Systems Administration",
            "Topic :: Text Processing :: Linguistic",
            "Natural Language :: English"
        ],
        python_requires=">=3.8",
        install_requires=[
            "click>=8.0.0",
            "python-dotenv>=1.0.0",
            "pydantic>=2.0.0", 
            "rich>=13.0.0",
            "typer>=0.9.0",
            "httpx>=0.25.0",
            "asyncio-throttle>=1.0.0",
            "tiktoken>=0.5.0",
            "nest-asyncio>=1.6.0",
            "psutil>=5.9.0",
            "pyyaml>=6.0.0",
            "pytz>=2023.3",
        ],
        extras_require={
            "ai": [
                "openai>=1.3.0",
                "anthropic>=0.3.0", 
                "litellm>=1.40.0",
                "sentence-transformers>=2.2.0",
                "faiss-cpu>=1.7.0",
            ],
            "multimedia": [
                "pillow>=10.0.0",
                "opencv-python>=4.8.0",
                "moviepy>=1.0.3",
                "imageio>=2.31.0",
                "requests>=2.31.0",
            ],
            "filipino": [
                "soundfile>=0.12.0",
                "librosa>=0.10.0",
                "phonemizer>=3.2.0",
                "espeak-ng>=1.51",
            ],
            "web": [
                "flask>=2.3.0",
                "flask-cors>=4.0.0",
                "websockets>=11.0.0",
                "jinja2>=3.1.0",
            ],
            "dev": [
                "pytest>=7.4.0",
                "pytest-asyncio>=0.21.0",
                "black>=23.0.0",
                "flake8>=6.0.0",
                "mypy>=1.5.0",
                "pre-commit>=3.4.0",
            ],
        },
        entry_points={
            "console_scripts": [
                "boyong=pareng_boyong.cli.main:app",
                "pareng-boyong=pareng_boyong.cli.main:app",
            ],
        },
        package_data={
            "pareng_boyong": [
                "cultural/data/*.json",
                "cultural/data/*.yaml", 
                "web/templates/*.html",
                "web/static/css/*.css",
                "web/static/js/*.js",
                "cli/templates/*.txt",
                "cli/templates/*.py",
            ],
        },
        include_package_data=True,
        zip_safe=False,
        keywords=[
            "ai", "agent", "filipino", "coding-assistant", "multimodal",
            "cost-optimization", "agent-zero", "pinoy-ai", "tts", "cli"
        ],
    )