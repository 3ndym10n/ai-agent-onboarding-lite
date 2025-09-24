"""
Test suite for the unified tool orchestration system.

This comprehensive test suite validates:
- UnifiedToolOrchestrator functionality
- Backward compatibility with all legacy systems
- Strategy routing and execution
- Error handling and safety features
"""

import pytest
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

# Test the unified system
from ai_onboard.core.unified_tool_orchestrator import (
    UnifiedToolOrchestrator,
    UnifiedOrchestrationStrategy,
    UnifiedToolCategory,
    ToolExecutionContext,
    UnifiedOrchestrationResult,
    get_unified_tool_orchestrator
)

# Test backward compatibility
from ai_onboard.core.orchestration_compatibility import (
    IntelligentToolOrchestrator,
    HolisticToolOrchestrator,
    AIAgentOrchestrationLayer,
    AutoApplicableTools,
    OrchestrationStrategy,
    migrate_to_unified_orchestrator,
    get_legacy_orchestrator_type
)


class TestUnifiedToolOrchestrator:
    """Test the core unified orchestrator functionality."""
    
    @pytest.fixture
    def temp_root(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def orchestrator(self, temp_root):
        """Create a test orchestrator instance."""
        return UnifiedToolOrchestrator(temp_root)
    
    def test_orchestrator_initialization(self, orchestrator, temp_root):
        """Test that orchestrator initializes correctly."""
        assert orchestrator.root_path == temp_root
        assert orchestrator.tool_tracker is not None
        assert orchestrator.discovery is not None
        assert orchestrator.pattern_system is not None
        assert orchestrator.user_preference_system is not None
        assert isinstance(orchestrator.execution_history, list)
        assert isinstance(orchestrator.tool_triggers, dict)
    
    def test_unified_strategies(self):
        """Test that all unified strategies are properly defined."""
        strategies = [
            UnifiedOrchestrationStrategy.VISION_FIRST,
            UnifiedOrchestrationStrategy.USER_PREFERENCE_DRIVEN,
            UnifiedOrchestrationStrategy.SAFETY_FIRST,
            UnifiedOrchestrationStrategy.COMPREHENSIVE_ANALYSIS,
            UnifiedOrchestrationStrategy.ADAPTIVE,
            UnifiedOrchestrationStrategy.TRIGGER_BASED,
            UnifiedOrchestrationStrategy.LEARNING_DRIVEN,
            UnifiedOrchestrationStrategy.SESSION_AWARE,
            UnifiedOrchestrationStrategy.ROLLBACK_SAFE
        ]
        
        for strategy in strategies:
            assert isinstance(strategy.value, str)
            assert len(strategy.value) > 0
    
    def test_unified_tool_categories(self):
        """Test that all tool categories are properly defined."""
        categories = [
            UnifiedToolCategory.CODE_QUALITY,
            UnifiedToolCategory.FILE_ORGANIZATION,
            UnifiedToolCategory.DEPENDENCY_ANALYSIS,
            UnifiedToolCategory.DUPLICATE_DETECTION,
            UnifiedToolCategory.VISION_ALIGNMENT,
            UnifiedToolCategory.USER_PREFERENCES,
            UnifiedToolCategory.SAFETY_CHECKS,
            UnifiedToolCategory.SESSION_MANAGEMENT
        ]
        
        for category in categories:
            assert isinstance(category.value, str)
            assert len(category.value) > 0
    
    def test_tool_execution_context(self):
        """Test ToolExecutionContext creation and usage."""
        context = ToolExecutionContext(
            user_request="test request",
            strategy=UnifiedOrchestrationStrategy.ADAPTIVE,
            session_id="test_session"
        )
        
        assert context.user_request == "test request"
        assert context.strategy == UnifiedOrchestrationStrategy.ADAPTIVE
        assert context.session_id == "test_session"
        assert context.user_id == "default"
        assert context.rollback_enabled is True
    
    @patch('ai_onboard.core.unified_tool_orchestrator.get_tool_tracker')
    @patch('ai_onboard.core.unified_tool_orchestrator.get_comprehensive_tool_discovery')
    def test_orchestrate_tools_adaptive(self, mock_discovery, mock_tracker, temp_root):
        """Test adaptive orchestration strategy."""
        # Mock the dependencies
        mock_tracker.return_value = Mock()
        mock_discovery.return_value = Mock()
        
        orchestrator = UnifiedToolOrchestrator(temp_root)
        
        result = orchestrator.orchestrate_tools(
            user_request="analyze code quality",
            strategy=UnifiedOrchestrationStrategy.ADAPTIVE
        )
        
        assert isinstance(result, UnifiedOrchestrationResult)
        assert result.total_execution_time >= 0
    
    def test_strategy_routing(self, orchestrator):
        """Test that different strategies route to correct execution methods."""
        
        # Mock the execution methods
        orchestrator._execute_intelligent_orchestration = Mock(return_value=UnifiedOrchestrationResult())
        orchestrator._execute_holistic_orchestration = Mock(return_value=UnifiedOrchestrationResult())
        orchestrator._execute_session_orchestration = Mock(return_value=UnifiedOrchestrationResult())
        orchestrator._execute_adaptive_orchestration = Mock(return_value=UnifiedOrchestrationResult())
        
        # Test trigger-based strategy
        orchestrator.orchestrate_tools(
            "test", strategy=UnifiedOrchestrationStrategy.TRIGGER_BASED
        )
        orchestrator._execute_intelligent_orchestration.assert_called_once()
        
        # Test holistic strategy
        orchestrator.orchestrate_tools(
            "test", strategy=UnifiedOrchestrationStrategy.VISION_FIRST
        )
        orchestrator._execute_holistic_orchestration.assert_called_once()
        
        # Test session strategy
        orchestrator.orchestrate_tools(
            "test", strategy=UnifiedOrchestrationStrategy.SESSION_AWARE
        )
        orchestrator._execute_session_orchestration.assert_called_once()
        
        # Test adaptive strategy
        orchestrator.orchestrate_tools(
            "test", strategy=UnifiedOrchestrationStrategy.ADAPTIVE
        )
        orchestrator._execute_adaptive_orchestration.assert_called_once()
    
    def test_singleton_factory(self, temp_root):
        """Test that the factory function returns singleton instances."""
        orchestrator1 = get_unified_tool_orchestrator(temp_root)
        orchestrator2 = get_unified_tool_orchestrator(temp_root)
        
        assert orchestrator1 is orchestrator2
        assert isinstance(orchestrator1, UnifiedToolOrchestrator)


class TestBackwardCompatibility:
    """Test backward compatibility with legacy orchestration systems."""
    
    @pytest.fixture
    def temp_root(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @patch('ai_onboard.core.orchestration_compatibility.get_unified_tool_orchestrator')
    def test_intelligent_orchestrator_compatibility(self, mock_get_unified, temp_root):
        """Test IntelligentToolOrchestrator backward compatibility."""
        mock_unified = Mock()
        mock_get_unified.return_value = mock_unified
        
        with pytest.warns(DeprecationWarning):
            legacy_orchestrator = IntelligentToolOrchestrator(temp_root)
        
        assert legacy_orchestrator.root_path == temp_root
        assert legacy_orchestrator._unified_orchestrator == mock_unified
        
        # Test conversation analysis
        mock_unified._analyze_triggers.return_value = [{"tool": "test", "confidence": 0.8}]
        
        result = legacy_orchestrator.analyze_conversation_for_tool_application(
            [{"content": "test message"}], {"context": "test"}
        )
        
        assert len(result) == 1
        assert result[0]["tool"] == "test"
        
        # Test tool execution
        mock_unified._execute_tool_safely.return_value = {"success": True}
        
        result = legacy_orchestrator.execute_automatic_tool_application(
            "test_tool", {"user_request": "test"}
        )
        
        assert result["tool"] == "test_tool"
        assert result["executed"] is True
    
    @patch('ai_onboard.core.orchestration_compatibility.get_unified_tool_orchestrator')
    def test_holistic_orchestrator_compatibility(self, mock_get_unified, temp_root):
        """Test HolisticToolOrchestrator backward compatibility."""
        mock_unified = Mock()
        mock_unified.orchestrate_tools.return_value = UnifiedOrchestrationResult()
        mock_get_unified.return_value = mock_unified
        
        with pytest.warns(DeprecationWarning):
            legacy_orchestrator = HolisticToolOrchestrator(temp_root)
        
        result = legacy_orchestrator.orchestrate_tools_for_request(
            "test request", strategy="adaptive"
        )
        
        # Verify the result is converted to legacy format
        assert hasattr(result, 'success')
        assert hasattr(result, 'executed_tools')
        assert hasattr(result, 'vision_alignment_score')
        assert hasattr(result, 'user_preference_compliance')
        assert hasattr(result, 'safety_compliance')
    
    @patch('ai_onboard.core.orchestration_compatibility.get_unified_tool_orchestrator')
    def test_ai_agent_orchestrator_compatibility(self, mock_get_unified, temp_root):
        """Test AIAgentOrchestrationLayer backward compatibility."""
        mock_unified = Mock()
        mock_unified.orchestrate_tools.return_value = UnifiedOrchestrationResult()
        mock_get_unified.return_value = mock_unified
        
        with pytest.warns(DeprecationWarning):
            legacy_orchestrator = AIAgentOrchestrationLayer(temp_root)
        
        # Test session creation
        session_id = legacy_orchestrator.create_session("test_user")
        assert session_id.startswith("session_")
        assert session_id in legacy_orchestrator.sessions
        
        # Test conversation processing
        result = legacy_orchestrator.process_conversation(session_id, "test input")
        assert "session_id" in result
        assert "success" in result
        
        # Test session status
        status = legacy_orchestrator.get_session_status(session_id)
        assert status["session_id"] == session_id
        assert status["user_id"] == "test_user"
    
    def test_legacy_enums_compatibility(self):
        """Test that legacy enum values are preserved."""
        
        # Test AutoApplicableTools
        assert AutoApplicableTools.CODE_QUALITY_ANALYSIS == "code_quality_analysis"
        assert AutoApplicableTools.ORGANIZATION_ANALYSIS == "organization_analysis"
        assert AutoApplicableTools.RISK_ASSESSMENT == "risk_assessment"
        
        # Test OrchestrationStrategy
        assert OrchestrationStrategy.VISION_FIRST == "vision_first"
        assert OrchestrationStrategy.SAFETY_FIRST == "safety_first"
        assert OrchestrationStrategy.ADAPTIVE == "adaptive"
    
    @patch('ai_onboard.core.orchestration_compatibility.get_unified_tool_orchestrator')
    def test_migration_helpers(self, mock_get_unified, temp_root):
        """Test migration helper functions."""
        mock_unified = Mock(spec=UnifiedToolOrchestrator)
        mock_get_unified.return_value = mock_unified
        
        # Test migration function
        result = migrate_to_unified_orchestrator(temp_root)
        assert result == mock_unified
        
        # Test legacy type detection
        with pytest.warns(DeprecationWarning):
            intelligent = IntelligentToolOrchestrator(temp_root)
            holistic = HolisticToolOrchestrator(temp_root)
            ai_agent = AIAgentOrchestrationLayer(temp_root)
        
        assert get_legacy_orchestrator_type(intelligent) == "intelligent"
        assert get_legacy_orchestrator_type(holistic) == "holistic"
        assert get_legacy_orchestrator_type(ai_agent) == "ai_agent"
        assert get_legacy_orchestrator_type(mock_unified) == "unified"
        assert get_legacy_orchestrator_type("unknown") == "unknown"


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    @pytest.fixture
    def temp_root(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @patch('ai_onboard.core.unified_tool_orchestrator.get_tool_tracker')
    def test_orchestration_error_handling(self, mock_tracker, temp_root):
        """Test that orchestration errors are handled gracefully."""
        mock_tracker.return_value = Mock()
        
        orchestrator = UnifiedToolOrchestrator(temp_root)
        
        # Mock an error in the execution phase, not the tracking phase
        orchestrator._execute_adaptive_orchestration = Mock(side_effect=Exception("Execution error"))
        
        # This should not raise an exception despite the execution error
        result = orchestrator.orchestrate_tools("test request")
        
        # The result should indicate failure but not crash
        assert isinstance(result, UnifiedOrchestrationResult)
        assert result.total_execution_time >= 0
        assert len(result.errors) > 0
        assert "Unified orchestration failed" in result.errors[0]
    
    def test_invalid_strategy_handling(self, temp_root):
        """Test handling of invalid strategies."""
        orchestrator = UnifiedToolOrchestrator(temp_root)
        
        # Mock the adaptive orchestration to test fallback
        orchestrator._execute_adaptive_orchestration = Mock(return_value=UnifiedOrchestrationResult())
        
        # Test with a valid strategy that should fallback to adaptive
        result = orchestrator.orchestrate_tools(
            "test", strategy=UnifiedOrchestrationStrategy.ADAPTIVE
        )
        
        assert isinstance(result, UnifiedOrchestrationResult)
        orchestrator._execute_adaptive_orchestration.assert_called_once()


class TestIntegration:
    """Integration tests for the unified orchestration system."""
    
    @pytest.fixture
    def temp_root(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @patch('ai_onboard.core.unified_tool_orchestrator.PatternRecognitionSystem')
    @patch('ai_onboard.core.unified_tool_orchestrator.UserPreferenceLearningSystem')
    @patch('ai_onboard.core.unified_tool_orchestrator.get_tool_tracker')
    @patch('ai_onboard.core.unified_tool_orchestrator.get_comprehensive_tool_discovery')
    def test_full_orchestration_flow(self, mock_discovery, mock_tracker, 
                                   mock_user_prefs, mock_pattern, temp_root):
        """Test a complete orchestration flow from start to finish."""
        
        # Mock all dependencies
        mock_tracker.return_value = Mock()
        mock_discovery.return_value = Mock()
        mock_user_prefs.return_value = Mock()
        mock_pattern.return_value = Mock()
        
        # Create orchestrator
        orchestrator = UnifiedToolOrchestrator(temp_root)
        
        # Create execution context
        context = ToolExecutionContext(
            user_request="analyze code quality and organize files",
            strategy=UnifiedOrchestrationStrategy.COMPREHENSIVE_ANALYSIS,
            session_id="integration_test_session"
        )
        
        # Execute orchestration
        result = orchestrator.orchestrate_tools(
            user_request=context.user_request,
            context=context,
            strategy=context.strategy
        )
        
        # Verify results
        assert isinstance(result, UnifiedOrchestrationResult)
        assert result.total_execution_time >= 0
        
        # Verify tracking was called
        mock_tracker.return_value.track_tool_usage.assert_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
