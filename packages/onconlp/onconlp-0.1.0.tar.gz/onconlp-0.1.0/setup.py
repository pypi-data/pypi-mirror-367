#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OncoNLP 安装脚本

肿瘤学自然语言处理工具包的安装配置
"""

from setuptools import setup, find_packages

# 读取 README 文件
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "OncoNLP - Natural Language Processing Toolkit for Oncology"

# 读取依赖文件
try:
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
except FileNotFoundError:
    # 如果 requirements.txt 不存在，使用基本依赖
    requirements = [
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "spacy>=3.4.0",
        "scikit-learn>=1.1.0",
        "transformers>=4.20.0"
    ]

setup(
    name="onconlp",
    version="0.1.0",
    author="OncoNLP Team",
    author_email="team@onconlp.org",
    description="Natural Language Processing Toolkit for Oncology",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/onconlp/onconlp",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Text Processing :: Linguistic",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    keywords="oncology, nlp, medical, text processing, cancer research",
    project_urls={
        "Bug Reports": "https://github.com/onconlp/onconlp/issues",
        "Source": "https://github.com/onconlp/onconlp",
        "Documentation": "https://onconlp.readthedocs.io/",
    },
)
