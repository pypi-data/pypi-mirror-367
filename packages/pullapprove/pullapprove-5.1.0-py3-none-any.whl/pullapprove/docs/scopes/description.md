---
title: Description
---

# `description`

Additional info about the scope can be saved as the `description`.

Unlike TOML comments, the `description` field can be displayed in user interfaces, making it visible to reviewers and other users of the system.

```toml
[[scopes]]
name = "database"
description = "Any changes to migrations or schema need to be reviewed for x, y, and z."
# ...
```
