"""
Visual Components - Rich visual elements for enhanced CLI experience.

This module provides:
- Progress bars and status indicators
- Tables and formatted output
- Icons and visual feedback
- Dashboard components
- Charts and graphs (ASCII-based)
"""

import math
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from ..core.ui_enhancement_system import get_ui_enhancement_system


class ProgressBar:
    """Animated progress bar with customizable styling."""

    def __init__(self, total: int, width: int = 40, user_id: str = "default"):
        self.total = total
        self.width = width
        self.current = 0
        self.user_id = user_id
        self.start_time = time.time()
        self.ui_system = None

    def _get_ui_system(self, root: Path):
        """Lazy load UI system to avoid circular imports."""
        if self.ui_system is None:
            self.ui_system = get_ui_enhancement_system(root)
        return self.ui_system

    def update(self, current: int, root: Path, message: str = "") -> str:
        """Update progress and return formatted string."""
        self.current = min(current, self.total)
        ui_system = self._get_ui_system(root)

        # Calculate percentage
        percentage = (self.current / self.total * 100) if self.total > 0 else 0

        # Create progress bar
        filled = int(self.width * self.current / self.total) if self.total > 0 else 0
        bar = "█" * filled + "░" * (self.width - filled)

        # Calculate ETA
        elapsed = time.time() - self.start_time
        if self.current > 0 and self.current < self.total:
            eta_seconds = (elapsed / self.current) * (self.total - self.current)
            eta = self._format_time(eta_seconds)
        else:
            eta = "00:00"

        # Format output
        progress_text = f"{bar} {percentage:5.1f}% ({self.current}/{self.total})"

        if message:
            progress_text += f" - {message}"

        if eta != "00:00":
            progress_text += f" ETA: {eta}"

        return ui_system.format_output(progress_text, "primary", self.user_id)

    def _format_time(self, seconds: float) -> str:
        """Format time duration."""
        if seconds < 60:
            return f"{int(seconds):02d}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes:02d}:{secs:02d}"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h{minutes:02d}m"


class StatusIndicator:
    """Status indicators with icons and colors."""

    def __init__(self, root: Path, user_id: str = "default"):
        self.ui_system = get_ui_enhancement_system(root)
        self.user_id = user_id

    def success(self, message: str) -> str:
        """Format success message."""
        return (
            f"{self.ui_system.format_output('✅', 'success', self.user_id)} {message}"
        )

    def warning(self, message: str) -> str:
        """Format warning message."""
        return f"{self.ui_system.format_output('⚠️', 'warning', self.user_id)} {message}"

    def error(self, message: str) -> str:
        """Format error message."""
        return f"{self.ui_system.format_output('❌', 'error', self.user_id)} {message}"

    def info(self, message: str) -> str:
        """Format info message."""
        return f"{self.ui_system.format_output('ℹ️', 'info', self.user_id)} {message}"

    def progress(self, message: str) -> str:
        """Format progress message."""
        return (
            f"{self.ui_system.format_output('🔄', 'primary', self.user_id)} {message}"
        )

    def completed(self, message: str) -> str:
        """Format completed message."""
        return (
            f"{self.ui_system.format_output('✨', 'success', self.user_id)} {message}"
        )


class Table:
    """ASCII table formatter with alignment and styling."""

    def __init__(self, headers: List[str], root: Path, user_id: str = "default"):
        self.headers = headers
        self.rows: List[List[str]] = []
        self.ui_system = get_ui_enhancement_system(root)
        self.user_id = user_id
        self.column_widths: List[int] = [len(h) for h in headers]

    def add_row(self, row: List[str]):
        """Add a row to the table."""
        # Convert all items to strings
        str_row = [str(item) for item in row]
        self.rows.append(str_row)

        # Update column widths
        for i, cell in enumerate(str_row):
            if i < len(self.column_widths):
                self.column_widths[i] = max(self.column_widths[i], len(cell))

    def render(self, max_width: Optional[int] = None) -> str:
        """Render the table as a string."""
        if not self.rows:
            return "No data to display"

        # Adjust column widths if max_width is specified
        if max_width:
            total_width = sum(self.column_widths) + len(self.headers) * 3 + 1
            if total_width > max_width:
                # Proportionally reduce column widths
                reduction_factor = (max_width - len(self.headers) * 3 - 1) / sum(
                    self.column_widths
                )
                self.column_widths = [
                    max(10, int(w * reduction_factor)) for w in self.column_widths
                ]

        lines = []

        # Header
        header_line = "│"
        for i, header in enumerate(self.headers):
            header_line += f" {header:<{self.column_widths[i]}} │"
        lines.append(self.ui_system.format_output(header_line, "primary", self.user_id))

        # Separator
        separator = "├"
        for width in self.column_widths:
            separator += "─" * (width + 2) + "┼"
        separator = separator[:-1] + "┤"
        lines.append(separator)

        # Rows
        for row in self.rows:
            row_line = "│"
            for i, cell in enumerate(row):
                if i < len(self.column_widths):
                    # Truncate if too long
                    if len(cell) > self.column_widths[i]:
                        cell = cell[: self.column_widths[i] - 3] + "..."
                    row_line += f" {cell:<{self.column_widths[i]}} │"
            lines.append(row_line)

        # Bottom border
        bottom = "└"
        for width in self.column_widths:
            bottom += "─" * (width + 2) + "┴"
        bottom = bottom[:-1] + "┘"
        lines.append(bottom)

        return "\n".join(lines)


class Chart:
    """ASCII chart generator for simple data visualization."""

    def __init__(self, root: Path, user_id: str = "default"):
        self.ui_system = get_ui_enhancement_system(root)
        self.user_id = user_id

    def bar_chart(
        self, data: Dict[str, float], title: str = "", max_width: int = 50
    ) -> str:
        """Create horizontal bar chart."""
        if not data:
            return "No data to display"

        lines = []

        if title:
            lines.append(self.ui_system.format_output(title, "primary", self.user_id))
            lines.append("=" * min(len(title), max_width))
            lines.append("")

        # Find max value for scaling
        max_value = max(data.values()) if data.values() else 1

        # Calculate label width
        max_label_width = max(len(str(key)) for key in data.keys())
        bar_width = max_width - max_label_width - 10  # Space for label and value

        for key, value in data.items():
            # Scale bar length
            bar_length = int((value / max_value) * bar_width) if max_value > 0 else 0
            bar = "█" * bar_length + "░" * (bar_width - bar_length)

            # Format line
            line = f"{key:<{max_label_width}} │{bar}│ {value}"
            lines.append(line)

        return "\n".join(lines)

    def sparkline(self, values: List[float], width: int = 20) -> str:
        """Create a sparkline chart."""
        if not values:
            return "─" * width

        min_val = min(values)
        max_val = max(values)

        if min_val == max_val:
            return "─" * width

        # Unicode block elements for sparklines
        blocks = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]

        sparkline = ""
        for value in values:
            # Normalize value to 0-7 range
            normalized = (value - min_val) / (max_val - min_val)
            block_index = min(int(normalized * len(blocks)), len(blocks) - 1)
            sparkline += blocks[block_index]

        # Truncate or pad to desired width
        if len(sparkline) > width:
            sparkline = sparkline[:width]
        else:
            sparkline += "─" * (width - len(sparkline))

        return sparkline


class Dashboard:
    """Dashboard component for status overview."""

    def __init__(self, root: Path, user_id: str = "default"):
        self.root = root
        self.ui_system = get_ui_enhancement_system(root)
        self.user_id = user_id
        self.status_indicator = StatusIndicator(root, user_id)
        self.chart = Chart(root, user_id)

    def create_project_dashboard(self, project_data: Dict[str, Any]) -> str:
        """Create project status dashboard."""
        dashboard = []

        # Header
        dashboard.append(
            self.ui_system.format_output(
                "🚀 Project Dashboard", "primary", self.user_id
            )
        )
        dashboard.append("=" * 50)
        dashboard.append("")

        # Project info
        if "name" in project_data:
            dashboard.append(f"Project: {project_data['name']}")
        if "phase" in project_data:
            dashboard.append(f"Phase: {project_data['phase']}")
        dashboard.append("")

        # Progress overview
        if "progress" in project_data:
            progress = project_data["progress"]
            dashboard.append(
                self.ui_system.format_output(
                    "📊 Progress Overview", "info", self.user_id
                )
            )

            if "completion_percentage" in progress:
                percentage = progress["completion_percentage"]
                bar = self.ui_system.get_progress_bar(
                    int(percentage), 100, 30, self.user_id
                )
                dashboard.append(f"Overall: {bar}")

            if "completed_tasks" in progress and "total_tasks" in progress:
                completed = progress["completed_tasks"]
                total = progress["total_tasks"]
                dashboard.append(f"Tasks: {completed}/{total} completed")

            dashboard.append("")

        # Milestones
        if "milestones" in project_data:
            dashboard.append(
                self.ui_system.format_output("🎯 Milestones", "info", self.user_id)
            )

            for milestone in project_data["milestones"][:5]:  # Show top 5
                name = milestone.get("name", "Unknown")
                status = milestone.get("status", "unknown")
                progress_pct = milestone.get("progress_percentage", 0)

                if status == "completed":
                    status_icon = "✅"
                elif status == "in_progress":
                    status_icon = "🔄"
                else:
                    status_icon = "⏳"

                bar = self.ui_system.get_progress_bar(
                    int(progress_pct), 100, 15, self.user_id
                )
                dashboard.append(f"  {status_icon} {name}: {bar}")

            dashboard.append("")

        # Recent activity
        if "recent_activity" in project_data:
            dashboard.append(
                self.ui_system.format_output(
                    "📝 Recent Activity", "secondary", self.user_id
                )
            )
            for activity in project_data["recent_activity"][:3]:
                dashboard.append(f"  • {activity}")
            dashboard.append("")

        # Quick actions
        dashboard.append(
            self.ui_system.format_output("⚡ Quick Actions", "secondary", self.user_id)
        )
        quick_actions = [
            "ai_onboard prompt progress - Check detailed progress",
            "ai_onboard validate - Run quality checks",
            "ai_onboard suggest - Get recommendations",
        ]

        for action in quick_actions:
            dashboard.append(f"  • {action}")

        return "\n".join(dashboard)

    def create_system_health_dashboard(self, health_data: Dict[str, Any]) -> str:
        """Create system health dashboard."""
        dashboard = []

        dashboard.append(
            self.ui_system.format_output("💚 System Health", "primary", self.user_id)
        )
        dashboard.append("=" * 40)
        dashboard.append("")

        # Overall health score
        if "overall_score" in health_data:
            score = health_data["overall_score"]
            if score >= 0.9:
                status = self.status_indicator.success(f"Excellent ({score:.1%})")
            elif score >= 0.7:
                status = self.status_indicator.info(f"Good ({score:.1%})")
            elif score >= 0.5:
                status = self.status_indicator.warning(f"Fair ({score:.1%})")
            else:
                status = self.status_indicator.error(f"Poor ({score:.1%})")

            dashboard.append(f"Overall Health: {status}")
            dashboard.append("")

        # Component status
        if "components" in health_data:
            dashboard.append(
                self.ui_system.format_output("🔧 Components", "info", self.user_id)
            )

            for component, status in health_data["components"].items():
                if status == "healthy":
                    indicator = self.status_indicator.success("OK")
                elif status == "warning":
                    indicator = self.status_indicator.warning("WARN")
                else:
                    indicator = self.status_indicator.error("ERROR")

                dashboard.append(f"  {component}: {indicator}")

            dashboard.append("")

        # Metrics chart
        if "metrics_trend" in health_data:
            dashboard.append(
                self.ui_system.format_output(
                    "📈 Trend (7 days)", "secondary", self.user_id
                )
            )
            sparkline = self.chart.sparkline(health_data["metrics_trend"], 30)
            dashboard.append(f"  Health: {sparkline}")
            dashboard.append("")

        return "\n".join(dashboard)


class AnimatedSpinner:
    """Animated spinner for long-running operations."""

    def __init__(self, root: Path, user_id: str = "default"):
        self.ui_system = get_ui_enhancement_system(root)
        self.user_id = user_id
        self.frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.current_frame = 0

    def next_frame(self, message: str = "") -> str:
        """Get next spinner frame with message."""
        frame = self.frames[self.current_frame]
        self.current_frame = (self.current_frame + 1) % len(self.frames)

        spinner_text = self.ui_system.format_output(frame, "primary", self.user_id)

        if message:
            return f"{spinner_text} {message}"
        else:
            return spinner_text


# Utility functions for easy access
def create_progress_bar(
    total: int, width: int = 40, user_id: str = "default"
) -> ProgressBar:
    """Create a progress bar."""
    return ProgressBar(total, width, user_id)


def create_table(headers: List[str], root: Path, user_id: str = "default") -> Table:
    """Create a table."""
    return Table(headers, root, user_id)


def create_status_indicator(root: Path, user_id: str = "default") -> StatusIndicator:
    """Create a status indicator."""
    return StatusIndicator(root, user_id)


def create_chart(root: Path, user_id: str = "default") -> Chart:
    """Create a chart."""
    return Chart(root, user_id)


def create_dashboard(root: Path, user_id: str = "default") -> Dashboard:
    """Create a dashboard."""
    return Dashboard(root, user_id)


def create_spinner(root: Path, user_id: str = "default") -> AnimatedSpinner:
    """Create an animated spinner."""
    return AnimatedSpinner(root, user_id)
