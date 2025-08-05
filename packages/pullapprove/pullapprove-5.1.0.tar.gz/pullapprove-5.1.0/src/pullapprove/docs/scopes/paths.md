---
title: Paths
---

# `paths`

Files are matched to scopes using glob patterns.

The glob patterns are case-insensitive, and use:

- `*` to match any number of characters except `/`
- `**` to match any number of characters including `/`
- `?` to match a single character
- `[...]` to match a range of characters
- `[!...]` to match any character not in the range
- `\` to escape special characters
- `{...,...}` to match any of the comma-separated patterns
- `!` at the start to exclude paths (negate pattern)

The patterns should never start with a `/`, as they are always matched against the relative path of the `CODEREVIEW.toml` file.

## Excluding Paths

You can exclude specific paths from a scope by prefixing the pattern with `!`:

```toml
[[scopes]]
name = "backend"
paths = ["backend/**/*", "!backend/tests/**/*", "!backend/**/*.test.py"]
```

This will match all files in the `backend/` directory except for files in the `tests/` subdirectory and files ending with `.test.py`.

```toml
[[scopes]]
name = "app"
paths = ["app/**/*"]

[[scopes]]
name = "docs"
paths = ["docs/**/*", "**/*.md"]
```

```console
$ git diff --name-only
app/INSTRUCTIONS.md
app/package.json
docs/README.md

$ pullapprove files --diff
app/INSTRUCTIONS.md -> docs
app/package.json -> app
docs/README.md -> docs
```

## Example with Exclusions

```toml
[[scopes]]
name = "source-code"
paths = ["src/**/*", "!src/**/*.test.js", "!src/**/__tests__/**/*"]

[[scopes]]
name = "tests"
paths = ["src/**/*.test.js", "src/**/__tests__/**/*"]
```

```console
$ git diff --name-only
src/utils/helper.js
src/utils/helper.test.js
src/components/__tests__/Button.js

$ pullapprove files --diff
src/utils/helper.js -> source-code
src/utils/helper.test.js -> tests
src/components/__tests__/Button.js -> tests
```

Note that when files are renamed or moved, both the old and new paths will be used for scope matching.

```console
$ git diff --name-status
R100    app/README.md    docs/README.md

$ pullapprove files --diff
app/README.md -> app
docs/README.md -> docs
```
