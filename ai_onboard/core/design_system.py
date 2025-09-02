"""
Design System Management

This module manages design tokens, components, and ensures design consistency
across the project by tracking design decisions and validating against established patterns.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class DesignToken:
    """A design token (color, typography, spacing, etc.)"""
    name: str
    category: str  # "color", "typography", "spacing", "border", "shadow"
    value: str
    description: str
    usage: List[str] = None


@dataclass
class DesignComponent:
    """A reusable design component"""
    name: str
    category: str  # "button", "input", "card", "navigation", etc.
    variants: List[str]
    props: Dict[str, str]
    usage_count: int = 0
    last_used: str = ""


@dataclass
class DesignPattern:
    """A design pattern or interaction pattern"""
    name: str
    description: str
    use_cases: List[str]
    examples: List[str]
    accessibility_notes: str = ""


class DesignSystemManager:
    """Manages the project's design system"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.design_system_path = self.project_path / ".ai_onboard" / "design_system"
        self.design_system_path.mkdir(exist_ok=True)
        
        self.tokens_file = self.design_system_path / "tokens.json"
        self.components_file = self.design_system_path / "components.json"
        self.patterns_file = self.design_system_path / "patterns.json"
        
        self.tokens = self._load_tokens()
        self.components = self._load_components()
        self.patterns = self._load_patterns()
    
    def _load_tokens(self) -> Dict[str, DesignToken]:
        """Load design tokens from file"""
        if self.tokens_file.exists():
            try:
                with open(self.tokens_file, 'r') as f:
                    data = json.load(f)
                    return {name: DesignToken(**token_data) for name, token_data in data.items()}
            except Exception as e:
                logger.error(f"Error loading design tokens: {e}")
        
        return self._create_default_tokens()
    
    def _load_components(self) -> Dict[str, DesignComponent]:
        """Load design components from file"""
        if self.components_file.exists():
            try:
                with open(self.components_file, 'r') as f:
                    data = json.load(f)
                    return {name: DesignComponent(**comp_data) for name, comp_data in data.items()}
            except Exception as e:
                logger.error(f"Error loading design components: {e}")
        
        return {}
    
    def _load_patterns(self) -> Dict[str, DesignPattern]:
        """Load design patterns from file"""
        if self.patterns_file.exists():
            try:
                with open(self.patterns_file, 'r') as f:
                    data = json.load(f)
                    return {name: DesignPattern(**pattern_data) for name, pattern_data in data.items()}
            except Exception as e:
                logger.error(f"Error loading design patterns: {e}")
        
        return self._create_default_patterns()
    
    def _create_default_tokens(self) -> Dict[str, DesignToken]:
        """Create default design tokens"""
        return {
            "primary-color": DesignToken(
                name="primary-color",
                category="color",
                value="#007bff",
                description="Primary brand color",
                usage=["buttons", "links", "highlights"]
            ),
            "secondary-color": DesignToken(
                name="secondary-color",
                category="color",
                value="#6c757d",
                description="Secondary brand color",
                usage=["text", "borders", "backgrounds"]
            ),
            "success-color": DesignToken(
                name="success-color",
                category="color",
                value="#28a745",
                description="Success state color",
                usage=["success messages", "completed states"]
            ),
            "error-color": DesignToken(
                name="error-color",
                category="color",
                value="#dc3545",
                description="Error state color",
                usage=["error messages", "validation errors"]
            ),
            "font-family": DesignToken(
                name="font-family",
                category="typography",
                value="'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
                description="Primary font family",
                usage=["body text", "headings"]
            ),
            "font-size-base": DesignToken(
                name="font-size-base",
                category="typography",
                value="16px",
                description="Base font size",
                usage=["body text", "default text"]
            ),
            "spacing-unit": DesignToken(
                name="spacing-unit",
                category="spacing",
                value="8px",
                description="Base spacing unit",
                usage=["margins", "padding", "gaps"]
            )
        }
    
    def _create_default_patterns(self) -> Dict[str, DesignPattern]:
        """Create default design patterns"""
        return {
            "card-layout": DesignPattern(
                name="card-layout",
                description="Consistent card-based layout pattern",
                use_cases=["product displays", "content sections", "information grouping"],
                examples=["Product cards", "Feature cards", "Content cards"],
                accessibility_notes="Ensure proper heading hierarchy and keyboard navigation"
            ),
            "form-validation": DesignPattern(
                name="form-validation",
                description="Consistent form validation and error display",
                use_cases=["user input forms", "data entry", "settings"],
                examples=["Login forms", "Registration forms", "Settings forms"],
                accessibility_notes="Provide clear error messages and ARIA labels"
            ),
            "navigation-breadcrumb": DesignPattern(
                name="navigation-breadcrumb",
                description="Breadcrumb navigation pattern",
                use_cases=["deep navigation", "hierarchical content", "user orientation"],
                examples=["E-commerce categories", "Document navigation", "File systems"],
                accessibility_notes="Use proper ARIA landmarks and keyboard navigation"
            )
        }
    
    def add_token(self, token: DesignToken) -> bool:
        """Add a new design token"""
        try:
            self.tokens[token.name] = token
            self._save_tokens()
            logger.info(f"Added design token: {token.name}")
            return True
        except Exception as e:
            logger.error(f"Error adding design token: {e}")
            return False
    
    def add_component(self, component: DesignComponent) -> bool:
        """Add a new design component"""
        try:
            self.components[component.name] = component
            self._save_components()
            logger.info(f"Added design component: {component.name}")
            return True
        except Exception as e:
            logger.error(f"Error adding design component: {e}")
            return False
    
    def add_pattern(self, pattern: DesignPattern) -> bool:
        """Add a new design pattern"""
        try:
            self.patterns[pattern.name] = pattern
            self._save_patterns()
            logger.info(f"Added design pattern: {pattern.name}")
            return True
        except Exception as e:
            logger.error(f"Error adding design pattern: {e}")
            return False
    
    def validate_design_consistency(self, design_description: str) -> Dict:
        """
        Validate design consistency against established patterns
        
        Args:
            design_description: Description of design change
            
        Returns:
            Consistency validation result
        """
        description_lower = design_description.lower()
        
        # Check for token usage
        used_tokens = []
        for token_name, token in self.tokens.items():
            if token_name.replace("-", " ") in description_lower:
                used_tokens.append(token_name)
        
        # Check for component usage
        used_components = []
        for comp_name, component in self.components.items():
            if comp_name.replace("-", " ") in description_lower:
                used_components.append(comp_name)
        
        # Check for pattern usage
        used_patterns = []
        for pattern_name, pattern in self.patterns.items():
            if pattern_name.replace("-", " ") in description_lower:
                used_patterns.append(pattern_name)
        
        # Calculate consistency score
        total_elements = len(used_tokens) + len(used_components) + len(used_patterns)
        consistency_score = min(total_elements / 5, 1.0)  # Normalize to 0-1
        
        # Generate suggestions
        suggestions = []
        if not used_tokens:
            suggestions.append("Consider using established design tokens for consistency")
        if not used_components:
            suggestions.append("Consider using existing design components")
        if not used_patterns:
            suggestions.append("Consider following established design patterns")
        
        return {
            "consistency_score": consistency_score,
            "used_tokens": used_tokens,
            "used_components": used_components,
            "used_patterns": used_patterns,
            "suggestions": suggestions,
            "is_consistent": consistency_score >= 0.6
        }
    
    def get_design_system_summary(self) -> Dict:
        """Get a summary of the design system"""
        return {
            "tokens_count": len(self.tokens),
            "components_count": len(self.components),
            "patterns_count": len(self.patterns),
            "token_categories": list(set(token.category for token in self.tokens.values())),
            "component_categories": list(set(comp.category for comp in self.components.values())),
            "recent_components": sorted(
                self.components.values(),
                key=lambda x: x.last_used,
                reverse=True
            )[:5]
        }
    
    def _save_tokens(self):
        """Save design tokens to file"""
        try:
            with open(self.tokens_file, 'w') as f:
                json.dump(
                    {name: asdict(token) for name, token in self.tokens.items()},
                    f,
                    indent=2
                )
        except Exception as e:
            logger.error(f"Error saving design tokens: {e}")
    
    def _save_components(self):
        """Save design components to file"""
        try:
            with open(self.components_file, 'w') as f:
                json.dump(
                    {name: asdict(component) for name, component in self.components.items()},
                    f,
                    indent=2
                )
        except Exception as e:
            logger.error(f"Error saving design components: {e}")
    
    def _save_patterns(self):
        """Save design patterns to file"""
        try:
            with open(self.patterns_file, 'w') as f:
                json.dump(
                    {name: asdict(pattern) for name, pattern in self.patterns.items()},
                    f,
                    indent=2
                )
        except Exception as e:
            logger.error(f"Error saving design patterns: {e}")


def validate_design_consistency(design_description: str, project_path: str) -> Dict:
    """Validate design consistency"""
    manager = DesignSystemManager(project_path)
    return manager.validate_design_consistency(design_description)


def get_design_system_summary(project_path: str) -> Dict:
    """Get design system summary"""
    manager = DesignSystemManager(project_path)
    return manager.get_design_system_summary()


