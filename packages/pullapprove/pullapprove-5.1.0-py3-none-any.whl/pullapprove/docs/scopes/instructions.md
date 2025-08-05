---
title: Instructions
---

# `instructions`

Review instructions can be sent to reviewers when they are requested to review a PR. When scopes are matched to a PR, the instructions are sent as a comment.

```toml
[[scopes]]
name = "database"
instructions = """
This change requires a database migration. Please review the migration script and ensure it is safe to run.
"""
```
