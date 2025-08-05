## Migrating from CODEOWNERS to PullApprove

The user has an existing CODEOWNERS file and wants to migrate to PullApprove.

**Goal**: Create a 1:1 migration preserving exact CODEOWNERS behavior. Enhancements only if requested.

### Your Task

1. Read CODEOWNERS and identify all path patterns and owners
2. Convert each CODEOWNERS entry to a PullApprove scope:
   - Keep exact paths and owners
   - Use `require = 1` (CODEOWNERS default)
   - Preserve path ordering
3. Create CODEREVIEW.toml with the migrated configuration
4. Validate with `pullapprove check`

Example:
```
# CODEOWNERS:
/backend/ @backend-team
*.js @frontend-team
```

Becomes:
```toml
[[scopes]]
name = "backend"
paths = ["backend/**/*"]
reviewers = ["@backend-team"]

[[scopes]]
name = "javascript"
paths = ["**/*.js"]
reviewers = ["@frontend-team"]
```

Note: PullApprove respects GitHub teams (@org/team syntax). Individual users don't need @ prefix. CODEOWNERS patterns may need minor adjustments for TOML glob syntax.
