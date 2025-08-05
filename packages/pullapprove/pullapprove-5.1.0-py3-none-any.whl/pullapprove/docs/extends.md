---
title: Extends
---

# `extends`

In large codebases, it can be useful to split your code review configuration up and keep it close to the code it applies to. PullApprove supports this by allowing multiple `CODEREVIEW.toml` files in the repo.

```console
$ tree
.
├── app
│   ├── CODEREVIEW.toml
│   └── package.json
├── docs
│   ├── CODEREVIEW.toml
│   └── README.md
└── CODEREVIEW.toml
```

When a file is modified, the closest `CODEREVIEW.toml` file is used to evaluate the scopes for that file.

By default, each `CODEREVIEW.toml` completely resets the configuration for the files in its directory and subdirectories. To build on the configuration of a parent `CODEREVIEW.toml`, use the `extends` setting to explicitly include the parent configuration.

```toml
# app/CODEREVIEW.toml
extends = ["../CODEREVIEW.toml"]

[[scopes]]
# ...
```

The `extends` path can be relative or repo-absolute. A `/` will point to the root of the repo.

```toml
# app/CODEREVIEW.toml
extends = ["/CODEREVIEW.toml"]

[[scopes]]
# ...
```

If the extended file is used purely as a template for other `CODEREVIEW.toml` files, you can mark it as a template to prevent it from being evaluated on its own. This also evaluates any paths as relative to the child file, instead of where the template was originally located.

```toml
# .codereview/base.toml
template = true

[[scopes]]
# ...
```

While this can feel a bit verbose at times, it also makes it very clear how an individual `CODEREVIEW.toml` file will behave. The included CLI commands can help inspect and manage your overall configuration if you need to make large-scale changes.

Unlike some versions of PullApprove, this version of `extends` can not load a configuration from a URL. This is to keep the configuration explicit, auditable, and close to the code it applies to. To share generic configuration across multiple repos, you can [use the admin UI to create and sync templates](#templates).

> Note that a root `CODEREVIEW.toml` *must* exist for PullApprove to be enabled. It can be empty, which is unlikely, but it must exist.
