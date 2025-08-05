## Fixing Configuration Errors

The user's PullApprove configuration has validation errors.

### Your Task

1. Run `pullapprove check` to identify validation errors
2. Read the existing configuration
3. **Fix ONLY the errors** - preserve all other behavior and intent
4. Re-validate after fixing

Common errors: TOML syntax, missing required fields, invalid values, circular references, invalid reviewers.

**Critical**: Make minimal changes. Do NOT add features, optimize, or redesign. Fix only what's broken.

Reference `pullapprove docs` for correct syntax.