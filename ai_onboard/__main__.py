from .cli.commands_refactored import main
from .core.universal_error_monitor import setup_global_error_handler
from pathlib import Path

if __name__ == "__main__":
    # Set up global error monitoring
    setup_global_error_handler(Path.cwd())
    main()
