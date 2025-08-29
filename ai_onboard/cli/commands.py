import argparse
from pathlib import Path
from ..core import (
    charter,
    planning,
    discovery,
    alignment,
    state,
    utils,
    validation_runtime,
    progress_tracker,
    telemetry,
    optimizer,
    versioning,
)


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="ai_onboard",
        description=(
            "AI Onboard: drop-in project coach "
            "(charter + plan + align + validate + kaizen)"
        ),
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    s_an = sub.add_parser("analyze", help="Scan repo and draft ai_onboard.json manifest")
    s_an.add_argument("--allowExec", action="store_true", help="Permit safe external probes (off by default)")

    s_ch = sub.add_parser("charter", help="Create or update project charter")
    s_ch.add_argument("--interactive", action="store_true")

    sub.add_parser("plan", help="Build plan.json from charter")

    s_al = sub.add_parser("align", help="Open or approve an alignment checkpoint")
    s_al.add_argument("--checkpoint", default="PlanGate")
    s_al.add_argument("--approve", action="store_true")
    s_al.add_argument("--note", default="", help="Optional note to store with approval")

    s_v = sub.add_parser("validate", help="Run validation and write report")
    s_v.add_argument("--report", action="store_true", help="Write .ai_onboard/report.md and versioned copy")

    s_k = sub.add_parser("kaizen", help="Run a kaizen cycle (metrics-driven nudges)")
    s_k.add_argument("--once", action="store_true")

    s_o = sub.add_parser("optimize", help="Run quick optimization experiments")
    s_o.add_argument("--budget", default="5m", help="Time budget (e.g., 5m)")

    s_ver = sub.add_parser("version", help="Show or bump ai_onboard version")
    s_ver.add_argument("--bump", choices=["major", "minor", "patch"])
    s_ver.add_argument("--set", help="Set explicit version (e.g., 1.2.3)")

    args = p.parse_args(argv)
    root = Path.cwd()
    st = state.load(root)

    try:
        if args.cmd == "analyze":
            manifest = discovery.run(root, allow_exec=args.allowExec)
            utils.write_json(root / "ai_onboard.json", manifest)
            print("Wrote ai_onboard.json (draft).")
            return

        if args.cmd == "charter":
            charter.ensure(root, interactive=args.interactive)
            state.advance(root, st, "chartered")
            print("Charter ready at .ai_onboard/charter.json")
            return

        if args.cmd == "plan":
            charter.require_gate(root, "chartered")
            planning.build(root)
            state.advance(root, st, "planned")
            print("Plan ready at .ai_onboard/plan.json")
            return

        if args.cmd == "align":
            cp = args.checkpoint
            if args.approve:
                alignment.record_decision(root, "ALIGN", cp, True, args.note)
                state.advance(root, st, "aligned")
                print(f"Alignment approved for {cp}.")
            else:
                alignment.open_checkpoint(root, cp)
                print(f"Opened alignment checkpoint {cp}.")
            return

        if args.cmd == "validate":
            alignment.require_state(root, "aligned")
            res = validation_runtime.run(root)
            if args.report:
                progress_tracker.write_report(root, res)
                print("Wrote .ai_onboard/report.md (+ versioned copy).")
            telemetry.record_run(root, res)
            return

        if args.cmd == "kaizen":
            print("Kaizen: ingesting telemetry and nudging schedules/bounds (lightweight).")
            optimizer.nudge_from_metrics(root)
            return

        if args.cmd == "optimize":
            optimizer.quick_optimize(root, args.budget)
            return

        if args.cmd == "version":
            if args.set:
                versioning.set_version(root, args.set)
                print(f"Version set to {args.set}")
                return
            if args.bump:
                current = versioning.get_version(root)
                newv = versioning.bump(current, args.bump)
                versioning.set_version(root, newv)
                print(f"Bumped {args.bump}: {current} -> {newv}")
                return
            print(versioning.get_version(root))
            return
    except state.StateError as e:
        print(e)
        return

