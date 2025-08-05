---
title: Authors
---

# `authors`

Scopes can be matched to specific pull request authors. This can be used to target PRs opened by a specific bot or specific team members. Note that `paths` are still required.

```toml
# CODEREVIEW.toml
[[scopes]]
name = "dependabot"
paths = ["**/*"]
authors = ["dependabot"]
reviewers = ["dev1", "dev2"]
```

Authors can also reference [`aliases`]({{ url('pages:config/aliases') }}).

```toml
# CODEREVIEW.toml
[aliases]
junior-devs = ["junior-dev1", "junior-dev2"]
senior-devs = ["senior-dev1", "senior-dev2"]

[[scopes]]
name = "junior-review"
paths = ["**/*"]
authors = ["$junior-devs"]
reviewers = ["$senior-devs"]
```

You can also use negated authors (prefixed with `!`) to exclude specific authors from matching a scope. This is useful when you want a scope to apply to all PRs except those from certain authors.


```toml
# CODEREVIEW.toml
[[scopes]]
name = "human-review"
paths = ["**/*"]
authors = ["!dependabot", "!renovate-bot"]  # Excludes bot PRs
reviewers = ["dev1", "dev2"]
```
