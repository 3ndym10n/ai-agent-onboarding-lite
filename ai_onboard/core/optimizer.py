import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from . import telemetry, utils


def parse_budget(s: str) -> int:
    s = s.strip().lower()
    if s.endswith("m"):
        return int(s[:-1]) * 60
    if s.endswith("s"):
        return int(s[:-1])
    return int(s)


def quick_optimize(root: Path, budget: str = "300s") -> None:
    trials = root / ".ai_onboard" / "optimizer_trials.jsonl"
    utils.ensure_dir(trials.parent)
    with open(trials, "a", encoding="utf - 8") as f:
        f.write(
            f'{{"ts":"{utils.now_iso()}","trial":"ordering / parallel","budget_s":{parse_budget(budget)},"result":"stub"}}\n'
        )
    print("Optimizer ran a quick (stub) trial. (Hooks are ready for deeper logic.)")


def nudge_from_metrics(root: Path) -> None:
    # Read metrics and nudge parameters (lightweight summary for now)
    items = telemetry.read_metrics(root)
    if not items:
        print("Kaizen: no telemetry yet. Run 'validate' to collect metrics.")
        return
    last = items[-1]
    comps = ", ".join(
        [
            f"{c.get('name', '?')}:{c.get('score', 'n / a')}"
            for c in last.get("components", [])
        ]
    )
    print(f"Kaizen: last run pass={last.get('pass')} | components: {comps}")


# ===== Optimization Strategist MVP: proposal generation =====


def _find_latest_test_report(root: Path) -> Optional[Path]:
    reports_dir = root / ".ai_onboard" / "test_reports"
    if not reports_dir.exists():
        return None
    candidates = [p for p in reports_dir.glob("*.json") if p.is_file()]
    if not candidates:
        return None
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def _load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        with open(path, "r", encoding="utf - 8") as f:
            return json.load(f)
    except Exception:
        return None


def _extract_hotspots(report: Dict[str, Any]) -> List[Tuple[str, float]]:
    """Return list of (name, seconds) sorted by descending time.

    Tries multiple shapes defensively.
    """
    hotspots: List[Tuple[str, float]] = []
    # Shape 1: metrics -> test_results: [{name, execution_time_s}]
    results = (
        (report.get("metrics") or {}).get("test_results")
        if isinstance(report, dict)
        else None
    )
    if isinstance(results, list):
        for item in results:
            name = str(item.get("name", "unknown"))
            secs = float(
                item.get("execution_time_s", item.get("execution_time", 0.0)) or 0.0
            )
            hotspots.append((name, secs))

    # Shape 2: direct list under detailed_metrics
    if not hotspots:
        dm = report.get("detailed_metrics") if isinstance(report, dict) else None
        if isinstance(dm, list):
            for item in dm:
                name = str(item.get("name", "unknown"))
                secs = float(
                    item.get("execution_time_s", item.get("execution_time", 0.0)) or 0.0
                )
                hotspots.append((name, secs))

    hotspots.sort(key=lambda x: x[1], reverse=True)
    return hotspots


def _ensure_prefs(root: Path, prefs: Dict[str, Any]) -> Path:
    prefs_path = root / ".ai_onboard" / "optimization_prefs.json"
    utils.ensure_dir(prefs_path.parent)
    try:
        if not prefs_path.exists():
            with open(prefs_path, "w", encoding="utf - 8") as f:
                json.dump(prefs, f, indent=2)
        else:
            # Merge - lite: keep existing keys, update with new ones
            existing = _load_json(prefs_path) or {}
            existing.update(prefs)
            with open(prefs_path, "w", encoding="utf - 8") as f:
                json.dump(existing, f, indent=2)
    except Exception:
        pass
    return prefs_path


def _analyze_hotspot_patterns(
    hotspots: List[Tuple[str, float]],
) -> List[Dict[str, Any]]:
    """Analyze hotspot patterns to recommend optimization strategies."""
    patterns = []

    for func_name, exec_time in hotspots:
        # CPU - bound patterns
        if any(
            keyword in func_name.lower()
            for keyword in ["loop", "calculate", "compute", "process", "math"]
        ):
            patterns.append(
                {
                    "type": "cpu_bound",
                    "function": func_name,
                    "time": exec_time,
                    "recommendations": ["cpu_bound"],
                }
            )

        # Memory - bound patterns
        elif any(
            keyword in func_name.lower()
            for keyword in ["dict", "list", "object", "memory", "cache"]
        ):
            patterns.append(
                {
                    "type": "memory_bound",
                    "function": func_name,
                    "time": exec_time,
                    "recommendations": ["memory_bound"],
                }
            )

        # I / O - bound patterns
        elif any(
            keyword in func_name.lower()
            for keyword in ["read", "write", "file", "network", "db", "open"]
        ):
            patterns.append(
                {
                    "type": "io_bound",
                    "function": func_name,
                    "time": exec_time,
                    "recommendations": ["io_bound"],
                }
            )

        # Algorithm patterns
        elif any(
            keyword in func_name.lower()
            for keyword in ["search", "sort", "filter", "find", "lookup"]
        ):
            patterns.append(
                {
                    "type": "algorithm",
                    "function": func_name,
                    "time": exec_time,
                    "recommendations": ["algorithm"],
                }
            )

        # Default to creative techniques if no pattern matches
        else:
            patterns.append(
                {
                    "type": "general",
                    "function": func_name,
                    "time": exec_time,
                    "recommendations": ["creative"],
                }
            )

    return patterns


def generate_optimization_proposals(
    root: Path, budget_seconds: int, preferences: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create grounded optimization proposals based on latest evidence.

    Returns a dict: { proposals: [...], evidence_summary: {...} }
    """
    prefs = preferences or {
        "risk_mode": "balanced_creative",
        "allowed_tech": [
            "Numba",
            "Cython",
            "Rust / WASM",
            "PyPy",
            "asyncio",
            "C",
            "C++",
            "C#",
            "NumPy",
            "Pandas",
            "Joblib",
            "NumExpr",
            "Dask",
            "Ray",
            "CuPy",
            "aiofiles",
            "concurrent.futures",
            "multiprocessing",
            "weakref",
        ],
        "experiment_budget_default_minutes": max(1, budget_seconds // 60) or 10,
        "optimization_categories": {
            "cpu_bound": ["numba_jit", "vectorize_numpy", "cython_compile", "pypy_jit"],
            "memory_bound": [
                "weakref_cache",
                "object_pool",
                "memoryview",
                "slots_optimization",
            ],
            "io_bound": ["async_io", "concurrent_futures", "aiofiles", "mmap_files"],
            "algorithm": [
                "bisect_search",
                "heapq_priority",
                "set_lookup",
                "dict_comprehension",
            ],
            "creative": [
                "rust_microkernel",
                "c_extension",
                "numexpr_eval",
                "joblib_parallel",
            ],
        },
    }
    _ensure_prefs(root, prefs)

    report_path = _find_latest_test_report(root)
    report = _load_json(report_path) if report_path else None
    hotspots = _extract_hotspots(report) if report else []

    proposals: List[Dict[str, Any]] = []

    # Analyze hotspot patterns for targeted recommendations
    hotspot_patterns = _analyze_hotspot_patterns(hotspots)

    # Heuristic: if we have hotspots, target top 1-3 with pattern-matched optimizations
    for name, secs in hotspots[:3]:
        # Get pattern recommendations for this specific hotspot
        pattern_recs = []
        for pattern in hotspot_patterns:
            if pattern["function"] == name:
                pattern_recs = pattern["recommendations"]
                break

        # Enhanced idea bank with more sophisticated optimizations
        idea_bank: List[Tuple[str, str, str, str]] = [
            # CPU-bound optimizations
            (
                "numba_jit",
                "Numba JIT hot loops",
                "Apply @njit/@jit to CPU - bound sections and avoid Python overhead",
                "cpu_bound",
            ),
            (
                "vectorize_numpy",
                "NumPy vectorization",
                "Replace Python loops with NumPy vector ops for 10-100x speedup",
                "cpu_bound",
            ),
            (
                "cython_compile",
                "Cython compilation",
                "Compile performance - critical sections to C extensions",
                "cpu_bound",
            ),
            (
                "pypy_jit",
                "PyPy JIT compilation",
                "Use PyPy's tracing JIT for automatic optimization",
                "cpu_bound",
            ),
            # Memory optimizations
            (
                "weakref_cache",
                "Weak reference caching",
                "Use weakref for memory-efficient caching without leaks",
                "memory_bound",
            ),
            (
                "object_pool",
                "Object pooling",
                "Reuse objects to reduce GC pressure and allocation overhead",
                "memory_bound",
            ),
            (
                "memoryview",
                "Memory views",
                "Use memoryview for zero-copy buffer access",
                "memory_bound",
            ),
            (
                "slots_optimization",
                "Slots optimization",
                "Use __slots__ to reduce memory footprint",
                "memory_bound",
            ),
            # I/O optimizations
            (
                "async_io",
                "Async I/O refactoring",
                "Convert blocking I/O to async/await patterns",
                "io_bound",
            ),
            (
                "concurrent_futures",
                "Thread pool execution",
                "Use concurrent.futures for parallel I/O operations",
                "io_bound",
            ),
            (
                "aiofiles",
                "Async file operations",
                "Replace sync file ops with aiofiles for non-blocking I/O",
                "io_bound",
            ),
            (
                "mmap_files",
                "Memory - mapped files",
                "Use mmap for efficient large file access",
                "io_bound",
            ),
            # Algorithm optimizations
            (
                "bisect_search",
                "Binary search optimization",
                "Replace linear searches with bisect for O(log n) lookup",
                "algorithm",
            ),
            (
                "heapq_priority",
                "Priority queue optimization",
                "Use heapq for efficient priority - based operations",
                "algorithm",
            ),
            (
                "set_lookup",
                "Set - based lookups",
                "Replace list membership tests with set lookups",
                "algorithm",
            ),
            (
                "dict_comprehension",
                "Dict comprehensions",
                "Use dict comprehensions for memory - efficient dict building",
                "algorithm",
            ),
            # Creative techniques
            (
                "rust_microkernel",
                "Rust / WASM micro - kernel",
                "Move tight numeric loop to Rust compiled to native / WASM and \
                    call via FFI",
                "creative",
            ),
            (
                "c_extension",
                "C extension modules",
                "Write performance - critical code in C with Python bindings",
                "creative",
            ),
            (
                "numexpr_eval",
                "NumExpr evaluation",
                "Use numexpr for efficient numerical expression evaluation",
                "creative",
            ),
            (
                "joblib_parallel",
                "Joblib parallelization",
                "Parallelize independent computations with joblib",
                "creative",
            ),
        ]

        # Filter ideas based on pattern recommendations or use all if no patterns
        relevant_ideas = []
        if pattern_recs:
            relevant_ideas = [idea for idea in idea_bank if idea[3] in pattern_recs]
        else:
            relevant_ideas = idea_bank

        # Limit to top 4 ideas per hotspot to avoid overwhelming
        for pid, title, desc, category in relevant_ideas[:4]:
            proposals.append(
                {
                    "id": f"{pid}:{name}",
                    "target": name,
                    "title": title,
                    "description": desc,
                    "evidence": {
                        "source": str(report_path) if report_path else "n / a",
                        "hotspot_seconds": secs,
                        "hotspot_rank": next(
                            (i for i, h in enumerate(hotspots, 1) if h[0] == name), 1
                        ),
                    },
                    "estimated_gain": "10 - 50%",
                    "risk": (
                        "balanced"
                        if pid in ("numba_jit", "vectorize_numpy", "asyncio_refactor")
                        else "creative"
                    ),
                    "tech": pid,
                    "branch_required": pid in ("rust_microkernel",),
                    "confidence": (
                        0.55 if pid in ("numba_jit", "vectorize_numpy") else 0.4
                    ),
                }
            )

    # Fallback if no hotspots / evidence
    if not proposals:
        proposals.append(
            {
                "id": "profiling_baseline",
                "target": "system",
                "title": "Capture profiling baseline",
                "description": "Run cProfile / py - spy to gather flame graphs and \
                    identify real hotspots",
                "evidence": {"reason": "No recent test report with timings found"},
                "estimated_gain": "TBD",
                "risk": "low",
                "tech": "profiling",
                "branch_required": False,
                "confidence": 0.7,
            }
        )

    return {
        "proposals": proposals,
        "evidence_summary": {
            "report_used": str(report_path) if report_path else None,
            "hotspot_count": len(hotspots),
            "budget_seconds": budget_seconds,
            "preferences": prefs,
        },
    }


def create_sandbox_plan(
    root: Path,
    proposal_id: Optional[str],
    budget_seconds: int,
) -> Dict[str, Any]:
    """Produce a sandbox execution plan for a given proposal (or top proposal).

    The plan is descriptive only (no side effects). Branching is recommended for
    high - risk items. Returns a dict with selected proposal and step plan.
    """
    proposals_bundle = generate_optimization_proposals(root, budget_seconds)
    proposals = proposals_bundle.get("proposals", [])
    if not proposals:
        return {
            "error": "no_proposals",
            "message": "No optimization proposals available. Run tests to generate evidence.",
        }

    selected = None
    if proposal_id:
        for p in proposals:
            if p.get("id") == proposal_id:
                selected = p
                break
    if selected is None:
        selected = proposals[0]

    branch_name = f"opt/{selected.get('tech', 'idea')}-{selected.get('target', 'unknown').replace(' ', '_')[:32]}"
    steps: List[str] = [
        f"Create branch {branch_name}",
        "Add micro - benchmark around target function / path",
        "Implement minimal change scoped to idea",
        "Run unit / system tests",
        "Run micro - bench and compare to baseline",
        "Generate report (gains, regressions, diff scope)",
    ]
    if selected.get("risk") == "high":
        steps.insert(0, "Gate approval required before branching (high risk)")

    return {
        "selected_proposal": selected,
        "branch": branch_name,
        "steps": steps,
        "budget_seconds": budget_seconds,
        "evidence": proposals_bundle.get("evidence_summary", {}),
    }
