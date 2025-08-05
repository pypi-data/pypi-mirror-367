## Migrating from PullApprove v3 to v5

The user has an existing `.pullapprove.yml` (v3) configuration to migrate to v5 format.

**Goal**: Preserve existing functionality. Only note where features cannot be migrated.

### Key Differences

- **Format**: v3 YAML → v5 TOML
- **Structure**: v3 "groups" → v5 "scopes"
- **Teams**: v3 allows GitHub teams, v5 requires individual usernames (use `gh` to resolve)
- **Draft PRs**: v5 automatically skips drafts (no config needed)

### Features Without Direct Migration

- **Overrides**: No direct v5 equivalent in some cases
- **Complex conditions**: v3 Python expressions → v5 path/code/author matching only
- **Optional groups**: v3 `type: optional` → v5 `ownership = "global"`
- **Reviewers without requests**: v3 `~username` → v5 `alternates = ["username"]`

### Your Task

1. **Read v3 capabilities first**: Run `pullapprove docs --v3` to verify feature availability
1. **Check v5 capabilities first**: Run `pullapprove docs` to verify feature availability
2. **Read v3 config**: Analyze groups, conditions, and review rules
3. **Map to v5**:
   - Groups → Scopes
   - Conditions → paths/code/authors fields
   - Review requirements → require/request
   - Teams → Resolve to usernames or leave TODO comments
4. **Validate**: Run `pullapprove check` on migrated config

### Common Migration Patterns

```yaml
# v3 basic group
groups:
  backend:
    conditions: ["*.py in files"]
    reviewers:
      users: [alice, bob]
    reviews:
      required: 2
```
→
```toml
# v5 scope
[[scopes]]
name = "backend"
paths = ["**/*.py"]
reviewers = ["alice", "bob"]
require = 2
```

```yaml
# v3 with teams and optional reviewers
groups:
  frontend:
    reviewers:
      teams: [frontend-team]
      users: [dev1, ~admin1]
    reviews:
      required: 1
```
→
```toml
# v5 with resolved teams
[[scopes]]
name = "frontend"
reviewers = ["dev1", "team_member1", "team_member2"]  # Teams expanded
alternates = ["admin1"]  # ~ prefix → alternates
require = 1
```

```yaml
# v3 optional group
groups:
  docs:
    conditions: ["*.md in files"]
    reviewers:
      users: [writer]
    reviews:
      required: 0
```
→
```toml
# v5 optional scope
[[scopes]]
name = "docs"
paths = ["**/*.md"]
reviewers = ["writer"]
ownership = "optional"
require = 1
```

**Important**: Many v3 features exist in v5 with the same names (author_value, reviewed_for, labels). Always check `pullapprove docs` before claiming incompatibility.
