---
title: Extends
description: Share YAML configuration across repos using URLs to templates
template: config/field.template.html
plan_required: true
next:
  url: /config/pullapprove-conditions/
  title: Enable and disable PullApprove
prev:
  url: /config/version/
  title: PullApprove version
---

# Extends

Your repo config file can "extend" an existing config file that lives somewhere else.
This makes it easy re-use configurations across your organization and/or base your configuration off of a template.

You can reference templates in another repo, or point directly to a public HTTPS URL.

<div class="px-4 py-2 mb-4 text-yellow-800 bg-yellow-200 rounded shadow">
  In the <strong>GitLab beta</strong>, extends does not yet automatically authenticate with templates from private repos.
</div>

## Extends with repos

Use the "owner/repo" shorthand for files located on GitHub (or in your GitHub Enterprise instance).
This works for private repos in the same organization,
assuming PullApprove has permission to access to it.

```yaml
# .pullapprove.yml by default
extends: "yourorg/pullapprove"

# specify the filename
extends: "yourorg/pullapprove:pullapprove-dev.yml"

# specify a git ref
extends: "yourorg/pullapprove@v1"

# specify a git ref and filename
extends: "yourorg/pullapprove@v1:pullapprove-ops.yml"

# use a file located in the same repo
extends: "./pullapprove-ops.yml"

# using a GitHub API URL
extends: "https://api.github.com/repos/example/pullapprove-config/contents/.pullapprove.yml"
```

## Extends with URLs

URLs need to be publicly accessible,
but can be obscure if you need some level of privacy.

```yaml
extends: "https://example.com/pullapprove-config.yml"
```

## Merging behavior

When you extend a template *and* provide settings in the `.pullapprove.yml` file itself,
the settings will be merged together. You can see your merged config in the "Config" tab of the PullApprove status page.

**The basic rule is that dictionaries will be merged, and any other kinds of fields will be overwritten.**

### Basic example

```yaml
# Template YAML
version: 3
groups:
  template_group: ...
```

```yaml
# Repo YAML
version: 3
extends: <template url>
groups:
  repo_group: ...
```

```yaml
# Merged YAML
version: 3
extends: <template url>
groups:
  template_group: ...
  repo_group: ...
```

### Fields that override

Fields that are lists, integers, or strings will be overwritten by your repo config.
A common example of this is `overrides`.

```yaml
# Template YAML
version: 3
overrides:
- <template override>
```

```yaml
# Repo YAML
version: 3
extends: <template url>
overrides:
- <repo override>
```

```yaml
# Merged YAML
version: 3
extends: <template url>
overrides:
- <repo override>
```
