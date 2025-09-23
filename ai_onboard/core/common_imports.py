"""Consolidated common imports for the codebase.

This module exposes commonly used standard-library symbols so callers can:

    #
        Path, Dict, List, Optional, Any, Union, Callable, Set, Iterable, Tuple,
        dataclass, field, deque, contextmanager, datetime, timedelta, Enum,
        json, os, sys,
    )
"""

import json
import os
import sys
from collections import deque
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Set, Tuple, Union

__all__ = [
    # pathlib / typing
    "Path",
    "Any",
    "Dict",
    "List",
    "Optional",
    "Union",
    "Callable",
    "Set",
    "Iterable",
    "Tuple",
    # dataclasses / collections / contextlib / datetime / enum
    "dataclass",
    "field",
    "deque",
    "contextmanager",
    "datetime",
    "timedelta",
    "Enum",
    # stdlib modules
    "json",
    "os",
    "sys",
]
