"""
Quality and Safety components for AI Onboard.

This module contains quality assurance, risk assessment, dependency checking,
code analysis, and safety mechanisms.
"""

# Import specific classes to avoid conflicts
from .cleanup_safety_gates import (
    CleanupSafetyGateFramework,
    CleanupOperation as SafetyGateCleanupOperation,
    RiskLevel as SafetyGateRiskLevel,
)
from .code_quality_analyzer import CodeQualityAnalyzer
from .dependency_checker import DependencyChecker, DependencyCheckResult
from .dependency_mapper import DependencyMapper
from .duplicate_detector import DuplicateDetector
from .risk_assessment_framework import (
    RiskAssessmentFramework,
    RiskAssessmentResult,
    RiskLevel,
)
from .structural_recommendation_engine import StructuralRecommendationEngine
from .syntax_validator import SyntaxValidator
from .ultra_safe_cleanup import (
    UltraSafeCleanupEngine,
    CleanupOperation as UltraSafeCleanupOperation,
    CleanupTarget,
)

__all__ = [
    # Safety Gates & Cleanup
    "CleanupSafetyGateFramework",
    "SafetyGateCleanupOperation",
    "UltraSafeCleanupEngine",
    # Quality Analysis
    "CodeQualityAnalyzer",
    "SyntaxValidator",
    "DuplicateDetector",
    # Risk & Assessment
    "RiskAssessmentFramework",
    "RiskAssessmentResult",
    "RiskLevel",
    # Dependencies
    "DependencyChecker",
    "DependencyCheckResult",
    "DependencyMapper",
    # Policy & Structure
    "StructuralRecommendationEngine",
    # Cleanup Operations
    "UltraSafeCleanupOperation",
    "CleanupTarget",
    "SafetyGateRiskLevel",
]
