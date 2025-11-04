# ForgeBase Quick Start

Get started with ForgeBase in 5 minutes.

## 🚀 Installation

```bash
# Install from GitHub
pip install git+https://github.com/palhanobrazil/forgebase.git@v0.1.3

# Verify installation
python -c "from forgebase.dev.api import QualityChecker; print('✅ ForgeBase ready!')"
```

## 📝 Your First UseCase

```python
from forgebase.dev.api import ScaffoldGenerator

# Generate UseCase boilerplate
generator = ScaffoldGenerator()
result = generator.create_usecase(
    name="CreateUser",
    input_type="CreateUserInput",
    output_type="CreateUserOutput"
)

# Write to file
with open(result.file_path, 'w') as f:
    f.write(result.code)

print(f"✅ UseCase created at: {result.file_path}")
```

## 🔍 Check Code Quality

```python
from forgebase.dev.api import QualityChecker

# Run all quality checks
checker = QualityChecker()
results = checker.run_all()

# See results
for tool, result in results.items():
    status = "✅" if result.passed else "❌"
    print(f"{status} {tool}: {len(result.errors)} errors")
```

## 🧪 Run Tests

```python
from forgebase.dev.api import TestRunner

# Run all tests
runner = TestRunner()
results = runner.run_all()

# See results
for test_type, result in results.items():
    status = "✅" if result.passed else "❌"
    print(f"{status} {test_type}: {result.passed_count}/{result.total}")
```

## 🗺️ Explore Codebase

```python
from forgebase.dev.api import ComponentDiscovery

# Discover components
discovery = ComponentDiscovery()
components = discovery.scan_project()

# See what you have
print(f"📦 Found:")
print(f"   - {len(components.entities)} Entities")
print(f"   - {len(components.usecases)} UseCases")
print(f"   - {len(components.repositories)} Repositories")
```

## 🎯 Complete Example

```python
"""
Complete ForgeBase workflow example.
"""
from forgebase.dev.api import (
    ScaffoldGenerator,
    QualityChecker,
    TestRunner,
    ComponentDiscovery
)

def main():
    # 1. Understand what exists
    print("📊 Step 1: Discovering components...")
    discovery = ComponentDiscovery()
    components = discovery.scan_project()
    print(f"   Found {len(components.entities)} entities")

    # 2. Generate new component
    print("\n🏗️  Step 2: Generating UseCase...")
    generator = ScaffoldGenerator()
    result = generator.create_usecase(
        name="ProcessOrder",
        input_type="OrderInput",
        output_type="OrderOutput"
    )

    if result.success:
        with open(result.file_path, 'w') as f:
            f.write(result.code)
        print(f"   Created: {result.file_path}")

    # 3. Check quality
    print("\n✅ Step 3: Checking quality...")
    checker = QualityChecker()
    quality = checker.run_all()

    all_passed = all(r.passed for r in quality.values())
    print(f"   Quality: {'✅ PASSED' if all_passed else '❌ FAILED'}")

    # 4. Run tests
    print("\n🧪 Step 4: Running tests...")
    runner = TestRunner()
    tests = runner.run_all()

    all_passed = all(r.passed for r in tests.values())
    print(f"   Tests: {'✅ PASSED' if all_passed else '❌ FAILED'}")

    print("\n✅ Workflow complete!")

if __name__ == "__main__":
    main()
```

Save this as `quickstart.py` and run:
```bash
python quickstart.py
```

## 📚 Next Steps

### For AI Agents
Read the AI agent guide:
```bash
# See the quick reference
cat AI_AGENT_QUICK_START.md

# Or the complete guide
cat src/forgebase/dev/AI_AGENTS.md
```

### For Developers
Explore the examples:
```bash
# See all examples
ls examples/

# Run AI agent examples
python examples/ai_agent_usage.py

# Run Claude API integration
export ANTHROPIC_API_KEY="your-key"
python examples/claude_api_integration.py
```

### Learn More
- **Installation Details**: See `INSTALLATION.md`
- **Full Documentation**: See `README.md`
- **API Reference**: See `src/forgebase/dev/AI_AGENTS.md`
- **Changelog**: See `CHANGELOG.md`

## 🎓 Tutorials

### Tutorial 1: Create Your First Entity

```python
from forgebase.dev.api import ScaffoldGenerator

generator = ScaffoldGenerator()
result = generator.create_entity(
    name="Product",
    attributes=["name", "price", "stock"]
)

with open(result.file_path, 'w') as f:
    f.write(result.code)

print(f"✅ Entity created: {result.file_path}")
```

### Tutorial 2: Fix Code Quality Issues

```python
from forgebase.dev.api import QualityChecker

checker = QualityChecker()
results = checker.run_ruff(["."])

# Show errors
for error in results.errors:
    print(f"❌ {error['file']}:{error['line']}")
    print(f"   {error['code']}: {error['message']}")

    # Auto-fix if possible
    if error['code'] == 'F401':  # Unused import
        print(f"   💡 Action: Remove unused import")
```

### Tutorial 3: Analyze Test Failures

```python
from forgebase.dev.api import TestRunner

runner = TestRunner()
results = runner.run_unit_tests()

if not results.passed:
    print("❌ Test failures:")
    for failure in results.failures:
        print(f"\n  Test: {failure.test_name}")
        print(f"  File: {failure.file}:{failure.line}")
        print(f"  Error: {failure.error_type}")
        print(f"  Message: {failure.message}")
```

## 💡 Pro Tips

1. **Use specific versions in production:**
   ```bash
   pip install git+https://github.com/palhanobrazil/forgebase.git@v0.1.3
   ```

2. **Cache discovery results:**
   ```python
   discovery = ComponentDiscovery()
   components = discovery.scan_project()
   # Reuse 'components' instead of scanning again
   ```

3. **Check error codes for smart fixing:**
   ```python
   if error['code'] == 'F401':
       action = "remove_import"
   elif error['code'] == 'no-untyped-def':
       action = "add_type_hints"
   ```

4. **Use run_all() for batch operations:**
   ```python
   # One call, all checks
   results = checker.run_all()
   ```

## 🚨 Common Issues

### Import Error
```python
# ❌ Error: No module named 'forgebase'
# ✅ Solution: Install first
pip install git+https://github.com/palhanobrazil/forgebase.git@v0.1.3
```

### Dev APIs Not Found
```python
# ❌ Error: No module named 'forgebase.dev.api'
# ✅ Solution: Install with dev dependencies
pip install "forgebase[dev] @ git+https://github.com/palhanobrazil/forgebase.git@v0.1.3"
```

### Git Not Found
```bash
# ❌ Error: git: command not found
# ✅ Solution: Install git
sudo apt-get install git  # Ubuntu/Debian
brew install git          # macOS
```

## 🔗 Resources

- **GitHub**: https://github.com/palhanobrazil/forgebase
- **AI Guide**: `AI_AGENT_QUICK_START.md`
- **Installation**: `INSTALLATION.md`
- **Examples**: `examples/`

---

**Ready to build?** Start with the complete example above! 🚀
