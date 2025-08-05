---
title: Scopes
---

# `scopes`

Review scopes are defined in order, and the last matching scope for a file is the one who has to review it. This is the default behavior and most similar to CODEOWNERS.

Unlike most CODEOWNERS implementations, PullApprove allows you to define approval requirements per scope. So certain paths can require approvals, while others notify but don't block. Or more critical paths can require 2 approvals while less critical paths only require 1.

The name of a scope needs to be a unique slug and should be descriptive — it will be used in various places during the review process so people should understand what it means.

**Note:** Draft pull requests are automatically skipped by PullApprove and won't be processed until they are marked as ready for review.

```toml
[[scopes]]
name = "global"
# ...

[[scopes]]
name = "security"
# ...

[[scopes]]
name = "dependencies"
# ...

[[scopes]]
name = "docs"
# ...

[[scopes]]
name = "database"
# ...
```

Additional info about the scope can be saved as the `description`.

```toml
[[scopes]]
name = "database"
description = "Any changes to migrations or schema need to be reviewed for x, y, and z."
# ...
```
