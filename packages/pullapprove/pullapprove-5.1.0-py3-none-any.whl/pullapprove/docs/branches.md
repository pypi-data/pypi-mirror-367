---
title: Branches
---

# `branches`

PullApprove runs when a `CODEREVIEW.toml` is found in the branch's base commit. The configuration is always pulled from the base branch, which means a PR can't modify the requirements for its own review.

There may be branches where the `CODEREVIEW.toml` is present, but you don't want PullApprove to run (usually because it will run later in a subsequent PR). The top-level `branches` setting can be used to define when PullApprove runs.

```toml
branches = ["main", "develop"]
```

Branch names are evaluated using fnmatch syntax, and can also use the git `..` syntax to specify the head and base branches.

```toml
branches = [
    "main",  # base only
    "release/*",  # base with pattern
    "feature/*..develop",  # base and head
    "..develop",  # head only
]
```
