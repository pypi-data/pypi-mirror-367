#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OncoNLP Core Module

Core classes and functions for the OncoNLP natural language processing toolkit.
Provides the main processing pipeline for oncological text analysis.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """
    Container for OncoNLP processing results.
    
    Attributes:
        text: Original input text
        cancer_type: Identified cancer type
        staging: TNM staging information
        biomarkers: List of identified biomarkers
        treatments: List of identified treatments
        confidence_scores: Confidence scores for extractions
        metadata: Additional metadata
    """
    text: str
    cancer_type: Optional[str] = None
    staging: Optional[Dict[str, str]] = None
    biomarkers: List[str] = None
    treatments: List[str] = None
    confidence_scores: Dict[str, float] = None
    metadata: Dict[str, any] = None
    
    def __post_init__(self):
        if self.biomarkers is None:
            self.biomarkers = []
        if self.treatments is None:
            self.treatments = []
        if self.confidence_scores is None:
            self.confidence_scores = {}
        if self.metadata is None:
            self.metadata = {}


class OncologyTextProcessor:
    """
    Main processor class for oncological text analysis.
    
    Provides comprehensive NLP capabilities for processing medical texts
    related to cancer diagnosis, treatment, and research.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the OncoNLP processor.
        
        Args:
            config: Configuration dictionary for customizing behavior
        """
        self.config = config or {}
        self.language = self.config.get('language', 'en')
        self.models_loaded = False
        
        # Cancer type patterns (simplified for demo)
        self.cancer_patterns = {
            r'lung\s+(?:adeno)?carcinoma|lung\s+cancer': 'lung cancer',
            r'breast\s+cancer|mammary\s+carcinoma': 'breast cancer',
            r'colorectal\s+cancer|colon\s+cancer': 'colorectal cancer',
            r'prostate\s+cancer|prostatic\s+carcinoma': 'prostate cancer',
            r'pancreatic\s+cancer|pancreatic\s+adenocarcinoma': 'pancreatic cancer'
        }
        
        # TNM staging patterns
        self.staging_patterns = {
            r'T([0-4X])[a-z]?': 'T',
            r'N([0-3X])': 'N', 
            r'M([01X])': 'M'
        }
        
        # Biomarker patterns
        self.biomarker_patterns = [
            r'HER2[+-]?', r'EGFR', r'KRAS', r'BRAF', r'PD-L1',
            r'BRCA[12]', r'TP53', r'PIK3CA', r'ALK', r'ROS1'
        ]
        
        logger.info("OncoNLP processor initialized")
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess medical text for analysis.
        
        Args:
            text: Input text to preprocess
            
        Returns:
            Preprocessed text
        """
        if not isinstance(text, str):
            raise ValueError("Input must be a string")
        
        # Basic preprocessing
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        text = re.sub(r'[^\w\s\-\+\./()]', '', text)  # Keep relevant chars
        
        return text
    
    def extract_cancer_type(self, text: str) -> Tuple[Optional[str], float]:
        """
        Extract cancer type from text.
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (cancer_type, confidence_score)
        """
        text_lower = text.lower()
        
        for pattern, cancer_type in self.cancer_patterns.items():
            if re.search(pattern, text_lower):
                confidence = 0.85  # Simplified confidence scoring
                return cancer_type, confidence
        
        return None, 0.0
    
    def extract_staging_info(self, text: str) -> Tuple[Optional[Dict], float]:
        """
        Extract TNM staging information from text.
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (staging_dict, confidence_score)
        """
        staging = {}
        confidence_sum = 0.0
        match_count = 0
        
        for pattern, stage_type in self.staging_patterns.items():
            matches = re.findall(pattern, text.upper())
            if matches:
                staging[stage_type] = matches[0]
                confidence_sum += 0.9
                match_count += 1
        
        if staging:
            avg_confidence = confidence_sum / match_count
            return staging, avg_confidence
        
        return None, 0.0
    
    def extract_biomarkers(self, text: str) -> Tuple[List[str], float]:
        """
        Extract biomarker information from text.
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (biomarkers_list, confidence_score)
        """
        biomarkers = []
        text_upper = text.upper()
        
        for pattern in self.biomarker_patterns:
            matches = re.findall(pattern, text_upper)
            biomarkers.extend(matches)
        
        # Remove duplicates while preserving order
        unique_biomarkers = list(dict.fromkeys(biomarkers))
        
        confidence = 0.8 if unique_biomarkers else 0.0
        return unique_biomarkers, confidence
    
    def process(self, text: str) -> ProcessingResult:
        """
        Process input text and extract oncological information.
        
        Args:
            text: Input medical text
            
        Returns:
            ProcessingResult object with extracted information
        """
        if not text or not isinstance(text, str):
            raise ValueError("Input text must be a non-empty string")
        
        # Preprocess text
        processed_text = self.preprocess_text(text)
        
        # Extract information
        cancer_type, cancer_confidence = self.extract_cancer_type(processed_text)
        staging, staging_confidence = self.extract_staging_info(processed_text)
        biomarkers, biomarker_confidence = self.extract_biomarkers(processed_text)
        
        # Create result object
        result = ProcessingResult(
            text=text,
            cancer_type=cancer_type,
            staging=staging,
            biomarkers=biomarkers,
            confidence_scores={
                'cancer_type': cancer_confidence,
                'staging': staging_confidence,
                'biomarkers': biomarker_confidence
            },
            metadata={
                'processed_at': datetime.now().isoformat(),
                'processor_version': '0.1.0',
                'language': self.language
            }
        )
        
        logger.info(f"Processed text with {len(biomarkers)} biomarkers found")
        return result
    
    def batch_process(self, texts: List[str]) -> List[ProcessingResult]:
        """
        Process multiple texts in batch.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of ProcessingResult objects
        """
        results = []
        
        for i, text in enumerate(texts):
            try:
                result = self.process(text)
                results.append(result)
                logger.info(f"Processed text {i+1}/{len(texts)}")
            except Exception as e:
                logger.error(f"Error processing text {i+1}: {str(e)}")
                # Create empty result for failed processing
                results.append(ProcessingResult(text=text))
        
        return results


class OncologyAnalyzer:
    """
    Advanced analyzer for oncological text data.
    
    Provides higher-level analysis functions beyond basic extraction.
    """
    
    def __init__(self):
        self.processor = OncologyTextProcessor()
    
    def analyze_clinical_report(self, text: str) -> ProcessingResult:
        """
        Analyze a clinical report with enhanced processing.
        
        Args:
            text: Clinical report text
            
        Returns:
            Enhanced ProcessingResult with additional analysis
        """
        result = self.processor.process(text)
        
        # Add report-specific analysis
        result.metadata['report_type'] = self._classify_report_type(text)
        result.metadata['report_sections'] = self._identify_sections(text)
        
        return result
    
    def _classify_report_type(self, text: str) -> str:
        """Classify the type of medical report."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['pathology', 'biopsy', 'histology']):
            return 'pathology_report'
        elif any(word in text_lower for word in ['radiology', 'imaging', 'ct', 'mri']):
            return 'imaging_report'
        elif any(word in text_lower for word in ['progress', 'follow', 'visit']):
            return 'progress_note'
        else:
            return 'clinical_note'
    
    def _identify_sections(self, text: str) -> List[str]:
        """Identify sections within the medical text."""
        sections = []
        text_lower = text.lower()
        
        section_indicators = [
            'history', 'examination', 'assessment', 'plan',
            'diagnosis', 'treatment', 'findings', 'impression'
        ]
        
        for indicator in section_indicators:
            if indicator in text_lower:
                sections.append(indicator)
        
        return sections


# Utility functions
def load_oncology_vocabulary(vocabulary_type: str = 'standard') -> Dict[str, List[str]]:
    """
    Load oncology-specific vocabulary sets.
    
    Args:
        vocabulary_type: Type of vocabulary to load
        
    Returns:
        Dictionary of vocabulary terms by category
    """
    # Simplified vocabulary for demo
    vocabulary = {
        'cancer_types': [
            'lung cancer', 'breast cancer', 'colorectal cancer',
            'prostate cancer', 'pancreatic cancer', 'liver cancer'
        ],
        'treatments': [
            'chemotherapy', 'radiation therapy', 'surgery',
            'immunotherapy', 'targeted therapy', 'hormone therapy'
        ],
        'biomarkers': [
            'HER2', 'EGFR', 'KRAS', 'BRAF', 'PD-L1',
            'BRCA1', 'BRCA2', 'TP53', 'PIK3CA'
        ]
    }
    
    return vocabulary


def validate_tnm_staging(staging: Dict[str, str]) -> bool:
    """
    Validate TNM staging information.
    
    Args:
        staging: Dictionary with T, N, M values
        
    Returns:
        True if staging is valid, False otherwise
    """
    valid_t = ['0', '1', '2', '3', '4', 'X']
    valid_n = ['0', '1', '2', '3', 'X']
    valid_m = ['0', '1', 'X']
    
    if 'T' in staging and staging['T'] not in valid_t:
        return False
    if 'N' in staging and staging['N'] not in valid_n:
        return False
    if 'M' in staging and staging['M'] not in valid_m:
        return False
    
    return True
