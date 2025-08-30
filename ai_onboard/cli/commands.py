import argparse
import json
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
    prompt_bridge,
    vision_guardian,
    dynamic_planner,
    smart_debugger,
    context_continuity,
    vision_interrogator,
)
from ..plugins import example_policy  # ensure example plugin registers on import


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

    # Checkpoints (agent-aware snapshots)
    s_ck = sub.add_parser("checkpoint", help="Manage lightweight checkpoints")
    ck_sub = s_ck.add_subparsers(dest="ck_cmd", required=True)
    ck_create = ck_sub.add_parser("create", help="Create checkpoint for given scope globs")
    ck_create.add_argument("--scope", nargs="+", default=["."])
    ck_create.add_argument("--reason", default="")
    ck_sub.add_parser("list", help="List checkpoints")
    ck_restore = ck_sub.add_parser("restore", help="Restore by id")
    ck_restore.add_argument("--id", required=True)

    # Agent-facing prompt bridge (read-mostly, feature-flagged)
    s_prompt = sub.add_parser("prompt", help="Agent context APIs: state|rules|summary|propose")
    sp = s_prompt.add_subparsers(dest="prompt_cmd", required=True)
    sp.add_parser("state", help="Emit compact project state JSON")
    sp_rules = sp.add_parser("rules", help="Applicable meta-policy rules for a target path")
    sp_rules.add_argument("--path", default=".")
    sp_rules.add_argument("--change", default="", help="Optional change summary (free-text or JSON)")
    sp_summary = sp.add_parser("summary", help="Model-aware summary: brief|full")
    sp_summary.add_argument("--level", choices=["brief","full"], default="brief")
    sp_propose = sp.add_parser("propose", help="Propose action; returns decision and rationale")
    sp_propose.add_argument("--diff", default="", help="JSON {files_changed, lines_deleted, has_tests, subsystems}")

    # Vision and planning commands
    s_vision = sub.add_parser("vision", help="Vision alignment and scope management")
    sv_sub = s_vision.add_subparsers(dest="vision_cmd", required=True)
    sv_sub.add_parser("validate", help="Validate decision alignment with project vision")
    sv_sub.add_parser("scope-change", help="Propose scope change with user validation")
    sv_sub.add_parser("update", help="Update vision documents")

    # Dynamic planning commands
    s_planning = sub.add_parser("planning", help="Dynamic project planning")
    sp_sub = s_planning.add_subparsers(dest="planning_cmd", required=True)
    sp_sub.add_parser("milestone", help="Mark milestone complete")
    sp_sub.add_parser("progress", help="Update activity progress")
    sp_sub.add_parser("auto-update", help="Auto-update plan based on progress")
    sp_sub.add_parser("add-milestone", help="Add new milestone to plan")

    # Smart debugging commands
    s_debug = sub.add_parser("debug", help="Smart debugging system")
    sd_sub = s_debug.add_subparsers(dest="debug_cmd", required=True)
    sd_sub.add_parser("analyze", help="Analyze error and provide smart insights")
    sd_sub.add_parser("improve", help="Improve debugging patterns")
    sd_sub.add_parser("stats", help="Show debugging system statistics")

    # Context continuity commands
    s_context = sub.add_parser("context", help="Context continuity management")
    sc_sub = s_context.add_subparsers(dest="context_cmd", required=True)
    sc_sub.add_parser("summary", help="Get context summary")
    sc_sub.add_parser("drift", help="Check for context drift")
    sc_sub.add_parser("resolve", help="Resolve context drift")

    # Vision interrogation commands
    s_interrogate = sub.add_parser("interrogate", help="Vision interrogation system")
    si_sub = s_interrogate.add_subparsers(dest="interrogate_cmd", required=True)
    si_sub.add_parser("check", help="Check if vision is ready for AI agents")
    si_sub.add_parser("start", help="Start vision interrogation process")
    si_sub.add_parser("submit", help="Submit response to interrogation question")
    si_sub.add_parser("questions", help="Get current interrogation questions")
    si_sub.add_parser("summary", help="Get interrogation summary")
    si_sub.add_parser("force-complete", help="Force complete interrogation (use with caution)")

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

        # Clean, early handler for cleanup to avoid legacy garbled prints below
        if args.cmd == "cleanup":
            print("Scanning for files to clean up...")

            # Always start with dry-run to show what would be deleted
            result = cleanup.safe_cleanup(root, dry_run=True)

            print("\nScan Results:")
            print(f"  Protected (critical): {result['protected']} files")
            print(f"  Would delete: {result['would_delete']} files")
            print(f"  Unknown: {result['unknown']} files")

            if result['would_delete'] == 0:
                print("\nNo files to clean up!")
                return

            if args.dry_run:
                print("\nDRY RUN MODE - No files will be deleted")
                print("Files that would be deleted:")
                for path in result['scan_result']['non_critical'][:10]:  # Show first 10
                    print(f"  - {path.relative_to(root)}")
                if len(result['scan_result']['non_critical']) > 10:
                    print(f"  ... and {len(result['scan_result']['non_critical']) - 10} more")
                return

            # Real cleanup mode
            if not args.force:
                response = input(f"\nAre you sure you want to delete {result['would_delete']} files? (y/N): ")
                if response.lower() != 'y':
                    print("Cleanup cancelled.")
                    return

            # Create backup if requested
            if args.backup:
                print("Creating backup...")
                backup_dir = cleanup.create_backup(root)
                print(f"Backup created at: {backup_dir}")

            print("Performing cleanup...")
            result = cleanup.safe_cleanup(root, dry_run=False)

            print("\nCleanup completed!")
            print(f"  Deleted: {result['deleted_count']} files")
            if result['errors']:
                print(f"  Errors: {len(result['errors'])} files failed to delete")
                for error in result['errors'][:5]:
                    print(f"    - {error}")
            return

        if args.cmd == "checkpoint":
            manifest = utils.read_json(root / "ai_onboard.json", default={}) or {}
            ff = (manifest.get("features") or {})
            if ff.get("checkpoints", True) is False:
                print("{\"error\":\"checkpoints disabled\"}")
                return
            subcmd = getattr(args, "ck_cmd", None)
            from ..core import checkpoints
            if subcmd == "create":
                rec = checkpoints.create(root, scope=args.scope, reason=args.reason)
                print(prompt_bridge.dumps_json({"created": rec}))
                return
            if subcmd == "list":
                items = checkpoints.list(root)
                print(prompt_bridge.dumps_json({"items": items}))
                return
            if subcmd == "restore":
                res = checkpoints.restore(root, ckpt_id=args.id)
                print(prompt_bridge.dumps_json(res))
                return
            print("{\"error\":\"unknown checkpoint subcommand\"}")
            return

        if args.cmd == "prompt":
            manifest = utils.read_json(root / "ai_onboard.json", default={}) or {}
            ff = (manifest.get("features") or {})
            if ff.get("prompt_bridge", True) is False:
                print("{\"error\":\"prompt_bridge disabled\"}")
                return
            pcmd = getattr(args, "prompt_cmd", None)
            if pcmd == "state":
                out = prompt_bridge.get_project_state(root)
                print(prompt_bridge.dumps_json(out))
                return
            if pcmd == "rules":
                out = prompt_bridge.get_applicable_rules(root, target_path=args.path, change_summary=args.change)
                print(prompt_bridge.dumps_json(out))
                return
            if pcmd == "summary":
                out = prompt_bridge.summary(root, level=args.level)
                print(prompt_bridge.dumps_json(out))
                return
            if pcmd == "propose":
                out = prompt_bridge.propose_action(root, diff_json=args.diff)
                print(prompt_bridge.dumps_json(out))
                return
            print("{\"error\":\"unknown prompt subcommand\"}")
            return

        # Vision alignment commands
        if args.cmd == "vision":
            vcmd = getattr(args, "vision_cmd", None)
            if vcmd == "validate":
                # Validate decision alignment
                decision_data = input("Enter decision data (JSON): ")
                try:
                    decision = json.loads(decision_data)
                    guardian = vision_guardian.get_vision_guardian(root)
                    result = guardian.validate_decision_alignment(decision)
                    print(prompt_bridge.dumps_json(result))
                except json.JSONDecodeError:
                    print("{\"error\":\"invalid JSON\"}")
                return
            elif vcmd == "scope-change":
                # Propose scope change
                change_data = input("Enter scope change request (JSON): ")
                try:
                    change_request = json.loads(change_data)
                    guardian = vision_guardian.get_vision_guardian(root)
                    result = guardian.propose_scope_change(change_request)
                    print(prompt_bridge.dumps_json(result))
                except json.JSONDecodeError:
                    print("{\"error\":\"invalid JSON\"}")
                return
            elif vcmd == "update":
                # Update vision documents
                updates_data = input("Enter vision updates (JSON): ")
                try:
                    updates = json.loads(updates_data)
                    guardian = vision_guardian.get_vision_guardian(root)
                    result = guardian.update_vision_documents(updates)
                    print(prompt_bridge.dumps_json(result))
                except json.JSONDecodeError:
                    print("{\"error\":\"invalid JSON\"}")
                return
            print("{\"error\":\"unknown vision subcommand\"}")
            return

        # Dynamic planning commands
        if args.cmd == "planning":
            pcmd = getattr(args, "planning_cmd", None)
            planner = dynamic_planner.get_dynamic_planner(root)
            
            if pcmd == "milestone":
                # Mark milestone complete
                milestone_name = input("Enter milestone name: ")
                completion_data = input("Enter completion data (JSON): ")
                try:
                    completion = json.loads(completion_data) if completion_data else {}
                    result = planner.mark_milestone_complete(milestone_name, completion)
                    print(prompt_bridge.dumps_json(result))
                except json.JSONDecodeError:
                    print("{\"error\":\"invalid JSON\"}")
                return
            elif pcmd == "progress":
                # Update activity progress
                activity_id = input("Enter activity ID: ")
                progress_data = input("Enter progress data (JSON): ")
                try:
                    progress = json.loads(progress_data)
                    result = planner.update_activity_progress(activity_id, progress)
                    print(prompt_bridge.dumps_json(result))
                except json.JSONDecodeError:
                    print("{\"error\":\"invalid JSON\"}")
                return
            elif pcmd == "auto-update":
                # Auto-update plan
                result = planner.auto_update_plan()
                print(prompt_bridge.dumps_json(result))
                return
            elif pcmd == "add-milestone":
                # Add new milestone
                milestone_data = input("Enter milestone data (JSON): ")
                try:
                    milestone = json.loads(milestone_data)
                    result = planner.add_new_milestone(milestone)
                    print(prompt_bridge.dumps_json(result))
                except json.JSONDecodeError:
                    print("{\"error\":\"invalid JSON\"}")
                return
            print("{\"error\":\"unknown planning subcommand\"}")
            return

        # Smart debugging commands
        if args.cmd == "debug":
            dcmd = getattr(args, "debug_cmd", None)
            debugger = smart_debugger.get_smart_debugger(root)
            
            if dcmd == "analyze":
                # Analyze error
                error_data = input("Enter error data (JSON): ")
                try:
                    error = json.loads(error_data)
                    result = debugger.analyze_error(error)
                    print(prompt_bridge.dumps_json(result))
                except json.JSONDecodeError:
                    print("{\"error\":\"invalid JSON\"}")
                return
            elif dcmd == "improve":
                # Improve patterns
                result = debugger.improve_patterns()
                print(prompt_bridge.dumps_json(result))
                return
            elif dcmd == "stats":
                # Show statistics
                result = debugger.get_debugging_stats()
                print(prompt_bridge.dumps_json(result))
                return
            print("{\"error\":\"unknown debug subcommand\"}")
            return

        # Context continuity commands
        if args.cmd == "context":
            ccmd = getattr(args, "context_cmd", None)
            context_manager = context_continuity.get_context_continuity_manager(root)
            
            if ccmd == "summary":
                # Get context summary
                level = input("Enter summary level (brief/full): ").strip() or "brief"
                result = context_manager.get_context_summary(level)
                print(prompt_bridge.dumps_json(result))
                return
            elif ccmd == "drift":
                # Check for drift
                result = context_manager.check_context_drift()
                print(prompt_bridge.dumps_json(result))
                return
            elif ccmd == "resolve":
                # Resolve drift
                drift_type = input("Enter drift type: ")
                resolution_data = input("Enter resolution data (JSON): ")
                try:
                    resolution = json.loads(resolution_data) if resolution_data else {}
                    result = context_manager.resolve_context_drift(drift_type, resolution)
                    print(prompt_bridge.dumps_json(result))
                except json.JSONDecodeError:
                    print("{\"error\":\"invalid JSON\"}")
                return
            print("{\"error\":\"unknown context subcommand\"}")
            return

        # Vision interrogation commands
        if args.cmd == "interrogate":
            icmd = getattr(args, "interrogate_cmd", None)
            interrogator = vision_interrogator.get_vision_interrogator(root)
            
            if icmd == "check":
                # Check vision readiness
                result = interrogator.check_vision_readiness()
                print(prompt_bridge.dumps_json(result))
                return
            elif icmd == "start":
                # Start interrogation
                result = interrogator.start_interrogation()
                print(prompt_bridge.dumps_json(result))
                return
            elif icmd == "submit":
                # Submit response
                phase = input("Enter phase: ")
                question_id = input("Enter question ID: ")
                response_data = input("Enter response (JSON): ")
                try:
                    response = json.loads(response_data)
                    result = interrogator.submit_response(phase, question_id, response)
                    print(prompt_bridge.dumps_json(result))
                except json.JSONDecodeError:
                    print("{\"error\":\"invalid JSON\"}")
                return
            elif icmd == "questions":
                # Get current questions
                result = interrogator.get_current_questions()
                print(prompt_bridge.dumps_json(result))
                return
            elif icmd == "summary":
                # Get interrogation summary
                result = interrogator.get_interrogation_summary()
                print(prompt_bridge.dumps_json(result))
                return
            elif icmd == "force-complete":
                # Force complete interrogation
                result = interrogator.force_complete_interrogation()
                print(prompt_bridge.dumps_json(result))
                return
            print("{\"error\":\"unknown interrogate subcommand\"}")
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
    except Exception as e:
        # Catch-all to avoid stack traces surfacing to users for known flows
        print(e)
        return
