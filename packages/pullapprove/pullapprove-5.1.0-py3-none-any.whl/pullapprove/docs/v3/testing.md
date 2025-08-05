---
title: Testing review workflows
description: Test new workflows on live pull requests
template: markdown_page.template.html
next:
  url: /templates/
  title: Templates
prev:
  url: /
  title: Topics
---

# Testing review workflows

The best way to test a PullApprove config is on a real PR.
To do this, leave a PR *review* comment in this format:

````md
# (GitHub review comment)
/pullapprove-test

```yaml
version: 3
groups:
  ...
```
````

PullApprove will send the results back to the PR in a comment.
Note that this is effectively a "dry run",
and won't modify any status checks or send out review requests.

[![PullApprove config test command](/assets/img/screenshots/config-test-input.png)](/assets/img/screenshots/config-test-input.png)
