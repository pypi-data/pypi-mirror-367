## Creating a New PullApprove Configuration

The user needs help setting up PullApprove for the first time.

### Your Task

1. Explore repository structure to identify key directories and file types
2. Use tools like `git blame` to find active contributors for different parts of the codebase
3. Ask about team size and review workflow needs
4. Create a simple CODEREVIEW.toml with:
   - Clear scope names matching codebase structure
   - Reasonable review requirements
   - Comments explaining each section
5. Validate with `pullapprove check`

Start simple. Use wildcards like `**/*.py` for file patterns. Consider a catch-all scope for uncategorized files.
