---
title: Availability
description: Manage code reviewer availability directly or in a separate JSON file
template: config/field.template.html
plan_required: true
---

# Availability

When people are out of the office or away from work for an extended period of time,
the `availability` setting allows you to remove them from the review process.

When a reviewer is "unavailable",
they won't receive review requests.
If they were already requested to review a PR,
those requests will be removed if the PR is updated while they are gone.

Availability can be set directly in your `.pullapprove.yml`:

```yaml
version: 3
availability:
  users_unavailable:
  - reviewer1
  - reviewer2
```

## Loading availability settings with `extends`

Use `extends` to load availability data from a separate repo or URL ([more detail here](/config/extends/)).
This way you can manage availability in a centralized location, and share that information across your repos.

```yaml
version: 3
availability:
  extends: "yourorg/pullapprove:availability.json"

  # JSON follows the same structure as YAML:
  # {
  #   "users_unavailable": [
  #     "reviewer1",
  #     "reviewer2"
  #   ]
  # }
```

**With `extends`, you can think of your organization's availability schedule as an API.**
Most teams have a convention for showing when you're away from work (Google Calendar, status on Slack, etc.) and you can incorporate that into your code review process with a custom integration through `extends`.

### Updating a file in a repo

When you point to a file in another repo, you don't have to worry about hosting or authentication/authorization because GitHub and PullApprove already work together.

Periodically updating a file via GitHub Actions is one way to manage availability for your organization.
A script can daily/hourly and commit any changes back to your repo for PullApprove to load.

An example of this is built in to the dropseed/pullapprove GitHub Action,
which uses GitHub Issues as a lightweight calendar.
Each issue uses a title in the form of `@user unavailable from <date> to <date>` which gets parsed when the action runs to determine who is away at any given time.
That list of users is committed to a JSON file in the repo,
which PullApprove can then load.

One advantage of using GitHub Issues for this is that you can easily set someone else as "unavailable" if they forgot to do it themselves.

[![Managing code reviewer availability through GitHub Issues](/assets/img/screenshots/availability-issue.png)](/assets/img/screenshots/availability-issue.png)

Here is an example `.github/workflows/pullapprove-availability.yml`:

```yaml
name: pullapprove-availability

on:
  workflow_dispatch: {}
  schedule:
  - cron: "0 */6 * * *"
  issues:
    types: [opened, edited, closed]

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - uses: dropseed/pullapprove@v3
      with:
        cmd: availability sync-issues availability.json
        github_token: ${{ secrets.GITHUB_TOKEN }}
    # and/or custom scripts to further modify availability.json
```

### Hosting an HTTP endpoint

If you point `extends` to a URL (ex. `extends: https://internal.yourorg.com/availability/`) then you could host an endpoint which integrates with any external services and returns a simple "here's who is unavailable" JSON response.

Here's a simplified example in Python:

```python
from flask import Flask
app = Flask(__name__)

@app.route('/availability/')
def availability():
    users_unavailable = []
    users_unavailable += get_unavailable_users_from_google_calendar()
    users_unavailable += get_unavailable_users_from_slack()
    return {
      "users_unavailable": users_unavailable,
    }
```

We would strongly recommened you implement some kind of caching,
as this could get a lot of traffic depending on your GitHub activity.
