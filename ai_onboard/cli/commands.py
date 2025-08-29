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
    cleanup,
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

    sub.add_parser("metrics", help="Show last validation run summary from telemetry")

    s_clean = sub.add_parser("cleanup", help="Safely remove non-critical files (build artifacts, cache, etc.)")
    s_clean.add_argument("--dry-run", action="store_true", help="Show what would be deleted without actually deleting")
    s_clean.add_argument("--force", action="store_true", help="Skip confirmation prompts")
    s_clean.add_argument("--backup", action="store_true", help="Create backup before cleanup")

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

        if args.cmd == "metrics":
            last = telemetry.last_run(root)
            if not last:
                print("No telemetry yet. Run: python -m ai_onboard validate --report")
                return
            comps = last.get("components", [])
            comp_lines = [
                f"- {c.get('name','?')}: score={c.get('score','n/a')} issues={c.get('issue_count',0)}"
                for c in comps
            ]
            print("Last validation run:")
            print(f"- ts: {last.get('ts')}")
            print(f"- pass: {last.get('pass')}")
            print("- components:")
            for line in comp_lines:
                print(line)
            return

        if args.cmd == "cleanup":
            print("🔍 Scanning for files to clean up...")
            
            # Always start with dry-run to show what would be deleted
            result = cleanup.safe_cleanup(root, dry_run=True)
            
            print(f"\n📊 Scan Results:")
            print(f"  🛡️  Protected (critical): {result['protected']} files")
            print(f"  🗑️  Would delete: {result['would_delete']} files")
            print(f"  ❓ Unknown: {result['unknown']} files")
            
            if result['would_delete'] == 0:
                print("\n✨ No files to clean up!")
                return
            
            if args.dry_run:
                print("\n🔍 DRY RUN MODE - No files will be deleted")
                print("Files that would be deleted:")
                for path in result['scan_result']['non_critical'][:10]:  # Show first 10
                    print(f"  - {path.relative_to(root)}")
                if len(result['scan_result']['non_critical']) > 10:
                    print(f"  ... and {len(result['scan_result']['non_critical']) - 10} more")
                return
            
            # Real cleanup mode
            if not args.force:
                response = input(f"\n⚠️  Are you sure you want to delete {result['would_delete']} files? (y/N): ")
                if response.lower() != 'y':
                    print("❌ Cleanup cancelled.")
                    return
            
            # Create backup if requested
            if args.backup:
                print("💾 Creating backup...")
                backup_dir = cleanup.create_backup(root)
                print(f"✅ Backup created at: {backup_dir}")
            
            print("🧹 Performing cleanup...")
            result = cleanup.safe_cleanup(root, dry_run=False)
            
            print(f"\n✅ Cleanup completed!")
            print(f"  🗑️  Deleted: {result['deleted_count']} files")
            if result['errors']:
                print(f"  ⚠️  Errors: {len(result['errors'])} files failed to delete")
                for error in result['errors'][:5]:
                    print(f"    - {error}")
            return
    except state.StateError as e:
        print(e)
        return
