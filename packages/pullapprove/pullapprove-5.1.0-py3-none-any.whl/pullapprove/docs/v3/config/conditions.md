---
title: Group conditions
description: Custom rules for deciding who needs to review which PRs
template: config/field.template.html
next:
  url: /config/labels/
  title: Group labels
prev:
  url: /config/groups/
  title: Set up your groups
---

# Group conditions

Write [expressions](/expressions/) to decide which PRs each group needs to review.
This often aligns with how your organization is structured or how your project is organized.

You can match groups to PRs using paths, branches, written descriptions, labels, diffs, other checks or statuses, etc.

For team hierarchies or more complex processes, you can even trigger groups based on the status of *other* groups.

**Every condition in the list must be met for the group to be activated.**
If you need to "or" a condition, then you can simply use the word "or".

```yaml
# (GitHub)
version: 3
groups:
  example-group:
    conditions:
    - '"bug" in labels or "error" in labels'
    - '"app/*" in files
```

```yaml
# (Bitbucket)
version: 3
groups:
  example-group:
    conditions:
    - '"app/*" in diffstat
```

```yaml
# (GitLab)
version: 3
groups:
  example-group:
    conditions:
    - '"bug" in labels or "error" in labels'
```

[See more examples of expressions →](/expressions/)
