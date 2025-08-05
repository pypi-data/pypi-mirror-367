---
title: Reviews
description: Decide how many approvals are required and when review requests are sent
template: config/field.template.html
next:
  url: /config/type/
  title: Group type
prev:
  url: /config/reviewers/
  title: Choose reviewers
---

# Reviews

Settings for how review requests are sent, and how many approvals are required.

```yaml
version: 3
groups:
  code:
    reviews:
      # 3 approvals from this group are required
      required: 3
      # 1 review request will be sent at a time
      request: 1
      # reviewers will be chosen in a random order
      request_order: shuffle
      # if the PR author is in this group, automatically add +1
      author_value: 1
      # decide whether reviews have to use the "Reviewed-for:" syntax to qualify for this group
      reviewed_for: optional
```

## Fields

### `required`

The number of people who need to approve a PR.
The default is `required: 1`.

If `required: -1`, then all users in the group will be required.

### `request`

The number of people who should be requested for review at any given time.

For example, if `request: 1` then 1 review request will be sent at a time until the number of `required` approvals are met.

If `request` is omitted then it will default to the number `required`.
This way it will automatically send out the number of requests that are needed to approve the PR.

If `request: -1` then review requests will be sent *every* reviewer in the group.

### `request_order`

Use `shuffle` (or `random`) to have reviewers selected randomly from the group. This is the default setting.

Use `given` to request reviewers in the order specified by your config.
This works best when using `reviewers.users`,
but it can also work with `reviewers.teams` (the order inside each team is determined by the GitHub API).

```yaml
version: 3
groups:
  code:
    reviews:
      required: 1
      request: 1
      request_order: given

    reviewers:
      users:
      - typicalreviewer
      - fallbackreviewer1
      - fallbackreviewer2
```

### `author_value`

If the author of the PR is in this group, then `author_value` will be added to the review "score". By default `author_value: 0`.

Set `author_value: 1` to effectively have the PR be "approved" by the author -- this will mean 1 less person from the group will have to approve to meet the number `required`.

```yaml
version: 3
groups:
  code:
    reviews:
      # only 2 approvals required if author is in this group
      required: 3
      author_value: 1

  code:
    reviews:
      # only 1 approval required if author is in this group
      required: 3
      author_value: 2

  code:
    reviews:
      # no approval required if author is in this group
      required: 3
      author_value: 3
```

To require *more* reviews if the author is in the group, then use a negative number.
For example, `author_value: -2` would require an additional 2 approvals from this group.
This might be useful if you want to ensure that any PR that this group "owns" gets more reviews than they usually do.
For example, if the "security" team needs to give extra attention to their own PRs.

```yaml
version: 3
groups:
  security:
    reviews:
      # 4 approvals will be required if the author is in the security group
      required: 3
      author_value: -1
```

*Note that on GitHub, authors can't actually review their own PR.*

### `reviewed_for`

Control the behavior or the ["Reviewed-for" syntax](/reviewing/).

![](/assets/img/screenshots/reviewed-for-approve.png)

There are three options: `optional` (default), `required`, and `ignored`

```yaml
version: 3
groups:
  security:
    reviews:
      # review body will have to contain "Reviewed-for: security" to count towards this group
      reviewed_for: required
```

#### `optional`

A review will apply to a group if it is specified in "Reviewed-for",
or if "Reviewed-for" is not used at all in the body of the review.


#### `required`

> This feature is available on the [business and organization plans](https://www.pullapprove.com/pricing/).

Reviews *must* specify the group using "Reviewed-for".

This can help with situations where a single person is involved in multiple active groups,
by forcing them to say which group they are reviewing for and preventing accidental overlapping reviews.

#### `ignored`

> This feature is available on the [business and organization plans](https://www.pullapprove.com/pricing/).

A review will always apply to the group,
regardless of how "Reviewed-for" is used.

This can be used if you have groups that should *always* apply,
but sometimes get forgotten if "Reviewed-for" is a part of the workflow for other groups.
An example of this would be setting a required number of approvals across your entire workflow:

```yaml
version: 3
groups:
  min-reviews-required:
    reviews:
      reviewed_for: ignored
      request: 0
      required: 3
```
