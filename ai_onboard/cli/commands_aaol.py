"""CLI commands for AI Agent Orchestration Layer (AAOL)."""

import argparse
import json
from pathlib import Path
from ..core.ai_agent_orchestration import create_ai_agent_orchestrator


def add_aaol_commands(subparsers):
    """Add AAOL command parsers."""
    
    # AAOL main command
    s_aaol = subparsers.add_parser("aaol", help="AI Agent Orchestration Layer - Revolutionary collaborative system")
    aaol_sub = s_aaol.add_subparsers(dest="aaol_cmd", required=True)
    
    # Create session
    s_create = aaol_sub.add_parser("create-session", help="Create new AI agent conversation session")
    s_create.add_argument("--user-id", default="default", help="User identifier")
    
    # Process conversation
    s_converse = aaol_sub.add_parser("converse", help="Process conversation through decision pipeline")
    s_converse.add_argument("--session-id", required=True, help="Session identifier")
    s_converse.add_argument("--message", required=True, help="User message/input")
    
    # Execute plan
    s_execute = aaol_sub.add_parser("execute", help="Execute planned commands for session")
    s_execute.add_argument("--session-id", required=True, help="Session identifier")
    
    # Session status
    s_status = aaol_sub.add_parser("status", help="Get session status and details")
    s_status.add_argument("--session-id", required=True, help="Session identifier")
    
    # Demo conversation
    s_demo = aaol_sub.add_parser("demo", help="Run interactive demo of AAOL system")


def handle_aaol_commands(args, root: Path):
    """Handle AAOL command execution."""
    
    orchestrator = create_ai_agent_orchestrator(root)
    
    if args.aaol_cmd == "create-session":
        # Create new session
        session_id = orchestrator.create_session(args.user_id)
        
        result = {
            "action": "session_created",
            "session_id": session_id,
            "user_id": args.user_id,
            "message": "New AI agent conversation session created"
        }
        
        print(json.dumps(result, indent=2))
        return True
    
    elif args.aaol_cmd == "converse":
        # Process conversation
        result = orchestrator.process_conversation(args.session_id, args.message)
        
        print("🤖 AI Agent Orchestration Layer Response:")
        print("="*60)
        
        # Show AI agent response
        if result.get("ai_agent_response"):
            print(f"🤖 AI Agent: {result['ai_agent_response']}")
        
        # Show pipeline details
        if result.get("pipeline_stages"):
            print(f"\n📊 Decision Pipeline Results:")
            for stage, details in result["pipeline_stages"].items():
                print(f"   {stage}: {details}")
        
        # Show execution readiness
        if result.get("ready_to_execute"):
            print(f"\n🚀 Ready to Execute!")
            print(f"   Commands: {result.get('execution_plan', {}).get('commands', [])}")
            print(f"   Run: ai_onboard aaol execute --session-id {args.session_id}")
        else:
            print(f"\n💬 Waiting for more input...")
        
        return True
    
    elif args.aaol_cmd == "execute":
        # Execute planned commands
        result = orchestrator.execute_plan(args.session_id)
        
        print("🚀 Execution Results:")
        print("="*40)
        
        if result.get("success"):
            print("✅ All commands executed successfully!")
            print(f"   Executed: {result.get('executed_commands', [])}")
        else:
            print("❌ Execution failed!")
            print(f"   Failed command: {result.get('failed_command')}")
            print(f"   Error: {result.get('error_details')}")
            
            if result.get("rollback_performed"):
                print("🔄 Automatic rollback performed - system restored to previous state")
            else:
                print("⚠️  Rollback failed - manual intervention may be required")
        
        return True
    
    elif args.aaol_cmd == "status":
        # Get session status
        status = orchestrator.get_session_status(args.session_id)
        
        print("📊 Session Status:")
        print("="*30)
        print(json.dumps(status, indent=2, default=str))
        
        return True
    
    elif args.aaol_cmd == "demo":
        # Interactive demo
        print("🚀 AI Agent Orchestration Layer (AAOL) Demo")
        print("="*50)
        print("This demo shows how AI agents can have collaborative conversations")
        print("with advanced decision-making and safety monitoring.\n")
        
        # Create demo session
        session_id = orchestrator.create_session("demo_user")
        print(f"✅ Created demo session: {session_id}\n")
        
        # Demo conversation scenarios
        demo_scenarios = [
            "I want to analyze my project and understand what it does",
            "Actually, I want to focus on real-time orderflow visualizations",
            "Can you add features for chart visualizations and data streaming?",
            "Yes, proceed with the plan"
        ]
        
        for i, scenario in enumerate(demo_scenarios, 1):
            print(f"📝 Demo Scenario {i}: {scenario}")
            result = orchestrator.process_conversation(session_id, scenario)
            
            if result.get("ai_agent_response"):
                print(f"🤖 AI Agent: {result['ai_agent_response']}")
            
            if result.get("ready_to_execute"):
                print(f"🚀 Ready to execute: {result.get('execution_plan', {}).get('commands', [])}")
                
                # In real demo, would ask user if they want to execute
                print("   [Demo mode - not executing actual commands]\n")
            else:
                print("   [Continuing conversation...]\n")
        
        print("🎯 Demo completed! The AAOL system provides:")
        print("✅ Natural conversation processing")
        print("✅ Multi-stage decision pipeline")
        print("✅ Real-time safety monitoring")
        print("✅ Command orchestration with rollback")
        print("✅ Session-based context management")
        
        return True
    
    return False
