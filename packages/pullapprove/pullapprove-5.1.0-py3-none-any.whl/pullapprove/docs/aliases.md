---
title: Aliases
---

# `aliases`

Reviewer aliases can be defined at the root of the `CODEREVIEW.toml` file. These aliases can be used anywhere a list of strings is expected, such as `reviewers`, `alternates`, `authors`, `cc`, or `labels`.

To reference an alias, use the `$` prefix.

```toml
[aliases]
devs = ["dev1", "dev2", "dev3", "dev4"]

[[scopes]]
name = "app"
reviewers = ["$devs"]
```

## Nested aliases

Aliases can reference other aliases, allowing you to build complex reviewer groups:

```toml
[aliases]
backend = ["alice", "bob"]
frontend = ["carol", "dave"]
qa = ["eve"]
all_devs = ["$backend", "$frontend"]
everyone = ["$all_devs", "$qa", "frank"]

[[scopes]]
name = "app"
reviewers = ["$everyone"]
# Expands to: ["alice", "bob", "carol", "dave", "eve", "frank"]
```

PullApprove will raise an error if it detects circular references in aliases (e.g., if alias A references B, and B references A). This helps catch configuration mistakes early.

To manage `aliases` at scale across your organization, you can make use of [templates]({{ url('pages:admin/templates') }}) to sync the same `aliases` to multiple repos.

## FAQs

### Why not sync with GitHub Teams?

PullApprove doesn't sync directly with GitHub Teams, GitLab Groups, or Bitbucket Groups, because the membership of those lists are not easily visible or auditable along with the rest of the configuration.

Locally referencing these lists also reduces API usage, which is important for running a rate-limited integration at enterprise-scale.

The term `aliases` was inspired by [Kubernetes OWNERS](https://www.kubernetes.dev/docs/guide/owners/#owners_aliases), which uses the same concept.
