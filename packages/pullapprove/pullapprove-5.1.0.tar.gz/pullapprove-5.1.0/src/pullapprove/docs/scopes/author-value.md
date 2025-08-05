---
title: author-value
---

# `author-value`

If the PR author is a also an eligible reviewer, you can count their approval automatically (even if the host platform doesn't allow them to approve a PR).

By default, `author_value` is `0`. Typically you will use `1` to count the author as one approval, but you can use bigger numbers to give the author more weight in the approval process.

```toml
[[scopes]]
name = "app"
author_value = 1
require = 1
reviewers = ["dev1"]
```
