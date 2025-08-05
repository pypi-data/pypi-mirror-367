---
title: Version
description: Set the PullApprove version
template: config/field.template.html
next:
  url: /config/extends/
  title: Extend a template
prev:
  url: /config/
  title: See all YAML fields
---

# Version

The version needs to be 3!
That's it.
If you are still using version 1 or 2,
you'll need to look at the [older documentation](https://v2-docs.pullapprove.com) and we highly recommend you [upgrade as soon as possible](/migration/).

<div class="bg-yellow-200 text-yellow-800 p-4 shadow rounded mb-4">
  Note that the <strong>version field is required!</strong>
  If you don't include it, we assume you are using an older version of PullApprove and you may not see any activity.
</div>

```yaml
version: 3
groups:
  ...
```
