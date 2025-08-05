---
title: Labels
---

# `labels`

Each scope can define an associated label. The label will be added to a PR automatically when a scope matches.

<!-- A label can also be added manually as an alternative way to flag a PR for a specific scope. -->

```toml
[[scopes]]
name = "app"
paths = ["app/**/*"]
labels = ["review/app"]
```

You can also use aliases in the `labels` list to reference predefined label groups.

<!-- With labels, it's actually possible to have a scope that is not matched to any specific files, but is instead triggered by a label.

TODO this doesn't quite work...
if path required, it will apply the label
if path not required, kinda weird?
it also makes it impossible to fully examine a diff without a PR...
but for that matter, you can't check requirements met without PR either...

[[scopes]]
name = "large-scale-changes"
paths = ["**/*"]
label = "review/large-scale-change"
reviewers = ["admin1"]
require = 1

-->
