"""
OncoNLP Configuration Module

Configuration parameters and settings for the OncoNLP toolkit,
including model configurations, data processing parameters, and
oncology-specific vocabularies.
"""

import os
from pathlib import Path

# Project Configuration
PROJECT_CONFIG = {
    "name": "OncoNLP",
    "version": "0.1.0",
    "description": "Natural Language Processing Toolkit for Oncology",
    "author": "OncoNLP Development Team",
    "license": "MIT",
    "repository": "https://github.com/onconlp/onconlp"
}

# Data Processing Configuration
DATA_CONFIG = {
    "input_dir": "data/input",
    "output_dir": "data/output", 
    "temp_dir": "data/temp",
    "models_dir": "models",
    "cache_dir": "cache",
    "supported_formats": [".txt", ".csv", ".json", ".xml", ".pdf", ".docx"],
    "max_file_size_mb": 100,
    "batch_size": 32,
    "encoding": "utf-8"
}

# NLP Model Configuration
NLP_CONFIG = {
    "default_language": "en",
    "supported_languages": ["en", "zh", "es", "fr", "de"],
    "models": {
        "tokenizer": "spacy",
        "pos_tagger": "spacy",
        "ner": "biobert",
        "sentiment": "vader",
        "embeddings": "bio-word2vec"
    },
    "spacy_models": {
        "en": "en_core_web_sm",
        "zh": "zh_core_web_sm"
    },
    "max_seq_length": 512,
    "stopwords_file": "resources/stopwords.txt"
}

# Oncology-Specific Configuration
ONCOLOGY_CONFIG = {
    "cancer_types": [
        "lung cancer", "breast cancer", "colorectal cancer", "prostate cancer",
        "stomach cancer", "liver cancer", "pancreatic cancer", "kidney cancer",
        "bladder cancer", "thyroid cancer", "leukemia", "lymphoma", "melanoma",
        "ovarian cancer", "cervical cancer", "brain tumor", "sarcoma"
    ],
    "treatment_types": [
        "surgery", "chemotherapy", "radiation therapy", "targeted therapy",
        "immunotherapy", "hormone therapy", "stem cell transplant",
        "precision medicine", "palliative care"
    ],
    "staging_systems": ["TNM", "AJCC", "UICC", "FIGO", "Ann Arbor"],
    "biomarkers": [
        "HER2", "EGFR", "KRAS", "BRAF", "PD-L1", "MSI", "BRCA1", "BRCA2",
        "TP53", "PIK3CA", "ALK", "ROS1", "NTRK", "TMB"
    ],
    "anatomical_sites": [
        "lung", "breast", "colon", "rectum", "prostate", "stomach", "liver",
        "pancreas", "kidney", "bladder", "thyroid", "ovary", "cervix", "brain"
    ]
}

# Performance Configuration
PERFORMANCE_CONFIG = {
    "enable_gpu": True,
    "num_workers": 4,
    "memory_limit_gb": 8,
    "cache_predictions": True,
    "parallel_processing": True
}
