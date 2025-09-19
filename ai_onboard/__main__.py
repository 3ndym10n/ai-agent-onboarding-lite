from pathlib import Path

from .cli.commands_intelligent_monitoring import (
    initialize_intelligent_monitoring,
    shutdown_intelligent_monitoring,
)
from .cli.commands_refactored import main
from .core.universal_error_monitor import setup_global_error_handler

if __name__ == "__main__":
    # Set up global error monitoring
    setup_global_error_handler(Path.cwd())

    # Initialize intelligent development monitoring
    root_path = Path.cwd()
    initialize_intelligent_monitoring(root_path)

    try:
        main()
    finally:
        # Ensure intelligent monitoring is properly shutdown
        shutdown_intelligent_monitoring()
