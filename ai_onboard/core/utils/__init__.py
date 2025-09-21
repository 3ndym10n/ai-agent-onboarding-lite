# Utils package for ai-onboard core utilities

from . import (
    cache,
    roadmap_lite,
    scheduler,
    session_storage,
    summarizer,
    tool_usage_tracker,
    versioning,
)

# visible_tool_tracker is imported at the core level for backward compatibility

__all__ = [
    "cache",
    "session_storage",
    "tool_usage_tracker",
    "versioning",
    "scheduler",
    "roadmap_lite",
    "summarizer",
]

import os

# Import functions from utils.py for backward compatibility
# Use direct import to avoid circular import issues
import sys

_utils_path = os.path.join(os.path.dirname(__file__), "..", "utils.py")
if os.path.exists(_utils_path):
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location("utils_module", _utils_path)
        utils_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(utils_module)

        # Re-export the functions
        ensure_dir = utils_module.ensure_dir
        generate_id = utils_module.generate_id
        write_json = utils_module.write_json
        read_json = utils_module.read_json
        read_json_cached = utils_module.read_json_cached
        read_json_async = utils_module.read_json_async
        read_multiple_json = utils_module.read_multiple_json
        read_multiple_json_sync = utils_module.read_multiple_json_sync

        # Add to __all__
        __all__.extend(
            [
                "ensure_dir",
                "generate_id",
                "write_json",
                "read_json",
                "read_json_cached",
                "read_json_async",
                "read_multiple_json",
                "read_multiple_json_sync",
            ]
        )
    except (ImportError, AttributeError):
        # If utils.py is not available or has issues, continue without it
        pass
