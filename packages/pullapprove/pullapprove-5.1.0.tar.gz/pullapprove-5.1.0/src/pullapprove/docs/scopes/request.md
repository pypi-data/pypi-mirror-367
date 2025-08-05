---
title: Request
---

# `request`

Once a change is opened as a pull request, PullApprove will automatically `request` reviewers for each scope that matches the files in the PR.

```toml
[[scopes]]
name = "app"
reviewers = ["dev1", "dev2"]
request = 1
```

Behavior:

- The reviewer will be chosen at random (using the PR number as a seed).
- If `require` > `request`, more requests will be sent as approvals come in.
- If eligible reviewers are already assigned to the PR (either manually or by a preceding scope), then additional reviewers won't be requested.
- Wildcard (`*`) reviewers are never auto-requested
- With mixed reviewers like `reviewers = ["alice", "bob", "*"]`, only alice and bob will be auto-requested
