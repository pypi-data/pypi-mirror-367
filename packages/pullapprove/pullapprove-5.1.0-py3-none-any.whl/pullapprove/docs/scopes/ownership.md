---
title: Ownership
---

# `ownership`

When matching a file to scopes, the default behavior is to only apply the last matching scope (remember, scopes are defined in order). This is most similar to how CODEOWNERS typically work.

The default value for `ownership` is an empty string (`""`), which means the last matched scope is the owner.

PullApprove has two other modes of file ownership:

- `append` - Establish joint-ownership of a file by appending this scope to any future matching scopes.
- `global` - Allow this scope to approve on behalf of any future matching scopes.



## `append`

With appended ownership, **each matching scope is required to approve the PR**.

```toml
[[scopes]]
name = "dependencies"
ownership = "append"
paths = ["**/*/package.json"]

[[scopes]]
name = "app"
paths = ["app/**/*"]
```

```console
$ git diff --name-only
app/package.json

$ pullapprove files --diff
app/package.json -> app dependencies
```

## `global`

With global ownership, **the global scope can approve the PR which overrides the status of the primary matched scope**. If a global scope uses `request`, the requests will only be sent if no other scopes match the file.

```toml
[[scopes]]
name = "global"
ownership = "global"
paths = ["**/*"]

[[scopes]]
name = "app"
paths = ["app/**/*"]
```

```console
$ git diff --name-only
app/package.json

$ pullapprove files --diff
app/package.json -> app ^global
```
