---
title: Template
---

# `template`

If a `CODEREVIEW.toml` file is marked as a template, it will not be processed as a live configuration file. Other `CODEREVIEW.toml` files can extend a template file, but the template file itself will not be used to review PRs.

```toml
# .codereview/base.toml
template = true

[[scopes]]
# ...
```

```toml
# CODEREVIEW.toml
extends = ".codereview/base.toml"

[[scopes]]
# ...
```
