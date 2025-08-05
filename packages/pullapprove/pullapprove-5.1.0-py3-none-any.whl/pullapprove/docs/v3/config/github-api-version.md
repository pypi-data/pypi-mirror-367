---
title: GitHub API Version
description: Enable GitHub API previews in PullApprove to use new features
template: config/field.template.html
gitlab: false
bitbucket: false
next:
  url: /config/meta/
  title: Top-level meta
prev:
  url: /config/description/
  title: Group description
---

# GitHub API Version

PullApprove does not officially support new GitHub features until they are out of "preview" and suitable for production use.
If you want to build your workflow around preview features,
you need to enable them manually by setting the `github_api_version` for your repo.
Doing this will change the data that PullApprove receives from GitHub,
and might give you access to new variables when writing conditions.


Just remember &mdash; they are in preview for a reason!
Keep an eye out for potential API changes while in preview and don't be too surprised if something behaves unexpectedly.


The list of current GitHub.com API previews can be found here:
[https://docs.github.com/v3/previews/](https://docs.github.com/v3/previews/)

## Enabling draft pull requests (as of 4/15/18)

```yaml
version: 3

# https://developer.github.com/v3/previews/#draft-pull-requests
github_api_version: "shadow-cat-preview"

# You'll now have access to the "draft" variable
# in overrides and group conditions
# https://developer.github.com/v3/pulls/#get-a-single-pull-request
overrides:
- if: "draft"
  status: "pending"
  explanation: "Work in progress"

groups:
  ...
```
