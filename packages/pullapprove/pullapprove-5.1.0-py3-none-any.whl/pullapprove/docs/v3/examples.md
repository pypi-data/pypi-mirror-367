---
title: Examples
description: Common code review workflows built with PullApprove
template: markdown_page.template.html
---

# Code review workflow examples

## Spreading the review workload

If you have a large team and want everyone to be involved in code review, randomly assigning reviewers
can be an easy way to distribute the work.

The following config will randomly choose 2 reviewers for each new pull request.
```yaml
version: 3
groups:
  code-review:
    reviewers:
      teams:
      - everybody
    reviews:
      request: 2
      request_order: random
```

## Reviewing process changes

In organizations where code review plays a vital role in security and
business operations, you will likely want to restrict changes to the
review process itself.

In PullApprove, you can create a review group specifically for the config file
to ensure no changes are made without an admin's approval.

```yaml
version: 3
groups:
  pullapprove:
    conditions:
    - "'.pullapprove.yml' in files"
    reviewers:
      teams:
      - admins
    reviews:
      required: 1
```

## Assigning reviewers based on labels

Labels can be a great, visual indicator of which topics a pull request covers or
which phase of review it is in.

You can use the `labels` variable when writing conditions to automatically
assign reviewers based on how the author or other collaborators label the PR.

This can be especially useful for situations where names of the files changed
don't give you enough insight into what *kind* of change is actually being made
(e.g. is modifying a "*.js" file in React a design tweak or a new feature?).

```yaml
version: 3
groups:
  design:
    conditions:
    - "'ui/ux' in labels"
    reviewers:
      teams:
      - design
```

## Instructing first-time contributors

Setting expectations is important when someone opens their first pull request.
They should know what is expected of them, and what they can expect to see during the review process.

A well-written automated comment can go a long way in giving the contributor a sense of
what will happen, and removing some of the burden from the maintainers/admins.

```yaml
version: 3
notifications:
- when: pull_request.opened
  if: "author_association == 'FIRST_TIME_CONTRIBUTOR'"
  comment: |
    Hey @{{ author }}, thanks for the PR! The review will start once
    the tests and CI checks have passed. If they don't, please review
    the logs and try to fix the issues (ask for help if you can't
    figure it out). A reviewer will be assigned once the tests are
    passing and they'll walk you through getting the PR finished
    and merged.
groups:
  ...
```

## Bypassing review for emergencies

Sometimes you need to provide a way for people to skip review entirely.
Depending on your situation, this could be a "hotfix" or a "break glass" situation.
You can use [`overrides`](/config/overrides/) to disable PullApprove (with a success status) but remember that you're trusting people will use it for emergencies only.

Labels are one way to disable PullApprove for emergencies (remember: anyone who can change labels, can disable PullApprove).

```yaml
version: 3
overrides:
- if: "'emergency' in labels"
  status: success
  explanation: "Review disabled with the emergency label"
```

For this to work, "pullapprove" should be a required status check but you should not enable GitHub's minimum reviews requirement.

## Skipping review on certain branches

If your workflow involves frequently opening PRs to merge
into a "development" or "staging" branch, you likely don't
want it to go through the same review process as merging to
"production" or "master".

You can use conditions on either the base *or* head branch
details to decide which process to use.

### Skip review entirely

```yaml
version: 3
overrides:
- if: "base.ref != 'master'"
  status: success
  explanation: "Review not required unless merging to master"
```

### Set up separate review groups based on branches

```yaml
version: 3
groups:
  staging:
    conditions:
    - "base.ref == 'staging'"
    reviewers:
      teams:
      - staging-reviewers
  master:
    conditions:
    - "base.ref == 'master'"
    reviewers:
      teams:
      - admins
```

## Waiting until Travis CI passes to start review

With good tests and other static analysis and linters in place,
you can let computers take care of pointing out the obvious. Human
review can then focus on what people are good at.

Use `overrides` to make sure the author
takes care of everything your automated checks can help with
before bothering real people.

```yaml
version: 3
overrides:
- if: "'*travis*' not in statuses.successful"
  status: "failure"
  explanation: "Tests must pass before review starts"
```

## Developer Certificate of Origin (DCO)

A common part of the pull request process for open-source projects
is to use
[Developer Certificate of Origin ("DCO")](https://developercertificate.org/).

There are tools built specifically for this purpose, but if you
are already using PullApprove then we also have a simple
variable that you can use to directly incorporate signed-off commits
into your review process.

```yaml
version: 3
overrides:
- if: "not commits.are_signed_off"
  status: "pending"
  explanation: "Commits need to be signed-off before review starts"
```

## Requesting reviews one at a time

An important aspect of PullApprove is that you have
the control to notify people only when they are needed.

For example, if Steve and Mike both need to sign off on a design
change, but Mike really only wants to look at it after Steve already has,
then you could use a config like this:

```yaml
version: 3
groups:
  design:
    reviewers:
      # the order matters!
      users:
      - steve
      - mike
    reviews:
      request: 1
      required: 2
      request_order: given
```

## Making sure tasks are finished

If GitHub PR [task lists](https://help.github.com/en/articles/about-task-lists)
are an important part of your process, there is a simple way to check their
completion when writing PullApprove conditions.

For example, to ensure that the tasks are completed before
reviews are requested:

```yaml
version: 3
overrides:
- condition: "body and '- [ ]' in body"
  status: pending
  explanation: "Please finish all the tasks first"
```

## Spot checking PRs

An effective way to boost code quality without burdening reviewers is to enable "spot checking."
To do this, you can randomly enable code review on a percentage of PRs using the `percent_chance` function.
[A study by SmartBear found that spot checking "20% to 33% of the code resulted in lower defect density with minimal time expenditure."](https://smartbear.com/learn/code-review/best-practices-for-peer-code-review/)

```yaml
version: 3

groups:
  spot-check:
    conditions:
    - "percent_chance(33)"
```

## "Work in progress" pull requests

If pull requests are opened "early and often", then
you may not want the typical review to happen right away.

Teams have different preferences for how these are marked.

### Using labels

```yaml
version: 3
overrides:
- if: "'wip' in labels"
  status: pending
  explanation: "Work in progress"
```

### Using titles

```yaml
version: 3
overrides:
- if: "'WIP' in title"
  status: pending
  explanation: "Work in progress"
```

### Using "draft" pull requests

```yaml
version: 3
overrides:
- condition: "draft"
  status: pending
  explanation: "Work in progress"
```

## Global reviewers

Add a "global" group which can override/deactivate
other groups if they need to step in and approve a PR immediately.

```yaml
version: 3
groups:
  global:
    type: optional
    reviewers:
      teams:
      - global
    reviews:
      request: 0
      required: 1
      reviewed_for: required

  code:
    conditions:
    - "'global' not in groups.approved"
    ...
```

## Reviews from the public or non-essential contributors

Use optional groups to request or allow non-essential reviews
to play a role in your code review process.

```yaml
version: 3
groups:
  public:
    type: optional
    reviews:
      required: 1
```

## Fallback review group

You can implement a "fallback" set of reviewers by placing the group last,
and checking whether any of the previous groups have been activated (i.e.
conditions met).

```yaml
version: 3

groups:
  code:
    ...

  database:
    ...

  fallback:
    ...
    conditions:
    # this group is asked to review if no previous groups match this PR
    - "len(groups.active) == 0"  # or "not groups.active"
```

## Require that at least one group matches a PR

When reviews are based on the files modified,
you may want to ensure that every file is assigned to at least one review group.
You can use `overrides` to automatically add a failing status if a PR isn't covered by your existing groups.

```yaml
version: 3

overrides:
- if: "len(groups.active) < 1"
  status: failure
  explanation: "At least one group must match this PR. A new group may need to be added to match this kind of PR."

groups:
  backend:
    conditions: ["'app/*' in files"]
    ...
  js:
    conditions: ["'*.js' in files"]
    ...
  ...
```
