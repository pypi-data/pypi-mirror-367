---
title: Description
description: Describe what this group is for and how it functions.
template: config/field.template.html
next:
  url: /config/github-api-version/
  title: GitHub API version
prev:
  url: /config/meta/
  title: Group meta
---

# Description

Tell your users more about the purpose of this group,
how to use it,
or where to direct questions about it.

This information will show up in the PullApprove report UI and can contain markdown.

```yaml
version: 3

groups:
  security:
    description: >
      [Security-related](https://en.wikipedia.org/wiki/Secure_coding)
      code will trigger this group automatically by
      using the regular expressions in the conditions.

      If you need to request a security review manually,
      apply the `security` label and someone will
      be requested for review.

```
