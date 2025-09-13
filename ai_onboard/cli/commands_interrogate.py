"""Interrogate commands for ai - onboard CLI."""

import json
import os
from pathlib import Path

from ..core import prompt_bridge, vision_interrogator
from ..core.gate_system import GateRequest, GateSystem, GateType
from ..core.lean_approval import request_approval


def add_interrogate_commands(subparsers):
    """Add interrogate command parsers."""

    s_interrogate = subparsers.add_parser(
        "interrogate", help="Vision interrogation system"
    )
    si_sub = s_interrogate.add_subparsers(dest="interrogate_cmd", required = True)

    si_sub.add_parser("check", help="Check if vision is ready for AI agents")
    si_sub.add_parser("start", help="Start vision interrogation process")

    submit_parser = si_sub.add_parser(
        "submit", help="Submit response to interrogation question"
    )
    submit_parser.add_argument("--phase", help="Interrogation phase")
    submit_parser.add_argument("--question - id", help="Question ID")
    submit_parser.add_argument("--response", help="Response data (JSON)")

    si_sub.add_parser("questions", help="Get current interrogation questions")
    si_sub.add_parser("summary", help="Get interrogation summary")
    si_sub.add_parser(
        "force - complete", help="Force complete interrogation (use with caution)"
    )
    si_sub.add_parser(
        "complete - from - charter",
        help="Mark interrogation complete using existing charter.json (non - interactive)",
    )


def handle_interrogate_commands(args, root: Path):
    """Handle interrogate command execution."""

    if args.cmd != "interrogate":
        return False

    icmd = getattr(args, "interrogate_cmd", None)
    if not icmd:
        print('{"error":"no interrogate subcommand specified"}')
        return True

    # Initialize interrogator
    interrogator = vision_interrogator.VisionInterrogator(root)

    if icmd == "check":
        # Check if vision is ready
        result = interrogator.check_vision_readiness()
        print(prompt_bridge.dumps_json(result))
        return True
    elif icmd == "start":
        # Start interrogation and immediately open a gate to collect answers from the human
        result = interrogator.start_interrogation()
        # Try to fetch questions for the gate prompt
        try:
            qres = interrogator.get_current_questions()
            questions = []
            for q in qres.get("questions", []):
                qt = q.get("text") or q.get("question")
                if qt:
                    questions.append(qt)
        except Exception:
            questions = []

        if questions:
            # Lean approve server (one - click). Stronger guarantee than chat gates.
            resp = request_approval(
                title="Vision Interrogation - Provide Your Answers",
                description="Answer the questions below, then click Approve to submit.",
                questions = questions,
                timeout_seconds = 600,
            )
            if resp.get("user_decision") == "proceed":
                try:
                    qres = interrogator.get_current_questions()
                    qlist = qres.get("questions", [])
                    answers = resp.get("user_responses", [])
                    for i, q in enumerate(qlist):
                        if i < len(answers):
                            payload = {"answer": answers[i]}
                            interrogator.submit_response(
                                q.get("phase") or "vision_core", q.get("id"), payload
                            )
                except Exception:
                    pass
        print(prompt_bridge.dumps_json(result))
        return True
    elif icmd == "submit":
        # Submit response (gate - enforced)
        phase = getattr(args, "phase", None)
        question_id = getattr(args, "question_id", None)
        provided_response = getattr(args, "response", None)

        if not all([phase, question_id]):
            print(
                '{"error":"missing required arguments: phase and question - id are required"}'
            )
            return True

        # CI - only bypass maintains previous behavior
        if (
            os.getenv("GITHUB_ACTIONS", "").lower() == "true"
            and os.getenv("AI_ONBOARD_BYPASS", "") == "ci"
            and provided_response
        ):
            try:
                try:
                    response = json.loads(provided_response)
                except json.JSONDecodeError:
                    response = {"answer": provided_response}
                result = interrogator.submit_response(phase, question_id, response)
                print(prompt_bridge.dumps_json(result))
            except Exception as e:
                print(f'{{"error":"failed to submit response: {str(e)}"}}')
            return True

        # Gate - enforced path: always ask the human in chat to answer
        # Find the question text for better UX
        question_text = None
        try:
            qres = interrogator.get_current_questions()
            for q in qres.get("questions", []):
                if q.get("id") == question_id or str(q.get("id")) == str(question_id):
                    question_text = q.get("text") or q.get("question")
                    break
        except Exception:
            pass
        if not question_text:
            question_text = "Please provide your answer to the interrogation question."

        gate = GateSystem(root)
        gate_request = GateRequest(
            gate_type = GateType.CLARIFICATION_NEEDED,
            title="Vision Interrogation",
            description = f"Phase: {phase} | Question ID: {question_id}",
            context={"phase": phase, "question_id": question_id},
            questions=[question_text],
        )
        response = gate.create_gate(gate_request)
        if response.get("user_decision") != "proceed":
            print('{"error":"interrogation halted by user (or timeout)"}')
            return True

        # Convert user response(s) to expected payload
        user_answers = response.get("user_responses", [])
        answer_text = user_answers[0] if user_answers else ""
        payload = {"answer": answer_text}

        try:
            result = interrogator.submit_response(phase, question_id, payload)
            print(prompt_bridge.dumps_json(result))
        except Exception as e:
            print(f'{{"error":"failed to submit response: {str(e)}"}}')
        return True
    elif icmd == "questions":
        # Get current questions and open a gate to collect answers
        result = interrogator.get_current_questions()
        print(prompt_bridge.dumps_json(result))
        try:
            questions = []
            for q in result.get("questions", []):
                qt = q.get("text") or q.get("question")
                if qt:
                    questions.append(qt)
            if questions:
                request_approval(
                    title="Vision Interrogation - Provide Your Answers",
                    description="Answer the questions below, then click Approve to submit.",
                    questions = questions,
                    timeout_seconds = 600,
                )
        except Exception:
            pass
        return True
    elif icmd == "summary":
        # Get interrogation summary
        result = interrogator.get_interrogation_summary()
        print(prompt_bridge.dumps_json(result))
        return True
    elif icmd == "force - complete":
        # Force complete interrogation
        result = interrogator.force_complete_interrogation()
        print(prompt_bridge.dumps_json(result))
        return True
    elif icmd == "complete - from - charter":
        # Non - interactive completion using existing charter
        result = interrogator.complete_from_charter()
        print(prompt_bridge.dumps_json(result))
        return True

    print('{"error":"unknown interrogate subcommand"}')
    return True
