"""
vaulter ライブラリのセットアップ設定
"""

from setuptools import setup, find_packages
import os

# READMEファイルを読み込み
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

setup(
    name="vaulter",
    version="1.0.0",
    author="tikisan",
    author_email="",
    description="機密情報を自動暗号化するPythonライブラリ",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/tikipiya/vaulter",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "cryptography>=3.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.0.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
            "mypy>=0.800",
        ],
    },
    keywords="security, encryption, secrets, vault, cryptography",
    project_urls={
        "Bug Reports": "https://github.com/tikipiya/vaulter/issues",
        "Source": "https://github.com/tikipiya/vaulter",
        "Documentation": "https://github.com/tikipiya/vaulter#readme",
    },
) 