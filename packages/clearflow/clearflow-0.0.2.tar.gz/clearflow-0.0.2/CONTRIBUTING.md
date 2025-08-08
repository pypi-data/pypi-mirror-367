# Contributing

## Requirements

All contributions must maintain:
- 100% test coverage
- Zero type errors (mypy and pyright strict mode)
- No external dependencies

## Setup

```bash
git clone https://github.com/consent-ai/ClearFlow.git
cd ClearFlow
uv sync --group dev
./quality-check.sh  # Must pass before PR
```

## Pull Requests

1. One change per PR
2. Run `./quality-check.sh`
3. Update tests (maintain 100% coverage)
4. Use conventional commits: `fix:`, `feat:`, `docs:`

## State Management

ClearFlow uses immutable state:

```python
# Correct - using transform()
new_state = state.transform(lambda d: {**d, "processed": True})

# Wrong - mutation not allowed
state.data["key"] = value
```

## What Gets Merged

✅ Bug fixes with tests  
✅ Performance improvements with benchmarks  
✅ Examples showing real patterns  

❌ External dependencies  
❌ Features that add complexity  
❌ Code that reduces type safety  

## Questions?

Open an issue for discussion.