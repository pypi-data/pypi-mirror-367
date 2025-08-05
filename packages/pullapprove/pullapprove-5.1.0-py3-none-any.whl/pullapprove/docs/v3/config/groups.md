---
title: Groups
description: Organize review workflows into groups
template: config/field.template.html
next:
  url: /config/conditions/
  title: Group conditions
prev:
  url: /config/notifications/
  title: Automate notifications
---

# Groups

Review groups are the key component of PullApprove.
For simple use cases,
you may only need one group.
For more sophisitcated setups,
groups can be used to divide reviewers by language, specialty, role,
or anything else you use to organize your workflow.
Groups can even depend on other groups to build a [phased review process](#phased-reviews).

Each group comes with its own rules for [when they are asked to review](/config/conditions/),
provides controls for how [reviewers](/config/reviewers/) are [selected](/config/reviews/),
and [how many reviews are required for approval](/config/reviews/).

```yaml
version: 3
groups:
  # group name
  ux:
    # the group is activated when all of these statements are true
    conditions:
    - '"ui/ux" in labels'
    # people who can approve for this group
    reviewers:
      teams:
      - design
    # settings for approval and reviewer selection
    reviews:
      required: 1
      request: 2
```

## Phased reviews

With advanced use of the [conditions](/config/conditions/) setting,
  you can set up reviews to be done in "phases", or happen in separate steps.

This is particularly useful if there are certain people that you don't want to
  bug until other parts of the review have been completed &mdash; either because their
  time is more valuable or because their area of review isn't necessary until
  other aspects have already been approved.

You can set this up by making groups depend on other groups. The
`groups` variable comes with a [set of convenient properties](/context/#groups) for
checking the state of other groups.

**Important:** Groups are evaluated *in order*, and the
`groups` variable only contains the preceding groups when you write
[conditions](/config/conditions/).

```yaml
version: 3

groups:
  code:
    ...

  database:
    ...
    conditions:
    # only asked to review once "code" has finished
    - "'code' in groups.approved"
```
