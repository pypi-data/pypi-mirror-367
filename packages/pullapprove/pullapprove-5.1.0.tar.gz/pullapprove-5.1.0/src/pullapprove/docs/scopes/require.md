---
title: Require
---

# `require`

The `require` setting specifies how many approvals are needed for each scope before the PR can be merged. By default `require = 0` and approvals are not required.

```toml
[[scopes]]
name = "app"
reviewers = ["dev1", "dev2"]
require = 1
```

Behavior:

- If `require` is not met, the PR will be blocked from merging.
- If anybody in the scope rejects the PR, it will be blocked from merging.
- If `require = -1`, all reviewers must approve the PR.
