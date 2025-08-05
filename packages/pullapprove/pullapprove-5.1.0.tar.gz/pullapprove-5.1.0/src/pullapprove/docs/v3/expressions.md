---
title: Expressions
description: Custom rules for deciding who needs to review which PRs
template: markdown_page.template.html
---

# Expressions

PullApprove expressions allow you to write powerful, custom rules to design your workflow.

Expressions are evaluated in a Python environment, using the [provided functions and variables](/context/).
You can use human-readable operators like "in", "not in", "and", and, "or".

The same syntax powers the [group conditions](/config/conditions/),
[overrides](/config/overrides/),
and [notification filters](/config/notifications/).

## Single vs multi-line

Most basic expressions can be written in a single line.
In YAML,
you'll typically want to surround these with single-quotes since you'll have double-quotes inside (or vice versa):

```yaml
version: 3
groups:
  api:
    conditions:
    - '"API" in title'
```

When you're comparing lots of values,
it may be easier to [write the expression over multiple lines](https://yaml-multiline.info/) using the `>` syntax:

```yaml
version: 3
overrides:
- if: >
    not contains_any_fnmatches(files, [
      "packages/*",
      "apps/*",
      "docs/*",
      ])
  status: success
```

## Examples

You can apply the same basic operations to most of the data we make available.
Here are some common examples of how to use the [available functions and variables](/context/).

### Files

Basic string comparisons will use [fnmatch](https://docs.python.org/3/library/fnmatch.html) under the hood.

```python
# (GitHub)
"*.js" in files or "frontend/*" in files
```

```python
# (Bitbucket)
"*.js" in diffstat or "frontend/*" in diffstat
```

You can also use the `contains_any_fnmatch` function to check more paths at once without writing lots of "or" lines.

```python
# (GitHub)
contains_any_fnmatches(files, [
    "packages/*",
    "apps/*",
    "docs/*",
    ])
```

```python
# (Bitbucket)
contains_any_fnmatches(diffstat, [
    "packages/*",
    "apps/*",
    "docs/*",
    ])
```

Or globs using `contains_any_globs`:

```python
# (GitHub)
contains_any_globs(files, [
    "packages/animations/**",
    "packages/platform-browser/animations/**",
    "aio/content/guide/animations.md",
    "aio/content/examples/animations/**",
    "aio/content/images/guide/animations/**",
    "aio/content/guide/complex-animation-sequences.md",
    "aio/content/guide/reusable-animations.md",
    "aio/content/guide/route-animations.md",
    "aio/content/guide/transition-and-triggers.md",
    ])
```

```python
# (Bitbucket)
contains_any_globs(diffstat, [
    "packages/animations/**",
    "packages/platform-browser/animations/**",
    "aio/content/guide/animations.md",
    "aio/content/examples/animations/**",
    "aio/content/images/guide/animations/**",
    "aio/content/guide/complex-animation-sequences.md",
    "aio/content/guide/reusable-animations.md",
    "aio/content/guide/route-animations.md",
    "aio/content/guide/transition-and-triggers.md",
    ])
```

Or a `glob()` instance:

```python
# (GitHub)
glob("packages/**/*.js") in files
```

```python
# (Bitbucket)
glob("packages/**/*.js") in diffstat
```

You can also chain the `include` and `exclude` methods to further filter down a list of files:

```python
# (GitHub)
files.include("src/*").exclude("*.md")
```

```python
# (Bitbucket)
diffstat.include("src/*").exclude("*.md")
```

### Branches

Use branch variables to enable review depending on PR branch names or where it's being merged into:

```python
# (GitHub)
# Reference a hardcoded branch name
base.ref == "master"

# Or another variable
base.ref != base.repo.default_branch

# Or use the standard comparision operators
"feature/" in head.ref
```

```python
# (GitLab)
# Reference a hardcoded branch name
target_branch == "master"

# Or use the standard comparision operators
"feature/" in source_branch
```

```python
# (Bitbucket)
# Reference a hardcoded branch name
destination.branch_name == "master"

# Or another variable
destination.branch_name != destination.repository.mainbranch.name

# Or use the standard comparision operators
"feature/" in source.branch_name
```

### Labels

```python
# (GitHub)
# Standard strings
"bug" in labels

# String patterns (fnmatch)
"sig-*" in labels

# Regular expressions
regex('.*/app') in labels
```

```python
# (GitLab)
# Standard strings
"bug" in labels

# String patterns (fnmatch)
"sig-*" in labels

# Regular expressions
regex('.*/app') in labels
```

### Other PullApprove groups

Use the state of preceding groups (above the current group in your config).

```python
# (All platforms)
# Use list operators
len(groups.approved) > 3

# Or basic logic by name
"admins" in groups.passing
```

### Checks and statuses

The "checks" on a PR come in two forms:
the [Checks API](https://docs.github.com/en/free-pro-team@latest/rest/reference/checks),
and the commit [Statuses API](https://docs.github.com/en/free-pro-team@latest/rest/reference/repos#statuses).

The GitHub interface often combines these, making it hard to tell the difference.
The best way to tell the difference is to look for the Checks tab on a PR page.
For anything on that page (like GitHub Actions/Workflows), use the `check_runs` object.
If you have a status that is not on that page, it will be found in `statuses`.

![GitHub pull request "Checks" tab](/assets/img/screenshots/github-pr-checks-tab.png)

#### Checks

```python
# (GitHub)
"build" not in check_runs.failed
```

#### Statuses

```python
# (GitHub)
"*travis*" in statuses.succeeded
```

```python
# (Bitbucket)
"*travis*" in statuses.successful
```

### Title

```python
# (All platforms)
# Use basic string comparisions
"WIP" in title

# Or fnmatch
"WIP*" in title

# Or regular expressions
regex("WIP: .*") in title
```

### Body/description

```python
# (GitHub)
"needs review" in body
```

```python
# (GitLab)
"needs review" in description
```

```python
# (Bitbucket)
"needs review" in description
```

### Size

```python
# (GitHub)
changed_files > 30
```

```python
# (Bitbucket)
len(diffstat.paths) > 30
```

### Author

```python
# (All platforms)
author in ["internA", "internB"]
```

GitHub also has an `author_association` variable which can be used ([check possible values here](https://docs.github.com/en/graphql/reference/enums#commentauthorassociation)):

```python
# (GitHub)
author_association == "FIRST_TIME_CONTRIBUTOR"
```

```python
# (GitLab)
first_contribution
```

### Mergeability

```python
# (GitHub)
not mergeable
```

```python
# (GitLab)
# https://docs.gitlab.com/ee/api/merge_requests.html#single-merge-request-response-notes
merge_status == "can_be_merged"
```

### Git diff and files changed

```python
# (GitHub)
contains_fnmatch(files.lines_added, '*dangerouslySetInnerHTML*')
```

```python
# (GitLab)
contains_fnmatch(diff.lines_added, '*dangerouslySetInnerHTML*')
```

```python
# (Bitbucket)
contains_fnmatch(diff.lines_added, '*dangerouslySetInnerHTML*')
```

### Dates

```python
# (GitHub)
created_at < date('3 days ago')
```

```python
# (Bitbucket)
created_on < date('3 days ago')
```
