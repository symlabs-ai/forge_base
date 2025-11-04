# Claude Code Configuration for ForgeBase

This directory contains instructions for Claude Code to work effectively with ForgeBase.

## 📁 Files in this Directory

- **forgebase_instructions.md** - Complete instructions for Claude Code
  - API usage guidelines
  - Error code mappings
  - Workflow examples
  - Best practices

## 🎯 How Claude Code Uses These Instructions

When you open this project in Claude Code, it will:

1. ✅ **Auto-detect** the `.claude/` directory
2. ✅ **Load** `forgebase_instructions.md` into context
3. ✅ **Use** ForgeBase Python APIs instead of CLI
4. ✅ **Access** structured error data (no text parsing)
5. ✅ **Reason** about error codes to determine fixes

## 🚀 Quick Setup

### For You (Project Owner)

**Nothing to do!** This directory is already configured.

When you ask Claude Code to:
- "Fix linting errors" → Uses `QualityChecker().run_all()`
- "Create a UseCase" → Uses `ScaffoldGenerator().create_usecase()`
- "What's in the codebase?" → Uses `ComponentDiscovery().scan_project()`
- "Run tests" → Uses `TestRunner().run_all()`

### For Claude Code (AI Agent)

**Read `forgebase_instructions.md` at session start.**

Key principles:
1. Import APIs: `from forgebase.dev.api import *`
2. Use structured data: Access `error['code']`, `error['file']`, `error['line']`
3. Map error codes to actions: `F401` → remove import, `no-untyped-def` → add types
4. Modify generated code: ScaffoldGenerator returns strings for customization
5. Always verify: Run quality checks before completing tasks

## 📊 Example Session

**User**: "Fix all the linting errors"

**Claude Code thinks**:
```
I should use QualityChecker API instead of running CLI commands.
This will give me structured error data with file, line, and error codes.
```

**Claude Code does**:
```python
from forgebase.dev.api import QualityChecker

checker = QualityChecker()
results = checker.run_all()

for tool, result in results.items():
    if not result.passed:
        for error in result.errors:
            # I can see exactly what to fix
            if error['code'] == 'F401':  # Unused import
                # Remove import at error['file']:error['line']
                fix_unused_import(error['file'], error['line'])
```

**Claude Code reports**:
```
Fixed 5 linting errors:
- Removed unused imports (F401) in user.py:10, order.py:5
- Added type hints (no-untyped-def) in service.py:42
- Fixed import order (I001) in repository.py:3

All quality checks now passing! ✅
```

## 🎓 Learning Path for Claude Code

### Level 1: Basic API Usage
- Read: `forgebase_instructions.md` (this directory)
- Practice: Run `QualityChecker`, understand error structure
- Goal: Stop using CLI, use Python APIs

### Level 2: Error Code Reasoning
- Memorize: Common error codes (F401, F841, no-untyped-def, etc.)
- Practice: Map error codes to specific fixes
- Goal: Autonomous error fixing

### Level 3: Code Generation
- Use: `ScaffoldGenerator` for boilerplate
- Practice: Customize generated code for requirements
- Goal: Generate + customize in one step

### Level 4: Autonomous Workflows
- Combine: Discovery → Generation → Quality → Testing
- Practice: Complete features end-to-end
- Goal: Full autonomous development

## 💡 Pro Tips

1. **Session Start**: Import all APIs once, reuse instances
   ```python
   from forgebase.dev.api import (
       QualityChecker,
       ScaffoldGenerator,
       ComponentDiscovery,
       TestRunner
   )

   checker = QualityChecker()  # Reuse this
   ```

2. **Error Codes**: Learn the common ones
   - `F401` = unused import → remove it
   - `F841` = unused variable → remove it
   - `no-untyped-def` = no type hints → add them
   - `E501` = line too long → break it

3. **Structured Access**: Never parse text
   ```python
   # ✅ Good
   file = error['file']
   line = error['line']
   code = error['code']

   # ❌ Bad
   match = re.search(r"(\w+\.py):(\d+)", text)
   ```

4. **Verify Always**: Check quality before completing
   ```python
   # After making changes
   results = checker.run_all()
   if all(r.passed for r in results.values()):
       print("✅ All checks passed!")
   ```

## 🔗 Additional Resources

- **Quick Reference**: `/AI_AGENT_QUICK_START.md` (root directory)
- **Complete Docs**: `/src/forgebase/dev/AI_AGENTS.md`
- **Code Examples**: `/examples/ai_agent_usage.py`
- **Claude API Integration**: `/examples/claude_api_integration.py`

## 🛠️ Customization

To modify Claude Code's behavior, edit:
- `forgebase_instructions.md` - Add project-specific guidelines
- Add more `.md` files here - Claude Code will read them

Example additions:
- `architecture_decisions.md` - ADRs for this project
- `coding_standards.md` - Project-specific conventions
- `api_patterns.md` - How to use specific ForgeBase patterns

## ✅ Verification

To verify Claude Code is using APIs correctly, check for:

1. ✅ Imports from `forgebase.dev.api`
2. ✅ Direct access to error dictionaries
3. ✅ No subprocess calls to devtool
4. ✅ No regex parsing of text output
5. ✅ Error code-based reasoning

## 📞 Support

If Claude Code is not using APIs:
1. Check `.claude/forgebase_instructions.md` exists
2. Verify instructions are loaded in context
3. Explicitly remind: "Use ForgeBase Python APIs from forgebase.dev.api"

---

**Version**: ForgeBase 0.1.3
**Last Updated**: 2025-11-04
**For**: Claude Code (AI Agent)
