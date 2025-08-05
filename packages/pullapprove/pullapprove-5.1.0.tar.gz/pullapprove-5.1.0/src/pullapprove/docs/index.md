---
title: PullApprove Configuration
---

# PullApprove Configuration

PullApprove is a powerful code review automation tool that uses a `CODEREVIEW.toml` file to define review requirements and workflows. This documentation covers all available configuration options and how to use them effectively.

## Quick Start

A basic `CODEREVIEW.toml` file contains one or more review scopes:

```toml
[[scopes]]
name = "app"
paths = ["app/**/*"]
reviewers = ["dev1", "dev2"]
require = 1
```

## Configuration Structure

### Root Configuration

These settings apply to the entire configuration file:

- **[`aliases`](aliases.md)** - Define reusable reviewer groups with `$` prefix syntax
- **[`branches`](branches.md)** - Control which branches PullApprove runs on
- **[`extends`](extends.md)** - Inherit configuration from other CODEREVIEW.toml files
- **[`template`](template.md)** - Mark a configuration as a template for reuse

### Review Scopes

The core of PullApprove configuration is the `[[scopes]]` array. Each scope defines review requirements for specific files or conditions.

#### Basic Scope Properties

- **[`name`](scopes/name.md)** - Unique identifier for the scope (required)
- **[`description`](scopes/description.md)** - Human-readable description of the scope's purpose
- **[`paths`](scopes/paths.md)** - Glob patterns to match files (required)

#### Reviewer Configuration

- **[`reviewers`](scopes/reviewers.md)** - List of eligible reviewers for this scope
- **[`alternates`](scopes/alternates.md)** - Additional reviewers who can approve but won't be auto-requested
- **[`require`](scopes/require.md)** - Number of approvals required (default: 0)
- **[`request`](scopes/request.md)** - Number of reviewers to auto-request

#### Advanced Matching

- **[`authors`](scopes/authors.md)** - Match scopes to specific PR authors
- **[`code`](scopes/code.md)** - Match scopes based on code changes within files
- **[`labels`](scopes/labels.md)** - Automatically apply labels when scope matches

#### Ownership Models

- **[`ownership`](scopes/ownership.md)** - Control how scopes interact (`append`, `global`)
- **[`author_value`](scopes/author-value.md)** - Count PR author as an approver
- **[`reviewed_for`](scopes/reviewed-for.md)** - Require explicit scope acknowledgment in reviews

#### Communication

- **[`instructions`](scopes/instructions.md)** - Send custom instructions to reviewers

## Configuration Examples

### Basic Setup

```toml
[[scopes]]
name = "general"
paths = ["**/*"]
reviewers = ["dev1", "dev2", "dev3"]
require = 1
request = 1
```

### Using Aliases

```toml
[aliases]
backend_team = ["alice", "bob", "charlie"]
frontend_team = ["dave", "eve", "frank"]

[[scopes]]
name = "backend"
paths = ["api/**/*", "**/*.py"]
reviewers = ["$backend_team"]
require = 2

[[scopes]]
name = "frontend"
paths = ["web/**/*", "**/*.js", "**/*.css"]
reviewers = ["$frontend_team"]
require = 1
```

### Multi-Level Ownership

```toml
# Global admins can approve anything
[[scopes]]
name = "admins"
ownership = "global"
paths = ["**/*"]
reviewers = ["admin1", "admin2"]

# Security changes always need security team
[[scopes]]
name = "security"
ownership = "append"
paths = ["**/security/**/*"]
reviewers = ["security-expert"]
require = 1

# Regular app changes
[[scopes]]
name = "app"
paths = ["app/**/*"]
reviewers = ["dev1", "dev2"]
require = 1
```

### Code Pattern Matching

```toml
[[scopes]]
name = "security-sensitive"
paths = ["**/*.py"]
code = [
    "^(\+|-).*@csrf_exempt.*",
    "^(\+|-).*subprocess\.",
    "^(\+|-).*eval\("
]
reviewers = ["security-team"]
require = 2
instructions = """
This change contains security-sensitive code patterns.
Please review carefully for potential vulnerabilities.
"""
```

## How Scopes Work

1. **Order Matters**: Scopes are evaluated in the order they're defined
2. **Last Match Wins**: By default, the last matching scope determines who reviews a file
3. **Ownership Modifiers**: Use `append` or `global` ownership to change this behavior
4. **Multiple Files**: Each changed file is matched independently to scopes
5. **Draft PRs**: Draft pull requests are automatically skipped and not processed by PullApprove

## Best Practices

- **Start Simple**: Begin with basic path-based scopes and add complexity as needed
- **Use Descriptive Names**: Scope names appear in the UI, make them clear
- **Leverage Aliases**: Reduce duplication and make updates easier
- **Test Your Config**: Use the CLI to validate and test your configuration
- **Document Complex Logic**: Use `description` and `instructions` for clarity

## Advanced Features

### Multiple Configuration Files

You can have multiple `CODEREVIEW.toml` files in different directories. The closest one to each changed file will be used:

```toml
# app/CODEREVIEW.toml
extends = ["../CODEREVIEW.toml"]

[[scopes]]
name = "app-specific"
paths = ["**/*"]
reviewers = ["app-team"]
```

### Branch-Specific Configuration

Control when PullApprove runs using branch patterns:

```toml
branches = [
    "main",
    "release/*",
    "feature/*..develop"
]
```

### Wildcard Reviewers

Accept reviews from anyone with `"*"`:

```toml
[[scopes]]
name = "open-review"
reviewers = ["*"]
require = 2
paths = ["docs/**/*"]
```

## Related Documentation

- [Scopes Overview](scopes/index.md) - Detailed information about review scopes
- CLI Commands - Use the included CLI to validate and test configurations
- Templates - Share configuration across repositories using the admin UI

This configuration system provides the flexibility to implement sophisticated code review workflows while maintaining clarity and auditability. Start with simple configurations and gradually add complexity as your team's needs evolve.