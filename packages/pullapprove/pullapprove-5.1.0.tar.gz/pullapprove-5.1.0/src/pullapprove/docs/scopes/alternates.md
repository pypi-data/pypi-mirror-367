---
title: Alternates
---

# `alternates`

Each scope can list a set of `alternates` that can approve a PR, but won't be requested automatically. This is another useful way to include fallback reviewers, managers, or "emeritus" team members.

```toml
[[scopes]]
name = "app"
paths = ["app/*"]
reviewers = ["dev1"]
alternates = ["admin1", "emeritus1"]
require = 1
```

You can also use aliases in the `alternates` list to reference predefined groups of users.
