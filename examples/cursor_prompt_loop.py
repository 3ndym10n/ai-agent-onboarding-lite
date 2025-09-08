#!/usr/bin/env python3
"""
Minimal prompt-only session driver for the Cursor Rule System.

Usage:
  python examples/cursor_prompt_loop.py --print-prompt
  python examples/cursor_prompt_loop.py --observe "Found README with goals X,Y" --rule readme
  python examples/cursor_prompt_loop.py --decide allow --why "docs are sufficient to proceed"
  python examples/cursor_prompt_loop.py --status
"""

import argparse
from pathlib import Path
import sys

# Ensure local ai_onboard is preferred over any installed package
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ai_onboard.core import cursor_rules


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--print-prompt", action="store_true")
    p.add_argument("--status", action="store_true")
    p.add_argument("--observe", help="Free-form observation text")
    p.add_argument("--rule", help="Rule/checklist id for observation")
    p.add_argument("--decide", help="Decision label (allow/deny/clarify/quick_confirm/custom)")
    p.add_argument("--why", help="Decision rationale")
    p.add_argument("--root", help="Target project root (defaults to CWD)")
    args = p.parse_args()

    root = Path(args.root).resolve() if args.root else Path.cwd()

    if args.print_prompt:
        print(cursor_rules.generate_system_prompt(root))
        return

    if args.status:
        from ai_onboard.core import prompt_bridge
        s = cursor_rules.status(root)
        s["project_state"] = prompt_bridge.get_project_state(root)
        import json
        print(json.dumps(s, indent=2))
        return

    if args.observe:
        rule_id = args.rule or "general"
        rec = cursor_rules.record_observation(root, rule_id, args.observe)
        import json
        print(json.dumps(rec, indent=2))
        return

    if args.decide:
        rec = cursor_rules.record_decision(root, args.decide, args.why or "")
        import json
        print(json.dumps(rec, indent=2))
        return

    # Default: show checklist
    import json
    print(json.dumps({"checklist": cursor_rules.next_checklist(root)}, indent=2))


if __name__ == "__main__":
    main()


