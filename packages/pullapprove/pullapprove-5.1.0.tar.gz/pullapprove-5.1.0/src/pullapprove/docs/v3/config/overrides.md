---
title: Overrides
description: Manually set the PullApprove status using custom expressions.
template: config/field.template.html
next:
  url: /config/notifications/
  title: Automate notifications
prev:
  url: /config/extends/
  title: Extend a template
---

# Overrides

Manually control the PullApprove status with overrides.
The overrides are processed in order and the first match (if any) will determine the status on the pull request.
[Review requests](/config/reviews/#request), [label changes](/config/labels/), and [notifications](/config/notifications/) are *not* sent if an override matches a PR.

There are several situations where you may want to override the results of your `groups`:

- Skip review for PRs to specific branches
- Create "escape hatches" for hotfix PRs by using labels
- Pausing review until CI tests are passing

```yaml
version: 3
overrides:
- if: "draft or 'WIP' in title"
  status: pending

- if: "base.ref != 'master'"
  status: success

- if: "'hotfix' in labels"
  status: success

- if: "'*test*' not in statuses.successful"
  status: failure
  explanation: "Tests must be passing before review starts"
```

Unlike the deprecated [pullapprove_conditions](/config/pullapprove-conditions/), overrides are processed *after* the groups are evaluated,
which means you can write expressions that consider the state of the groups themselves.

```yaml
version: 3

overrides:
- if: "len(groups.active) < 1"
  status: failure
  explanation: "At least one group must match this PR. A new group may need to be added to match this kind of PR."
```
