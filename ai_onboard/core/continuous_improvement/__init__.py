"""
Continuous Improvement components for AI Onboard.

This module contains continuous improvement, performance optimization,
learning persistence, and system health monitoring systems.
"""

from .adaptive_config_manager import (
    AdaptiveConfigManager,
    get_adaptive_config_manager,
)
from .continuous_improvement_analytics import (
    ContinuousImprovementAnalytics,
    get_continuous_improvement_analytics,
)
from .continuous_improvement_system import (
    ContinuousImprovementSystem,
    get_continuous_improvement_system,
)
from .continuous_improvement_validator import (
    ContinuousImprovementValidator,
    get_continuous_improvement_validator,
    ValidationCategory,
    ValidationReport,
    ValidationResult,
    ValidationTestCase,
)
from .knowledge_base_evolution import (
    KnowledgeBaseEvolution,
    get_knowledge_base_evolution,
)
from .learning_persistence import LearningPersistenceManager

# optimizer and optimizer_state modules contain only functions, no classes
from .performance_optimizer import (
    PerformanceOptimizer,
    get_performance_optimizer,
)
from .system_damage_detector import (
    SystemDamageDetector,
    get_system_damage_detector,
)
from .system_health_monitor import (
    SystemHealthMonitor,
    get_system_health_monitor,
)

__all__ = [
    # Continuous Improvement Core
    "ContinuousImprovementSystem",
    "get_continuous_improvement_system",
    "ContinuousImprovementValidator",
    "get_continuous_improvement_validator",
    "ValidationCategory",
    "ValidationReport",
    "ValidationResult",
    "ValidationTestCase",
    "ContinuousImprovementAnalytics",
    "get_continuous_improvement_analytics",
    # Performance Optimization
    "PerformanceOptimizer",
    "get_performance_optimizer",
    # Learning & Persistence
    "LearningPersistenceManager",
    "KnowledgeBaseEvolution",
    "get_knowledge_base_evolution",
    # System Health
    "SystemHealthMonitor",
    "get_system_health_monitor",
    "SystemDamageDetector",
    "get_system_damage_detector",
    # Adaptive Configuration
    "AdaptiveConfigManager",
    "get_adaptive_config_manager",
]
