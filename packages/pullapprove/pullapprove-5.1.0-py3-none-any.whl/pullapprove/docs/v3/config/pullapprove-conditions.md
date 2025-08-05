---
title: PullApprove Conditions
description: Custom rules for deciding when review needs to happen
template: config/field.template.html
---

# PullApprove Conditions

<div class="flex items-center p-4 my-4 text-yellow-800 bg-yellow-100 border border-yellow-200 rounded">
  <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 mr-2" viewBox="0 0 20 20" fill="currentColor">
  <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
</svg>
</svg>
  <div>
    This setting is deprecated in favor of <a href="/config/overrides/" class="underline">overrides</a>.
  </div>
</div>

Write [expressions](/expressions/) to decide which PRs get reviewed and when the review starts.

By default there are no `pullapprove_conditions` and every PR is eligible for review according to your [groups](/config/groups/).

When you use `pullapprove_conditions` to disable review, by default you will see a "success" status in GitHub.

```yaml
version: 3
pullapprove_conditions:
- "'WIP' not in title"  # only review if not marked as work in progress
- "base.ref == 'master'"  # only review things being merged into master
- "'*travis*' in statuses.successful"  # only review if tests have already passed
- "'hotfix' not in labels"  # let hotfix PRs go through without review

# review groups are only evaluated if all of the pullapprove_conditions are true
groups:
  ...
```

![Success status from pullapprove when conditions are not met](/assets/img/screenshots/pullapprove-condition-success.png)

## Blocking PRs

Depending on your condition,
you may want to set the status to "pending" or "failure" when a condition is unmet.
If PullApprove is a required status check on your repo,
this will block a PR from being merged.

You can also write a custom explanation to provide more information directly in the GitHub interface.

> Note that the conditions are evaluated in order,
  and the first one to fail will set the status and explanation.

```yaml
version: 3
pullapprove_conditions:
- condition: "base.ref == 'master'"
  unmet_status: success
  explanation: "Review not required unless merging to master"
- "'hotfix' not in labels"  # when using the string type, the default status is "success"
- condition: "'WIP' not in title"
  unmet_status: pending
  explanation: "Work in progress"
- condition: "'*travis*' in statuses.successful"
  unmet_status: failure
  explanation: "Tests must pass before review starts"

# review groups are only evaluated if all of the pullapprove_conditions are true
groups:
  ...
```

![Pending status for WIP pull request from pullapprove when conditions are not met](/assets/img/screenshots/pullapprove-condition-pending.png)
