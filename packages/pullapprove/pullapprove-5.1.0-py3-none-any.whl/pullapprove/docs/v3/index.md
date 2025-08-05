---
title: Overview
description: Documentation and examples of how to use PullApprove
template: markdown_page.template.html
next:
  url: /examples/
  title: Examples
prev:
  url: /
  title: Topics
---

# Overview

PullApprove is configured by a `.pullapprove.yml` file,
which is placed in the root of your repo.

The basic idea is to organize your reviews into review [`groups`](/config/groups/).
Groups might be split by language or specific areas of your codebase,
or instead might be different types of review that need to be done
(e.g. "security" or "design").

However you decide to organize your groups,
you can use the group [`conditions`](/config/conditions/) to determine when each group is asked to review a PR.
When the conditions are met,
the group is considered *active* and review requests will be sent out automatically.

Here's a simple example:

```yaml
# .pullapprove.yml
version: 3

overrides:
- if: "base.ref != 'master'"
  status: success
  explanation: "Review only required when merging to master"

groups:
  code:
    reviewers:
      users:
      - reviewerA
      - reviewerB
    reviews:
      required: 2
      request: 1
      request_order: random
    labels:
      approved: "Code review approved"

  database:
    conditions:
    - "'*migrations*' in files"
    reviewers:
      teams:
      - database
```
