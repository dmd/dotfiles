# Global Claude Code Instructions

## Python Execution

Whenever executing python, use python3.

**Always use uv for Python scripts with inline dependency metadata:**

Every Python script must start with a block like:

```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "requests",
#   "tqdm",
#   # these are only examples - include the dependencies that are actually needed
# ]
# ///

# ... rest of code
```

With this shebang, scripts can be executed directly (e.g., `./script.py`) and uv will automatically handle dependencies.

This ensures consistent dependency management and execution across all Python scripts.

## Shell Compatibility

**Use `/bin/bash -c '...'` for complex shell commands:**

The default shell environment has zsh compatibility issues with common bash syntax:
- Command substitution `$(...)` may fail with parse errors
- Here-strings `<<<` don't work reliably
- Parameter expansion like `${VAR%%:*}` may produce empty results

For commands involving variable parsing, pipelines, or subshells, wrap them:
```bash
/bin/bash -c 'api_key=$(echo "$VAR" | cut -d: -f1); curl -H "Key: $api_key" ...'
```

Simple commands (single binaries, no shell features) can run directly.

## Miscellaneous

- Don't keep telling me things are the smoking gun or the critical issue, as you're almost never right.