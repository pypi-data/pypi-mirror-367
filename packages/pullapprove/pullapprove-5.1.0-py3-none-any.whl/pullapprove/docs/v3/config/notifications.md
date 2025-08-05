---
title: Notifications
description: Automated PR comments as a part of your review workflow
template: config/field.template.html
gitlab: false
bitbucket: true
next:
  url: /config/groups/
  title: Set up your groups
prev:
  url: /config/pullapprove-conditions/
  title: Enable or disable PullApprove
---

# Notifications

Use automated PR comments to help guide users through your review process.
These can be used to communicate your process to contributors and first-timers, instruct reviewers, or boost morale 🎉.

Notifications are triggered by "events".
These events include many of the GitHub/Bitbucket webhooks,
but also a few events from PullApprove itself.

## Example

```yaml
version: 3
notifications:
- when: pull_request.opened
  comment: |
    Hey @{{ author }}, thanks for the PR! The review will start once
    the tests and CI checks have passed. You'll also need to sign our
    CLA if you haven't before.
- when: pullapprove.approved
  if: "author_association == 'CONTRIBUTOR'"
  comment: "The review is completed. Thanks @{{ author }}, we'll take it from here."

groups:
  ...
```

![Pull request automated review comment from PullApprove](/assets/img/screenshots/opening-comment.png)

## Events

The following events can be used for the `when` field.

### PullApprove events

- **pullapprove.started** - the first time that PullApprove sends a "pending" status for the PR (e.g. groups have been activated)
- **pullapprove.approved** - when there are active groups, and they have all approved the PR
- **pullapprove.group.requested_reviewers** - when review requests are created by PullApprove, comes with `event.group` and `event.requested_reviewers`
- **pullapprove.group.unrequested_reviewers** - when review requests are removed by PullApprove, comes with `event.group` and `event.unrequested_reviewers`

```yaml
notifications:
- when: pullapprove.group.requested_reviewers
  comment: |
    {{ event.group }} review requested from {{ text_list(event.requested_reviewers.mentions, "and") }}
```

### GitHub events

When [filtering events](#filtering-with-if) or writing comment templates,
GitHub events come with additional data from the GitHub webhook itself.
This data will be available in the `event` object and would contain things like `event.sender` or `event.review.body`.
[Check the GitHub docs for up-to-date examples of what data these webhooks come with.](https://docs.github.com/webhooks/event-payloads/)

```yaml
notifications:
- when: pull_request.edited
  comment: "@{{ event.sender }} edited this PR."
```

- **pull_request_review_comment.created**
- **pull_request_review_comment.deleted**
- **pull_request_review_comment.edited**
- **pull_request_review.dismissed**
- **pull_request_review.edited**
- **pull_request_review.submitted**
- **pull_request.assigned**
- **pull_request.converted_to_draft**
- **pull_request.edited**
- **pull_request.labeled**
- **pull_request.locked**
- **pull_request.opened**
- **pull_request.ready_for_review**
- **pull_request.reopened**
- **pull_request.review_request_removed**
- **pull_request.synchronize**
- **pull_request.unassigned**
- **pull_request.unlabeled**
- **check_run.completed**
- **check_run.created**
- **status**

### Bitbucket events

More information about the Bitbucket webhook payloads can be found [here](https://support.atlassian.com/bitbucket-cloud/docs/event-payloads/).

```yaml
notifications:
- when: "pullrequest:updated"
  comment: "{{ event.actor }} updated this PR."
```

- **repo:push**
- **repo:commit_status_created**
- **repo:commit_status_updated**
- **pullrequest:created**
- **pullrequest:updated**
- **pullrequest:approved**
- **pullrequest:unapproved**
- **pullrequest:changes_request_created**
- **pullrequest:changes_request_removed**

### GitLab events

*Notifications are not yet enabled for the GitLab beta.*

## Filtering with "if"

You can filter out events based on the state of the PR by adding an
`if` condition. This is written using the [expressions syntax](/expressions/) but you also have access to the `event` object.

```yaml
notifications:
- when: pullapprove.approved
  if: "author_association == 'CONTRIBUTOR'"
  comment: The review is completed. Thanks @{{ author }}, we'll take it from here.
```

## Updating existing comments

Use `comment_behavior: create_or_update` to keep an updated "status" comment on the PR. Note that when a comment is updated, it won't trigger notifications to people on the PR.

```yaml
notifications:
- when: pull_request_review.submitted
  comment_behavior: create_or_update
  comment: >
    {% if groups.pending -%}
    This PR still needs to be approved by {{ text_list(groups.pending, 'and') }}
    {%- else -%}
    No review groups pending.
    {%- endif %}
```

## Combining events

The `when` field can also be a list of events. This is particularly useful when using `comment_behavior: create_or_update` since a single comment can be updated by multiple events. Just note that each event may have a different context, so be sure that the variables you use in `if` or `comment` are available in all events.

```yaml
notifications:
- when: [pull_request.opened, pull_request.reopened]
  comment_behavior: create_or_update
  comment: >
    {% if event.pull_request.draft -%}
    This PR is a draft and won't be reviewed yet.
    {%- else -%}
    This PR is ready for review.
    {%- endif %}
```
