---
title: Code
---

# `code`

Scopes can also be matched to code changes within files. This uses the `git diff` output and includes the surrounding context (i.e. on GitHub this is 3 lines above and below the changed line).

```toml
[[scopes]]
name = "security"
paths = ["**/*.py"]
code = [
    # To match lines added or removed in the diff,
    # use `^(\+|-)` at the start of the regex.
    "^(\+|-).*@csrf_exempt.*",
]
```

```console
$ git diff app/views.py
- @csrf_exempt
+ @csrf_protect

$ pullapprove files --diff
app/views.py:L10 -> security
```

You can also use aliases in the `code` patterns to reference predefined patterns or groups of patterns.
