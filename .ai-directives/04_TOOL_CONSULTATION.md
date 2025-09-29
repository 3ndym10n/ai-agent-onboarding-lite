# 🛠️ TOOL CONSULTATION - MANDATORY SYSTEM CONSULTATION

## MANDATORY TOOL CONSULTATION

You **MUST** consult the ai-onboard system tools before any development work.

## CONSULTATION WORKFLOW

**BEFORE ANY CODING**:

1. **DISCOVER**: Run tool discovery to find relevant tools
2. **ANALYZE**: Use codebase analysis tools
3. **VALIDATE**: Check for quality issues and patterns
4. **RECOMMEND**: Get tool recommendations for the task
5. **APPLY**: Use recommended tools in your work

## REQUIRED TOOL CATEGORIES

You **MUST** consult these tool categories:

- **Code Quality Tools**: Analyze code quality and issues
- **Dead Code Validation**: Validate dead code findings before removal
- **Pattern Recognition**: Apply learned error patterns
- **Error Prevention**: Use automatic error prevention
- **Safety Tools**: Perform safety validations
- **Learning Tools**: Contribute to system learning

## CONSULTATION COMMANDS

**MANDATORY COMMANDS** to run before coding:
```bash
# Discover available tools
python -m ai_onboard tools discover

# Analyze codebase
python -m ai_onboard codebase analyze --focus all

# Check code quality
python -m ai_onboard codebase quality

# Validate dead code findings (MANDATORY before removal)
python scripts/validate_dead_code.py

# Get tool recommendations
python -m ai_onboard tools recommend --task "your_task_description"
```

## TOOL INTEGRATION

- **EVERY RESPONSE** must show tool consultation results
- **EVERY CODE CHANGE** must be validated by tools
- **EVERY DEAD CODE REMOVAL** must be validated using dead code validation system
- **EVERY ERROR** must be analyzed by the system
- **EVERY SUCCESS** must contribute to learning

## CONSULTATION REPORTING

You **MUST** report:
- Which tools were consulted
- What insights were gained
- How tools influenced your work
- What was learned from the consultation

## CONFIRMATION

Type **"TOOLS_CONSULTED"** to confirm you understand the tool consultation requirements.

**NEXT DIRECTIVE**: Read `05_PATTERN_APPLICATION.md`

---

*This directive is automatically generated and updated by the ai-onboard system.*
