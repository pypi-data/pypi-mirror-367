---
title: Reviewers
---

# `reviewers`

For each scope, you can define a list of reviewers. These are the people who are eligible to approve changes if you use `require`, and who will be requested to review the PR if you use `request`.

```toml
[[scopes]]
name = "database"
reviewers = [
    "databaseExpert1",
    "databaseExpert2",
]
paths = ["**/*/migrations/**/*"]
```

To re-use a list of reviewers across scopes, look at [`aliases`](#aliases).

## Wildcard Reviewers

You can use `"*"` as a special wildcard value to accept reviews from anyone:

```toml
# Require 2 reviews from anyone
[[scopes]]
name = "general-review"
reviewers = ["*"]
require = 2
paths = ["**/*.py"]
```

When using wildcard reviewers:
- Anybody with permission can approve the PR
- You can mix wildcards with explicit reviewers: `reviewers = ["alice", "*"]`
- With mixed reviewers, only specific reviewers (not `*`) will be auto-requested
- Author value (`author_value`) only applies to explicitly listed reviewers, not those covered by `*`
