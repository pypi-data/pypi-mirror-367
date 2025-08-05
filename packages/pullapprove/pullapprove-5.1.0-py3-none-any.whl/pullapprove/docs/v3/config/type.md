---
title: Type
description: Different types of groups can determine their behavior and impact on your review process.
plan_required: true
template: config/field.template.html
next:
  url: /config/meta/
  title: Group meta
prev:
  url: /config/reviews/
  title: Request and require reviews
---

# Type

There are currently two types of groups: `required` (the default) and `optional`.
Changing the type of group can allow you to design more complex workflows by altering how it plays into the rest of your review process.

## Values

### `required`

An [active](/config/conditions/), `required` group must approve the PR for PullApprove to pass.

**This is the default value**, but you can use it explicitly if you want.

```yaml
version: 3
groups:
  code:
    type: required
    ...
```

### `optional`

> This feature is available on the [business and organization plans](https://www.pullapprove.com/pricing/).

An `optional` group doesn't directly impact the overall PullApprove status.
They can approve or reject a PR if they want to cast their vote,
but it won't affect your review process unless you leverage [conditions](/config/conditions/) later in the process to reincorporate it in a custom way.

```yaml
version: 3
groups:
  global:
    type: optional
    ...
```
