---
title: Reviewed-for
---

# `reviewed-for`

The `reviewed_for` setting controls how reviews are counted based on the presence of `Reviewed-for: <scope_name>` syntax in review comments. This setting helps ensure reviewers are explicit about which aspects of a PR they've reviewed.

## Options

### `"required"`

With `reviewed_for = "required"`, a review only counts if the review body contains a `Reviewed-for: <scope_name>` line. This forces users to be explicit about what they are reviewing the PR for.

A common use case for this is with high-level `global` ownership scopes that can approve any change in the repo. Adding `reviewed-for` to this scope can prevent accidental approvals during regular reviews, if the reviewers are involved in multiple scopes.

### `"ignored"`

With `reviewed_for = "ignored"`, reviews always count for the scope regardless of whether reviewers use the `Reviewed-for: <scope_name>` syntax. This is the opposite of `"required"`.

This option is useful for:
- Ensuring critical scopes are always reviewed, even if reviewers forget to use the `Reviewed-for` syntax
- Setting minimum review requirements that apply across all workflows
- Groups that should always be included in the review process

```toml
[[scopes]]
name = "global"
paths = ["*"]
reviewers = ["admin1"]
reviewed_for = "required"
ownership = "global"

[[scopes]]
name = "design"
paths = ["*.css"]
reviewers = ["admin1"]
```

<!-- universal cli? no comments though in gitlab/bb so you have to look for comment too? -->
<!-- can validate Reviewed-for pre-submit -->

<!-- $ git review submit --state approved --body "Looks good" --reviewed-for global -->
