---
title: Reviewing PRs
description: How to review PRs in GitHub and additional PullApprove syntax
template: markdown_page.template.html
next:
  url: /extension/
  title: Chrome extension
prev:
  url: /
  title: Topics
---

# Reviewing PRs

When submitting your review, PullApprove provides the option to specify *which*
group that review is for. This allows you to review a PR multiple times, for
different purposes. Or, for example, to review a PR for "security" but leave
general "code" review for someone else. By default, a review will apply to all
groups that you are capable of reviewing for.

## Usage

Use the `Reviewed-for: groupname` syntax to specify a group. The `groupname`
should exactly match one of the groups defined in your `.pullapprove.yml`. To
apply the review to multiple groups, just comma-separate them: `Reviewed-for:
security, code`.

![PullApprove Reviewed-for specific groups](/assets/img/screenshots/reviewed-for-approve.png)

And the same syntax can be used to request changes for specific groups only.

![PullApprove Reviewed-for specific groups](/assets/img/screenshots/reviewed-for-reject.png)
