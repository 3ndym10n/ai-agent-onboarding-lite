"""
Knowledge Base Evolution System - Intelligent knowledge management and evolution.

This module provides a comprehensive knowledge base system that:
- Captures and stores knowledge from all system interactions
- Evolves knowledge through pattern recognition and learning
- Provides intelligent knowledge retrieval and recommendations
- Maintains knowledge quality and relevance over time
- Integrates with all system components for comprehensive knowledge building
"""

import statistics
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from . import continuous_improvement_system, telemetry, utils


class KnowledgeType(Enum):
    """Types of knowledge stored in the system."""

    USER_PREFERENCE = "user_preference"
    WORKFLOW_PATTERN = "workflow_pattern"
    ERROR_SOLUTION = "error_solution"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    CONFIGURATION_BEST_PRACTICE = "configuration_best_practice"
    DOMAIN_EXPERTISE = "domain_expertise"
    SYSTEM_BEHAVIOR = "system_behavior"
    INTEGRATION_PATTERN = "integration_pattern"
    TROUBLESHOOTING_GUIDE = "troubleshooting_guide"
    BEST_PRACTICE = "best_practice"


class KnowledgeSource(Enum):
    """Sources of knowledge."""

    USER_INTERACTION = "user_interaction"
    SYSTEM_ANALYSIS = "system_analysis"
    ERROR_RESOLUTION = "error_resolution"
    PERFORMANCE_MONITORING = "performance_monitoring"
    CONFIGURATION_CHANGE = "configuration_change"
    EXTERNAL_LEARNING = "external_learning"
    PATTERN_RECOGNITION = "pattern_recognition"
    FEEDBACK_ANALYSIS = "feedback_analysis"


class KnowledgeQuality(Enum):
    """Quality levels for knowledge."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXPERT = "expert"


class KnowledgeStatus(Enum):
    """Status of knowledge items."""

    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    CONFLICTED = "conflicted"
    VERIFIED = "verified"

@dataclass

class KnowledgeItem:
    """A single piece of knowledge in the system."""

    knowledge_id: str
    knowledge_type: KnowledgeType
    title: str
    content: str
    source: KnowledgeSource
    quality: KnowledgeQuality
    status: KnowledgeStatus
    created_at: datetime
    updated_at: datetime
    last_accessed: Optional[datetime] = None
    access_count: int = 0
    confidence_score: float = 0.0
    relevance_score: float = 0.0
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    related_knowledge: List[str] = field(default_factory=list)
    validation_evidence: List[Dict[str, Any]] = field(default_factory=list)
    usage_statistics: Dict[str, Any] = field(default_factory=dict)

@dataclass

class KnowledgePattern:
    """A pattern discovered in the knowledge base."""

    pattern_id: str
    pattern_type: str
    description: str
    frequency: int
    confidence: float
    examples: List[str]
    conditions: Dict[str, Any]
    outcomes: Dict[str, Any]
    discovered_at: datetime
    last_updated: datetime
    validation_count: int = 0
    success_rate: float = 0.0

@dataclass

class KnowledgeRecommendation:
    """A knowledge - based recommendation."""

    recommendation_id: str
    knowledge_item_id: str
    recommendation_type: str
    title: str
    description: str
    confidence: float
    relevance_score: float
    context: Dict[str, Any]
    created_at: datetime
    expires_at: Optional[datetime] = None
    usage_count: int = 0
    feedback_score: float = 0.0


class KnowledgeBaseEvolution:
    """Comprehensive knowledge base evolution system."""


    def __init__(self, root: Path):
        self.root = root
        self.knowledge_path = root / ".ai_onboard" / "knowledge_base.jsonl"
        self.patterns_path = root / ".ai_onboard" / "knowledge_patterns.json"
        self.recommendations_path = (
            root / ".ai_onboard" / "knowledge_recommendations.jsonl"
        )
        self.evolution_config_path = (
            root / ".ai_onboard" / "knowledge_evolution_config.json"
        )

        # Initialize subsystems
        self.continuous_improvement = (
            continuous_improvement_system.get_continuous_improvement_system(root)
        )

        # Knowledge storage
        self.knowledge_items: Dict[str, KnowledgeItem] = {}
        self.knowledge_patterns: Dict[str, KnowledgePattern] = {}
        self.knowledge_recommendations: List[KnowledgeRecommendation] = []

        # Knowledge evolution state
        self.evolution_config = self._load_evolution_config()
        self.knowledge_index: Dict[str, Set[str]] = defaultdict(
            set
        )  # tag -> knowledge_ids
        self.knowledge_graph: Dict[str, Set[str]] = defaultdict(
            set
        )  # knowledge_id -> related_ids

        # Ensure directories exist
        self._ensure_directories()

        # Load existing knowledge
        self._load_knowledge_items()
        self._load_knowledge_patterns()
        self._load_knowledge_recommendations()


    def _ensure_directories(self):
        """Ensure all required directories exist."""
        for path in [
            self.knowledge_path,
            self.patterns_path,
            self.recommendations_path,
            self.evolution_config_path,
        ]:
            utils.ensure_dir(path.parent)


    def _load_evolution_config(self) -> Dict[str, Any]:
        """Load knowledge evolution configuration."""
        return utils.read_json(
            self.evolution_config_path,
            default={
                "auto_evolution_enabled": True,
                "pattern_discovery_enabled": True,
                "knowledge_quality_threshold": 0.7,
                "recommendation_confidence_threshold": 0.8,
                "knowledge_decay_days": 90,
                "pattern_min_frequency": 3,
                "max_knowledge_items": 10000,
                "max_patterns": 1000,
                "max_recommendations": 500,
                "knowledge_types_to_track": [
                    "user_preference",
                    "workflow_pattern",
                    "error_solution",
                    "performance_optimization",
                    "configuration_best_practice",
                ],
                "evolution_triggers": [
                    "new_knowledge_added",
                    "pattern_discovered",
                    "knowledge_conflict",
                    "quality_degradation",
                    "usage_pattern_change",
                ],
            },
        )


    def _load_knowledge_items(self):
        """Load knowledge items from storage."""
        if not self.knowledge_path.exists():
            return

        with open(self.knowledge_path, "r", encoding="utf - 8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    knowledge_item = KnowledgeItem(
                        knowledge_id=data["knowledge_id"],
                        knowledge_type=KnowledgeType(data["knowledge_type"]),
                        title=data["title"],
                        content=data["content"],
                        source=KnowledgeSource(data["source"]),
                        quality=KnowledgeQuality(data["quality"]),
                        status=KnowledgeStatus(data["status"]),
                        created_at=datetime.fromisoformat(data["created_at"]),
                        updated_at=datetime.fromisoformat(data["updated_at"]),
                        last_accessed=(
                            datetime.fromisoformat(data["last_accessed"])
                            if data.get("last_accessed")
                            else None
                        ),
                        access_count=data.get("access_count", 0),
                        confidence_score=data.get("confidence_score", 0.0),
                        relevance_score=data.get("relevance_score", 0.0),
                        tags=data.get("tags", []),
                        metadata=data.get("metadata", {}),
                        related_knowledge=data.get("related_knowledge", []),
                        validation_evidence=data.get("validation_evidence", []),
                        usage_statistics=data.get("usage_statistics", {}),
                    )
                    self.knowledge_items[knowledge_item.knowledge_id] = knowledge_item

                    # Update index
                    for tag in knowledge_item.tags:
                        self.knowledge_index[tag].add(knowledge_item.knowledge_id)

                    # Update graph
                    for related_id in knowledge_item.related_knowledge:
                        self.knowledge_graph[knowledge_item.knowledge_id].add(
                            related_id
                        )

                except (json.JSONDecodeError, KeyError, ValueError):
                    continue


    def _load_knowledge_patterns(self):
        """Load knowledge patterns from storage."""
        if not self.patterns_path.exists():
            return

        data = utils.read_json(self.patterns_path, default=[])

        for pattern_data in data:
            pattern = KnowledgePattern(
                pattern_id=pattern_data["pattern_id"],
                pattern_type=pattern_data["pattern_type"],
                description=pattern_data["description"],
                frequency=pattern_data["frequency"],
                confidence=pattern_data["confidence"],
                examples=pattern_data["examples"],
                conditions=pattern_data["conditions"],
                outcomes=pattern_data["outcomes"],
                discovered_at=datetime.fromisoformat(pattern_data["discovered_at"]),
                last_updated=datetime.fromisoformat(pattern_data["last_updated"]),
                validation_count=pattern_data.get("validation_count", 0),
                success_rate=pattern_data.get("success_rate", 0.0),
            )
            self.knowledge_patterns[pattern.pattern_id] = pattern


    def _load_knowledge_recommendations(self):
        """Load knowledge recommendations from storage."""
        if not self.recommendations_path.exists():
            return

        with open(self.recommendations_path, "r", encoding="utf - 8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    recommendation = KnowledgeRecommendation(
                        recommendation_id=data["recommendation_id"],
                        knowledge_item_id=data["knowledge_item_id"],
                        recommendation_type=data["recommendation_type"],
                        title=data["title"],
                        description=data["description"],
                        confidence=data["confidence"],
                        relevance_score=data["relevance_score"],
                        context=data["context"],
                        created_at=datetime.fromisoformat(data["created_at"]),
                        expires_at=(
                            datetime.fromisoformat(data["expires_at"])
                            if data.get("expires_at")
                            else None
                        ),
                        usage_count=data.get("usage_count", 0),
                        feedback_score=data.get("feedback_score", 0.0),
                    )
                    self.knowledge_recommendations.append(recommendation)
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue


    def add_knowledge(
        self,
        knowledge_type: KnowledgeType,
        title: str,
        content: str,
        source: KnowledgeSource,
        quality: KnowledgeQuality = KnowledgeQuality.MEDIUM,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None,
        confidence_score: float = 0.5,
    ) -> str:
        """Add new knowledge to the system."""
        knowledge_id = f"kb_{int(time.time())}_{utils.random_string(8)}"

        # Check for similar knowledge
        similar_knowledge = self._find_similar_knowledge(title, content, knowledge_type)

        knowledge_item = KnowledgeItem(
            knowledge_id=knowledge_id,
            knowledge_type=knowledge_type,
            title=title,
            content=content,
            source=source,
            quality=quality,
            status=KnowledgeStatus.DRAFT,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            confidence_score=confidence_score,
            relevance_score=self._calculate_relevance_score(content, tags or []),
            tags=tags or [],
            metadata=metadata or {},
            related_knowledge=[k.knowledge_id for k in similar_knowledge],
        )

        # Validate knowledge quality
        if self._validate_knowledge_quality(knowledge_item):
            knowledge_item.status = KnowledgeStatus.ACTIVE
        else:
            knowledge_item.status = KnowledgeStatus.DRAFT

        # Store knowledge
        self.knowledge_items[knowledge_id] = knowledge_item
        self._save_knowledge_item(knowledge_item)

        # Update index and graph
        self._update_knowledge_index(knowledge_item)

        # Trigger evolution
        if self.evolution_config["auto_evolution_enabled"]:
            self._trigger_knowledge_evolution("new_knowledge_added", knowledge_item)

        # Record learning event
        self.continuous_improvement.record_learning_event(
            learning_type=continuous_improvement_system.LearningType.KNOWLEDGE_ACQUISITION,
            context={
                "knowledge_type": knowledge_type.value,
                "source": source.value,
                "quality": quality.value,
                "similar_knowledge_count": len(similar_knowledge),
            },
            outcome={
                "knowledge_added": {
                    "id": knowledge_id,
                    "title": title,
                    "status": knowledge_item.status.value,
                }
            },
            confidence=confidence_score,
            impact_score=0.7,
            source="knowledge_base_evolution",
        )

        telemetry.log_event(
            "knowledge_added",
            knowledge_id=knowledge_id,
            knowledge_type=knowledge_type.value,
            source=source.value,
            quality=quality.value,
            status=knowledge_item.status.value,
        )

        return knowledge_id


    def _find_similar_knowledge(
        self, title: str, content: str, knowledge_type: KnowledgeType
    ) -> List[KnowledgeItem]:
        """Find similar knowledge items."""
        similar_items = []

        for item in self.knowledge_items.values():
            if item.knowledge_type != knowledge_type:
                continue

            # Simple similarity check based on title and content
            title_similarity = self._calculate_text_similarity(title, item.title)
            content_similarity = self._calculate_text_similarity(content, item.content)

            if title_similarity > 0.7 or content_similarity > 0.6:
                similar_items.append(item)

        return similar_items


    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings."""
        # Simple word - based similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0


    def _calculate_relevance_score(self, content: str, tags: List[str]) -> float:
        """Calculate relevance score for knowledge content."""
        # Simple relevance scoring based on content length and tags
        content_score = min(len(content) / 1000, 1.0)  # Normalize by 1000 chars
        tag_score = min(len(tags) / 5, 1.0)  # Normalize by 5 tags

        return (content_score + tag_score) / 2


    def _validate_knowledge_quality(self, knowledge_item: KnowledgeItem) -> bool:
        """Validate knowledge quality and determine if it should be active."""
        # Basic quality checks
        if len(knowledge_item.content) < 50:
            return False

        if (
            knowledge_item.confidence_score
            < self.evolution_config["knowledge_quality_threshold"]
        ):
            return False

        # Check for required fields based on knowledge type
        if knowledge_item.knowledge_type == KnowledgeType.ERROR_SOLUTION:
            if not any(
                keyword in knowledge_item.content.lower()
                for keyword in ["solution", "fix", "resolve", "error"]
            ):
                return False

        return True


    def _update_knowledge_index(self, knowledge_item: KnowledgeItem):
        """Update knowledge index and graph."""
        # Update tag index
        for tag in knowledge_item.tags:
            self.knowledge_index[tag].add(knowledge_item.knowledge_id)

        # Update knowledge graph
        for related_id in knowledge_item.related_knowledge:
            self.knowledge_graph[knowledge_item.knowledge_id].add(related_id)
            self.knowledge_graph[related_id].add(knowledge_item.knowledge_id)


    def search_knowledge(
        self,
        query: str,
        knowledge_types: List[KnowledgeType] = None,
        tags: List[str] = None,
        quality_threshold: float = 0.0,
        limit: int = 10,
    ) -> List[KnowledgeItem]:
        """Search for knowledge items."""
        results = []

        for item in self.knowledge_items.values():
            # Filter by knowledge type
            if knowledge_types and item.knowledge_type not in knowledge_types:
                continue

            # Filter by tags
            if tags and not any(tag in item.tags for tag in tags):
                continue

            # Filter by quality
            if item.confidence_score < quality_threshold:
                continue

            # Calculate relevance to query
            relevance = self._calculate_query_relevance(query, item)

            if relevance > 0.1:  # Minimum relevance threshold
                results.append((item, relevance))

        # Sort by relevance and return top results
        results.sort(key=lambda x: x[1], reverse=True)
        return [item for item, _ in results[:limit]]


    def _calculate_query_relevance(
        self, query: str, knowledge_item: KnowledgeItem
    ) -> float:
        """Calculate relevance of a knowledge item to a search query."""
        query_words = set(query.lower().split())

        # Check title relevance
        title_words = set(knowledge_item.title.lower().split())
        title_relevance = (
            len(query_words.intersection(title_words)) / len(query_words)
            if query_words
            else 0
        )

        # Check content relevance
        content_words = set(knowledge_item.content.lower().split())
        content_relevance = (
            len(query_words.intersection(content_words)) / len(query_words)
            if query_words
            else 0
        )

        # Check tag relevance
        tag_relevance = 0.0
        for tag in knowledge_item.tags:
            if any(word in tag.lower() for word in query_words):
                tag_relevance += 0.2

        # Weighted combination
        return title_relevance * 0.4 + content_relevance * 0.4 + tag_relevance * 0.2


    def get_knowledge_recommendations(
        self, context: Dict[str, Any], limit: int = 5
    ) -> List[KnowledgeRecommendation]:
        """Get knowledge - based recommendations for a given context."""
        recommendations = []

        # Find relevant knowledge items
        relevant_knowledge = self._find_contextual_knowledge(context)

        for knowledge_item in relevant_knowledge:
            # Create recommendation
            recommendation = KnowledgeRecommendation(
                recommendation_id=f"rec_{int(time.time())}_{utils.random_string(8)}",
                knowledge_item_id=knowledge_item.knowledge_id,
                recommendation_type="knowledge_application",
                title=f"Apply: {knowledge_item.title}",
                description=f"Consider applying this knowledge: {knowledge_item.content[:200]}...",
                confidence=knowledge_item.confidence_score,
                relevance_score=knowledge_item.relevance_score,
                context=context,
                created_at=datetime.now(),
            )
            recommendations.append(recommendation)

        # Sort by relevance and confidence
        recommendations.sort(
            key=lambda r: r.relevance_score * r.confidence, reverse=True
        )

        return recommendations[:limit]


    def _find_contextual_knowledge(
        self, context: Dict[str, Any]
    ) -> List[KnowledgeItem]:
        """Find knowledge items relevant to a given context."""
        relevant_items = []

        # Extract context keywords
        context_text = " ".join(str(v) for v in context.values() if isinstance(v, str))
        context_words = set(context_text.lower().split())

        for item in self.knowledge_items.values():
            if item.status != KnowledgeStatus.ACTIVE:
                continue

            # Check if knowledge is relevant to context
            relevance = self._calculate_context_relevance(context, context_words, item)

            if relevance > 0.3:  # Minimum relevance threshold
                relevant_items.append((item, relevance))

        # Sort by relevance
        relevant_items.sort(key=lambda x: x[1], reverse=True)
        return [item for item, _ in relevant_items[:10]]


    def _calculate_context_relevance(
        self,
        context: Dict[str, Any],
        context_words: Set[str],
        knowledge_item: KnowledgeItem,
    ) -> float:
        """Calculate relevance of knowledge item to context."""
        relevance = 0.0

        # Check content relevance
        content_words = set(knowledge_item.content.lower().split())
        content_relevance = (
            len(context_words.intersection(content_words)) / len(context_words)
            if context_words
            else 0
        )
        relevance += content_relevance * 0.4

        # Check tag relevance
        for tag in knowledge_item.tags:
            if any(word in tag.lower() for word in context_words):
                relevance += 0.2

        # Check metadata relevance
        for key, value in context.items():
            if key in knowledge_item.metadata:
                if str(value).lower() in str(knowledge_item.metadata[key]).lower():
                    relevance += 0.1

        return min(relevance, 1.0)


    def discover_patterns(self) -> List[KnowledgePattern]:
        """Discover patterns in the knowledge base."""
        if not self.evolution_config["pattern_discovery_enabled"]:
            return []

        patterns = []

        # Discover workflow patterns
        workflow_patterns = self._discover_workflow_patterns()
        patterns.extend(workflow_patterns)

        # Discover error - solution patterns
        error_patterns = self._discover_error_solution_patterns()
        patterns.extend(error_patterns)

        # Discover performance patterns
        performance_patterns = self._discover_performance_patterns()
        patterns.extend(performance_patterns)

        # Store discovered patterns
        for pattern in patterns:
            self.knowledge_patterns[pattern.pattern_id] = pattern

        self._save_knowledge_patterns()

        return patterns


    def _discover_workflow_patterns(self) -> List[KnowledgePattern]:
        """Discover workflow patterns from knowledge."""
        patterns = []

        # Group knowledge by workflow - related tags
        workflow_groups = defaultdict(list)

        for item in self.knowledge_items.values():
            if item.knowledge_type == KnowledgeType.WORKFLOW_PATTERN:
                for tag in item.tags:
                    if "workflow" in tag.lower() or "process" in tag.lower():
                        workflow_groups[tag].append(item)

        # Create patterns for frequent workflows
        for tag, items in workflow_groups.items():
            if len(items) >= self.evolution_config["pattern_min_frequency"]:
                pattern = KnowledgePattern(
                    pattern_id=f"pattern_{int(time.time())}_{utils.random_string(8)}",
                    pattern_type="workflow",
                    description=f"Common workflow pattern: {tag}",
                    frequency=len(items),
                    confidence=min(len(items) / 10, 1.0),
                    examples=[item.knowledge_id for item in items[:5]],
                    conditions={"tag": tag, "knowledge_type": "workflow_pattern"},
                    outcomes={"efficiency": "improved", "consistency": "increased"},
                    discovered_at=datetime.now(),
                    last_updated=datetime.now(),
                )
                patterns.append(pattern)

        return patterns


    def _discover_error_solution_patterns(self) -> List[KnowledgePattern]:
        """Discover error - solution patterns."""
        patterns = []

        # Group error solutions by error type
        error_groups = defaultdict(list)

        for item in self.knowledge_items.values():
            if item.knowledge_type == KnowledgeType.ERROR_SOLUTION:
                # Extract error type from content
                error_type = self._extract_error_type(item.content)
                if error_type:
                    error_groups[error_type].append(item)

        # Create patterns for common error types
        for error_type, items in error_groups.items():
            if len(items) >= self.evolution_config["pattern_min_frequency"]:
                pattern = KnowledgePattern(
                    pattern_id=f"pattern_{int(time.time())}_{utils.random_string(8)}",
                    pattern_type="error_solution",
                    description=f"Common solution for {error_type} errors",
                    frequency=len(items),
                    confidence=min(len(items) / 5, 1.0),
                    examples=[item.knowledge_id for item in items[:3]],
                    conditions={"error_type": error_type},
                    outcomes={
                        "resolution_time": "reduced",
                        "success_rate": "increased",
                    },
                    discovered_at=datetime.now(),
                    last_updated=datetime.now(),
                )
                patterns.append(pattern)

        return patterns


    def _discover_performance_patterns(self) -> List[KnowledgePattern]:
        """Discover performance optimization patterns."""
        patterns = []

        # Group performance optimizations by type
        perf_groups = defaultdict(list)

        for item in self.knowledge_items.values():
            if item.knowledge_type == KnowledgeType.PERFORMANCE_OPTIMIZATION:
                # Extract optimization type from content
                opt_type = self._extract_optimization_type(item.content)
                if opt_type:
                    perf_groups[opt_type].append(item)

        # Create patterns for common optimizations
        for opt_type, items in perf_groups.items():
            if len(items) >= self.evolution_config["pattern_min_frequency"]:
                pattern = KnowledgePattern(
                    pattern_id=f"pattern_{int(time.time())}_{utils.random_string(8)}",
                    pattern_type="performance_optimization",
                    description=f"Common {opt_type} optimization pattern",
                    frequency=len(items),
                    confidence=min(len(items) / 5, 1.0),
                    examples=[item.knowledge_id for item in items[:3]],
                    conditions={"optimization_type": opt_type},
                    outcomes={"performance": "improved", "efficiency": "increased"},
                    discovered_at=datetime.now(),
                    last_updated=datetime.now(),
                )
                patterns.append(pattern)

        return patterns


    def _extract_error_type(self, content: str) -> Optional[str]:
        """Extract error type from content."""
        # Simple error type extraction
        error_keywords = {
            "timeout": ["timeout", "timed out", "time out"],
            "memory": ["memory", "out of memory", "memory error"],
            "network": ["network", "connection", "network error"],
            "permission": ["permission", "access denied", "unauthorized"],
            "configuration": ["config", "configuration", "setting"],
        }

        content_lower = content.lower()
        for error_type, keywords in error_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                return error_type

        return None


    def _extract_optimization_type(self, content: str) -> Optional[str]:
        """Extract optimization type from content."""
        # Simple optimization type extraction
        opt_keywords = {
            "caching": ["cache", "caching", "memoization"],
            "database": ["database", "query", "sql", "index"],
            "algorithm": ["algorithm", "complexity", "optimization"],
            "memory": ["memory", "garbage collection", "memory management"],
            "network": ["network", "bandwidth", "latency"],
        }

        content_lower = content.lower()
        for opt_type, keywords in opt_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                return opt_type

        return None


    def _trigger_knowledge_evolution(self, trigger: str, context: Any = None):
        """Trigger knowledge evolution based on events."""
        if trigger not in self.evolution_config["evolution_triggers"]:
            return

        # Record evolution event
        self.continuous_improvement.record_learning_event(
            learning_type=continuous_improvement_system.LearningType.KNOWLEDGE_EVOLUTION,
            context={
                "trigger": trigger,
                "context_type": type(context).__name__ if context else None,
            },
            outcome={
                "evolution_triggered": {
                    "trigger": trigger,
                    "timestamp": datetime.now().isoformat(),
                }
            },
            confidence=0.8,
            impact_score=0.6,
            source="knowledge_base_evolution",
        )

        # Perform evolution actions
        if trigger == "new_knowledge_added":
            self._evolve_knowledge_relationships(context)
        elif trigger == "pattern_discovered":
            self._evolve_knowledge_patterns()
        elif trigger == "knowledge_conflict":
            self._resolve_knowledge_conflicts()
        elif trigger == "quality_degradation":
            self._improve_knowledge_quality()
        elif trigger == "usage_pattern_change":
            self._adapt_knowledge_relevance()


    def _evolve_knowledge_relationships(self, new_knowledge: KnowledgeItem):
        """Evolve knowledge relationships when new knowledge is added."""
        # Find and update related knowledge
        for existing_id, existing_item in self.knowledge_items.items():
            if existing_id == new_knowledge.knowledge_id:
                continue

            # Check for relationship
            similarity = self._calculate_text_similarity(
                new_knowledge.content, existing_item.content
            )

            if similarity > 0.5:
                # Add bidirectional relationship
                new_knowledge.related_knowledge.append(existing_id)
                existing_item.related_knowledge.append(new_knowledge.knowledge_id)

                # Update stored knowledge
                self._save_knowledge_item(existing_item)


    def _evolve_knowledge_patterns(self):
        """Evolve knowledge patterns based on new discoveries."""
        # Update pattern confidence based on new evidence
        for pattern in self.knowledge_patterns.values():
            # Find new examples
            new_examples = self._find_pattern_examples(pattern)

            if new_examples:
                pattern.examples.extend(new_examples[:3])  # Keep top 3 new examples
                pattern.frequency += len(new_examples)
                pattern.confidence = min(pattern.frequency / 10, 1.0)
                pattern.last_updated = datetime.now()

        self._save_knowledge_patterns()


    def _find_pattern_examples(self, pattern: KnowledgePattern) -> List[str]:
        """Find new examples for a pattern."""
        examples = []

        for item in self.knowledge_items.values():
            if item.knowledge_id in pattern.examples:
                continue

            # Check if item matches pattern conditions
            if self._item_matches_pattern(item, pattern):
                examples.append(item.knowledge_id)

        return examples


    def _item_matches_pattern(
        self, item: KnowledgeItem, pattern: KnowledgePattern
    ) -> bool:
        """Check if a knowledge item matches a pattern."""
        # Check knowledge type
        if pattern.conditions.get("knowledge_type"):
            if item.knowledge_type.value != pattern.conditions["knowledge_type"]:
                return False

        # Check tags
        if pattern.conditions.get("tag"):
            if pattern.conditions["tag"] not in item.tags:
                return False

        # Check error type
        if pattern.conditions.get("error_type"):
            error_type = self._extract_error_type(item.content)
            if error_type != pattern.conditions["error_type"]:
                return False

        return True


    def _resolve_knowledge_conflicts(self):
        """Resolve conflicts in knowledge base."""
        # Find conflicting knowledge items
        conflicts = self._find_knowledge_conflicts()

        for conflict_group in conflicts:
            # Resolve conflict by keeping highest quality item
            best_item = max(conflict_group, key=lambda x: x.confidence_score)

            for item in conflict_group:
                if item.knowledge_id != best_item.knowledge_id:
                    item.status = KnowledgeStatus.CONFLICTED
                    self._save_knowledge_item(item)


    def _find_knowledge_conflicts(self) -> List[List[KnowledgeItem]]:
        """Find conflicting knowledge items."""
        conflicts = []
        processed: set[str] = set()

        for item1 in self.knowledge_items.values():
            if item1.knowledge_id in processed:
                continue

            conflict_group = [item1]

            for item2 in self.knowledge_items.values():
                if (
                    item2.knowledge_id in processed
                    or item1.knowledge_id == item2.knowledge_id
                ):
                    continue

                # Check for conflict
                if self._is_knowledge_conflict(item1, item2):
                    conflict_group.append(item2)

            if len(conflict_group) > 1:
                conflicts.append(conflict_group)
                processed.update(item.knowledge_id for item in conflict_group)

        return conflicts


    def _is_knowledge_conflict(
        self, item1: KnowledgeItem, item2: KnowledgeItem
    ) -> bool:
        """Check if two knowledge items conflict."""
        # Same knowledge type and similar content but different recommendations
        if item1.knowledge_type != item2.knowledge_type:
            return False

        similarity = self._calculate_text_similarity(item1.content, item2.content)
        if similarity < 0.7:
            return False

        # Check for contradictory content
        return self._has_contradictory_content(item1.content, item2.content)


    def _has_contradictory_content(self, content1: str, content2: str) -> bool:
        """Check if two content strings are contradictory."""
        # Simple contradiction detection
        contradiction_keywords = [
            ("should", "should not"),
            ("always", "never"),
            ("enable", "disable"),
            ("true", "false"),
            ("yes", "no"),
        ]

        content1_lower = content1.lower()
        content2_lower = content2.lower()

        for positive, negative in contradiction_keywords:
            if positive in content1_lower and negative in content2_lower:
                return True
            if negative in content1_lower and positive in content2_lower:
                return True

        return False


    def _improve_knowledge_quality(self):
        """Improve knowledge quality through validation and enhancement."""
        for item in self.knowledge_items.values():
            if item.status == KnowledgeStatus.DRAFT:
                # Re - validate draft items
                if self._validate_knowledge_quality(item):
                    item.status = KnowledgeStatus.ACTIVE
                    item.updated_at = datetime.now()
                    self._save_knowledge_item(item)


    def _adapt_knowledge_relevance(self):
        """Adapt knowledge relevance based on usage patterns."""
        for item in self.knowledge_items.values():
            # Update relevance score based on access count and recency
            if item.last_accessed:
                days_since_access = (datetime.now() - item.last_accessed).days
                access_factor = max(
                    0, 1 - (days_since_access / 30)
                )  # Decay over 30 days
            else:
                access_factor = 0

            # Update relevance score
            item.relevance_score = item.relevance_score * 0.7 + access_factor * 0.3
            self._save_knowledge_item(item)


    def get_knowledge_statistics(self) -> Dict[str, Any]:
        """Get comprehensive knowledge base statistics."""
        total_items = len(self.knowledge_items)
        active_items = len(
            [
                item
                for item in self.knowledge_items.values()
                if item.status == KnowledgeStatus.ACTIVE
            ]
        )

        # Knowledge type distribution
        type_distribution = Counter(
            item.knowledge_type.value for item in self.knowledge_items.values()
        )

        # Quality distribution
        quality_distribution = Counter(
            item.quality.value for item in self.knowledge_items.values()
        )

        # Source distribution
        source_distribution = Counter(
            item.source.value for item in self.knowledge_items.values()
        )

        # Average confidence and relevance
        avg_confidence = (
            statistics.mean(
                [item.confidence_score for item in self.knowledge_items.values()]
            )
            if self.knowledge_items
            else 0
        )
        avg_relevance = (
            statistics.mean(
                [item.relevance_score for item in self.knowledge_items.values()]
            )
            if self.knowledge_items
            else 0
        )

        # Pattern statistics
        total_patterns = len(self.knowledge_patterns)
        avg_pattern_confidence = (
            statistics.mean([p.confidence for p in self.knowledge_patterns.values()])
            if self.knowledge_patterns
            else 0
        )

        # Recommendation statistics
        total_recommendations = len(self.knowledge_recommendations)
        active_recommendations = len(
            [
                r
                for r in self.knowledge_recommendations
                if not r.expires_at or r.expires_at > datetime.now()
            ]
        )

        return {
            "total_knowledge_items": total_items,
            "active_knowledge_items": active_items,
            "draft_knowledge_items": total_items - active_items,
            "knowledge_type_distribution": dict(type_distribution),
            "quality_distribution": dict(quality_distribution),
            "source_distribution": dict(source_distribution),
            "average_confidence_score": avg_confidence,
            "average_relevance_score": avg_relevance,
            "total_patterns": total_patterns,
            "average_pattern_confidence": avg_pattern_confidence,
            "total_recommendations": total_recommendations,
            "active_recommendations": active_recommendations,
            "knowledge_index_size": len(self.knowledge_index),
            "knowledge_graph_size": len(self.knowledge_graph),
        }


    def _save_knowledge_item(self, knowledge_item: KnowledgeItem):
        """Save a knowledge item to storage."""
        data = {
            "knowledge_id": knowledge_item.knowledge_id,
            "knowledge_type": knowledge_item.knowledge_type.value,
            "title": knowledge_item.title,
            "content": knowledge_item.content,
            "source": knowledge_item.source.value,
            "quality": knowledge_item.quality.value,
            "status": knowledge_item.status.value,
            "created_at": knowledge_item.created_at.isoformat(),
            "updated_at": knowledge_item.updated_at.isoformat(),
            "last_accessed": (
                knowledge_item.last_accessed.isoformat()
                if knowledge_item.last_accessed
                else None
            ),
            "access_count": knowledge_item.access_count,
            "confidence_score": knowledge_item.confidence_score,
            "relevance_score": knowledge_item.relevance_score,
            "tags": knowledge_item.tags,
            "metadata": knowledge_item.metadata,
            "related_knowledge": knowledge_item.related_knowledge,
            "validation_evidence": knowledge_item.validation_evidence,
            "usage_statistics": knowledge_item.usage_statistics,
        }

        with open(self.knowledge_path, "a", encoding="utf - 8") as f:
            json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")


    def _save_knowledge_patterns(self):
        """Save knowledge patterns to storage."""
        data = []
        for pattern in self.knowledge_patterns.values():
            data.append(
                {
                    "pattern_id": pattern.pattern_id,
                    "pattern_type": pattern.pattern_type,
                    "description": pattern.description,
                    "frequency": pattern.frequency,
                    "confidence": pattern.confidence,
                    "examples": pattern.examples,
                    "conditions": pattern.conditions,
                    "outcomes": pattern.outcomes,
                    "discovered_at": pattern.discovered_at.isoformat(),
                    "last_updated": pattern.last_updated.isoformat(),
                    "validation_count": pattern.validation_count,
                    "success_rate": pattern.success_rate,
                }
            )

        utils.write_json(self.patterns_path, data)


    def _save_knowledge_recommendations(self):
        """Save knowledge recommendations to storage."""
        with open(self.recommendations_path, "w", encoding="utf - 8") as f:
            for recommendation in self.knowledge_recommendations:
                data = {
                    "recommendation_id": recommendation.recommendation_id,
                    "knowledge_item_id": recommendation.knowledge_item_id,
                    "recommendation_type": recommendation.recommendation_type,
                    "title": recommendation.title,
                    "description": recommendation.description,
                    "confidence": recommendation.confidence,
                    "relevance_score": recommendation.relevance_score,
                    "context": recommendation.context,
                    "created_at": recommendation.created_at.isoformat(),
                    "expires_at": (
                        recommendation.expires_at.isoformat()
                        if recommendation.expires_at
                        else None
                    ),
                    "usage_count": recommendation.usage_count,
                    "feedback_score": recommendation.feedback_score,
                }
                json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
                f.write("\n")


def get_knowledge_base_evolution(root: Path) -> KnowledgeBaseEvolution:
    """Get knowledge base evolution system instance."""
    return KnowledgeBaseEvolution(root)
