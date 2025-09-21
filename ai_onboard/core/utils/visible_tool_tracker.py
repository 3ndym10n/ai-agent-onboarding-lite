"""
Visible Tool Usage Tracker

Shows the user exactly what tools are being used and the quality of their outcomes.
This addresses the user's need to see when agents are actively using the built tools.
"""

# Import read_json, write_json from utils.py module (parent directory)
import importlib.util
import time
_utils_spec.loader.exec_module(_utils_module)
read_json = _utils_module.read_json
write_json = _utils_module.write_json


class ToolQualityLevel(Enum):
    """Quality levels for tool outcomes."""

    EXCELLENT = "excellent"  # Tool worked perfectly, high value
    GOOD = "good"  # Tool worked well, some value
    FAIR = "fair"  # Tool worked but limited value
    POOR = "poor"  # Tool had issues, low value
    FAILED = "failed"  # Tool failed completely


@dataclass
class ToolUsageEvent:
    """Represents a single tool usage event."""

    timestamp: float
    tool_name: str
    tool_type: str
    context: str
    input_summary: str
    execution_time: float
    quality_level: ToolQualityLevel
    outcome_summary: str
    insights_generated: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    user_visible: bool = True


@dataclass
class ToolQualityMetrics:
    """Quality metrics for a tool."""

    total_uses: int = 0
    excellent_count: int = 0
    good_count: int = 0
    fair_count: int = 0
    poor_count: int = 0
    failed_count: int = 0
    average_execution_time: float = 0.0
    success_rate: float = 0.0
    quality_score: float = 0.0  # 0-100 scale


class VisibleToolTracker:
    """
    Tracks and displays tool usage in a user-visible way.

    This system ensures the user can see:
    1. What tools are being used
    2. Quality level of outcomes
    3. When tools are being consulted
    4. Success/failure rates
    """

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.tracking_path = root_path / ".ai_onboard" / "visible_tool_tracking.jsonl"
        self.metrics_path = root_path / ".ai_onboard" / "tool_quality_metrics.json"

        # Ensure tracking directory exists
        self.tracking_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing metrics
        self.tool_metrics = self._load_tool_metrics()

        # Current session tracking
        self.current_session_events: List[ToolUsageEvent] = []
        self.session_start_time = time.time()

    def _load_tool_metrics(self) -> Dict[str, ToolQualityMetrics]:
        """Load existing tool quality metrics."""
        try:
            data = read_json(self.metrics_path, default={})
            metrics = {}
            for tool_name, tool_data in data.items():
                metrics[tool_name] = ToolQualityMetrics(**tool_data)
            return metrics
        except Exception:
            return {}

    def _save_tool_metrics(self):
        """Save tool quality metrics."""
        try:
            data = {}
            for tool_name, metrics in self.tool_metrics.items():
                data[tool_name] = {
                    "total_uses": metrics.total_uses,
                    "excellent_count": metrics.excellent_count,
                    "good_count": metrics.good_count,
                    "fair_count": metrics.fair_count,
                    "poor_count": metrics.poor_count,
                    "failed_count": metrics.failed_count,
                    "average_execution_time": metrics.average_execution_time,
                    "success_rate": metrics.success_rate,
                    "quality_score": metrics.quality_score,
                }
            write_json(self.metrics_path, data)
        except Exception as e:
            print(f"⚠️ Failed to save tool metrics: {e}")

    def track_tool_usage(
        self,
        tool_name: str,
        tool_type: str,
        context: str,
        input_summary: str,
        execution_time: float,
        quality_level: ToolQualityLevel,
        outcome_summary: str,
        insights: List[str] = None,
        errors: List[str] = None,
        user_visible: bool = True,
    ) -> ToolUsageEvent:
        """Track a tool usage event and display it to the user."""

        if insights is None:
            insights = []
        if errors is None:
            errors = []

        # Create the event
        event = ToolUsageEvent(
            timestamp=time.time(),
            tool_name=tool_name,
            tool_type=tool_type,
            context=context,
            input_summary=input_summary,
            execution_time=execution_time,
            quality_level=quality_level,
            outcome_summary=outcome_summary,
            insights_generated=insights,
            errors=errors,
            user_visible=user_visible,
        )

        # Add to current session
        self.current_session_events.append(event)

        # Update metrics
        self._update_tool_metrics(tool_name, event)

        # Display to user if visible
        if user_visible:
            self._display_tool_usage(event)

        # Save to persistent storage
        self._save_tool_event(event)

        return event

    def _update_tool_metrics(self, tool_name: str, event: ToolUsageEvent):
        """Update quality metrics for a tool."""
        if tool_name not in self.tool_metrics:
            self.tool_metrics[tool_name] = ToolQualityMetrics()

        metrics = self.tool_metrics[tool_name]
        metrics.total_uses += 1

        # Update quality counts
        if event.quality_level == ToolQualityLevel.EXCELLENT:
            metrics.excellent_count += 1
        elif event.quality_level == ToolQualityLevel.GOOD:
            metrics.good_count += 1
        elif event.quality_level == ToolQualityLevel.FAIR:
            metrics.fair_count += 1
        elif event.quality_level == ToolQualityLevel.POOR:
            metrics.poor_count += 1
        elif event.quality_level == ToolQualityLevel.FAILED:
            metrics.failed_count += 1

        # Update execution time average
        total_time = metrics.average_execution_time * (metrics.total_uses - 1)
        metrics.average_execution_time = (
            total_time + event.execution_time
        ) / metrics.total_uses

        # Calculate success rate (excellent + good + fair)
        successful_uses = (
            metrics.excellent_count + metrics.good_count + metrics.fair_count
        )
        metrics.success_rate = (successful_uses / metrics.total_uses) * 100

        # Calculate quality score (weighted average)
        quality_weights = {
            ToolQualityLevel.EXCELLENT: 100,
            ToolQualityLevel.GOOD: 80,
            ToolQualityLevel.FAIR: 60,
            ToolQualityLevel.POOR: 30,
            ToolQualityLevel.FAILED: 0,
        }

        total_quality_score = (
            metrics.excellent_count * quality_weights[ToolQualityLevel.EXCELLENT]
            + metrics.good_count * quality_weights[ToolQualityLevel.GOOD]
            + metrics.fair_count * quality_weights[ToolQualityLevel.FAIR]
            + metrics.poor_count * quality_weights[ToolQualityLevel.POOR]
            + metrics.failed_count * quality_weights[ToolQualityLevel.FAILED]
        )
        metrics.quality_score = total_quality_score / metrics.total_uses

    def _display_tool_usage(self, event: ToolUsageEvent):
        """Display tool usage to the user in a clear, visible way."""

        # Quality emoji mapping
        quality_emoji = {
            ToolQualityLevel.EXCELLENT: "🌟",
            ToolQualityLevel.GOOD: "✅",
            ToolQualityLevel.FAIR: "⚠️",
            ToolQualityLevel.POOR: "❌",
            ToolQualityLevel.FAILED: "💥",
        }

        print(f"\n🔧 TOOL USAGE TRACKER")
        print(f"=" * 50)
        print(f"🛠️  Tool: {event.tool_name}")
        print(f"📂 Type: {event.tool_type}")
        print(f"🎯 Context: {event.context}")
        print(
            f"📝 Input: {event.input_summary[:100]}{'...' if len(event.input_summary) > 100 else ''}"
        )
        print(f"⏱️  Execution Time: {event.execution_time:.2f}s")
        print(
            f"{quality_emoji[event.quality_level]} Quality: {event.quality_level.value.upper()}"
        )
        print(f"📊 Outcome: {event.outcome_summary}")

        if event.insights_generated:
            print(f"💡 Insights Generated:")
            for insight in event.insights_generated:
                print(f"   • {insight}")

        if event.errors:
            print(f"⚠️ Errors:")
            for error in event.errors:
                print(f"   • {error}")

        print(f"=" * 50)

    def _save_tool_event(self, event: ToolUsageEvent):
        """Save tool event to persistent storage."""
        try:
            event_data = {
                "timestamp": event.timestamp,
                "tool_name": event.tool_name,
                "tool_type": event.tool_type,
                "context": event.context,
                "input_summary": event.input_summary,
                "execution_time": event.execution_time,
                "quality_level": event.quality_level.value,
                "outcome_summary": event.outcome_summary,
                "insights_generated": event.insights_generated,
                "errors": event.errors,
                "user_visible": event.user_visible,
            }

            with open(self.tracking_path, "a", encoding="utf-8") as f:
                import json

                f.write(json.dumps(event_data) + "\n")
        except Exception as e:
            print(f"⚠️ Failed to save tool event: {e}")

    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session tool usage."""
        if not self.current_session_events:
            return {"message": "No tools used in this session"}

        total_tools = len(self.current_session_events)
        successful_tools = len(
            [
                e
                for e in self.current_session_events
                if e.quality_level
                in [ToolQualityLevel.EXCELLENT, ToolQualityLevel.GOOD]
            ]
        )
        failed_tools = len(
            [
                e
                for e in self.current_session_events
                if e.quality_level == ToolQualityLevel.FAILED
            ]
        )

        session_duration = time.time() - self.session_start_time

        return {
            "session_duration": session_duration,
            "total_tools_used": total_tools,
            "successful_tools": successful_tools,
            "failed_tools": failed_tools,
            "success_rate": (
                (successful_tools / total_tools) * 100 if total_tools > 0 else 0
            ),
            "tools_used": [e.tool_name for e in self.current_session_events],
            "quality_breakdown": {
                "excellent": len(
                    [
                        e
                        for e in self.current_session_events
                        if e.quality_level == ToolQualityLevel.EXCELLENT
                    ]
                ),
                "good": len(
                    [
                        e
                        for e in self.current_session_events
                        if e.quality_level == ToolQualityLevel.GOOD
                    ]
                ),
                "fair": len(
                    [
                        e
                        for e in self.current_session_events
                        if e.quality_level == ToolQualityLevel.FAIR
                    ]
                ),
                "poor": len(
                    [
                        e
                        for e in self.current_session_events
                        if e.quality_level == ToolQualityLevel.POOR
                    ]
                ),
                "failed": len(
                    [
                        e
                        for e in self.current_session_events
                        if e.quality_level == ToolQualityLevel.FAILED
                    ]
                ),
            },
        }

    def display_session_summary(self):
        """Display current session summary to the user."""
        summary = self.get_session_summary()

        if "message" in summary:
            print(f"\n📊 SESSION SUMMARY: {summary['message']}")
            return

        print(f"\n📊 SESSION TOOL USAGE SUMMARY")
        print(f"=" * 50)
        print(f"⏱️  Session Duration: {summary['session_duration']:.1f}s")
        print(f"🛠️  Total Tools Used: {summary['total_tools_used']}")
        print(f"✅ Successful Tools: {summary['successful_tools']}")
        print(f"❌ Failed Tools: {summary['failed_tools']}")
        print(f"📈 Success Rate: {summary['success_rate']:.1f}%")

        print(f"\n🛠️  Tools Used:")
        for tool in summary["tools_used"]:
            print(f"   • {tool}")

        print(f"\n📊 Quality Breakdown:")
        quality = summary["quality_breakdown"]
        print(f"   🌟 Excellent: {quality['excellent']}")
        print(f"   ✅ Good: {quality['good']}")
        print(f"   ⚠️ Fair: {quality['fair']}")
        print(f"   ❌ Poor: {quality['poor']}")
        print(f"   💥 Failed: {quality['failed']}")
        print(f"=" * 50)

    def get_tool_quality_report(self) -> Dict[str, Any]:
        """Get comprehensive tool quality report."""
        return {
            "tool_metrics": {
                name: {
                    "total_uses": metrics.total_uses,
                    "success_rate": metrics.success_rate,
                    "quality_score": metrics.quality_score,
                    "average_execution_time": metrics.average_execution_time,
                }
                for name, metrics in self.tool_metrics.items()
            },
            "session_summary": self.get_session_summary(),
        }


def get_visible_tool_tracker(root_path: Path) -> VisibleToolTracker:
    """Get the global visible tool tracker instance."""
    global _visible_tracker_instance
    if _visible_tracker_instance is None:
        _visible_tracker_instance = VisibleToolTracker(root_path)
    return _visible_tracker_instance


# Global instance
_visible_tracker_instance: Optional[VisibleToolTracker] = None
