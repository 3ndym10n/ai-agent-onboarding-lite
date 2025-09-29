"""
Continuous Improvement components for AI Onboard.

This module contains continuous improvement, performance optimization,
learning persistence, and system health monitoring systems.
"""

from .adaptive_config_manager import *
from .continuous_improvement_analytics import *
from .continuous_improvement_system import *
from .continuous_improvement_validator import *
from .knowledge_base_evolution import *
from .learning_persistence import *
from .optimizer import *
from .optimizer_state import *
from .performance_optimizer import *
from .system_damage_detector import *
from .system_health_monitor import *

__all__ = [
    # Continuous Improvement Core
    "ContinuousImprovementSystem",
    "get_continuous_improvement_system",
    "ContinuousImprovementValidator",
    "ContinuousImprovementAnalytics",
    # Performance Optimization
    "PerformanceOptimizer",
    "get_performance_optimizer",
    "Optimizer",
    "OptimizerState",
    # Learning & Persistence
    "LearningPersistence",
    "KnowledgeBaseEvolution",
    # System Health
    "SystemHealthMonitor",
    "get_system_health_monitor",
    "SystemDamageDetector",
    # Adaptive Configuration
    "AdaptiveConfigManager",
]
