---
title: Templates
description: Share workflow configurations across an organization
template: markdown_page.template.html
plan_required: true
next:
  url: /
  title: Overview
prev:
  url: /
  title: Topics
---

# Templates

PullApprove configurations can be shared across your organization or projects.
This makes it easy to re-use common settings or avoid copy-pasting the same `.pullapprove.yml` into tens or hundreds of repos.

You can do this by using the [extends](/config/extends/) setting,
which simply points to a HTTP url where the template can be found.

By adding specific settings after the `extends` field,
you can build upon the template and merge the settings together.

```yaml
# (GitHub)
version: 3

extends: your-github-org/pullapprove

# these will be combined with the template groups
groups:
  group_to_add:
    ...
```

[See the "extends" documentation for more details.](/config/extends/)
