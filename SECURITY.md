# Security Policy

## Supported Versions

Plantagenet ships from `master` and tags releases from there; there are no
maintained release branches and no backports. Fixes land on `master` and go
out in the next tag, so the supported versions are **the latest release and
`master`**. If you are running something older, please check whether the
problem is still there on `master` before reporting it.

## Reporting a Vulnerability

**Please don't open a public issue for a security problem.**

Use GitHub's private vulnerability reporting: go to the
[Security tab](https://github.com/izrik/plantagenet/security) and choose
**Report a vulnerability**. That opens an advisory that only you and the
maintainer can see. If it isn't available to you, email the maintainer
directly at <izrik@izrik.com>.

Helpful things to include: what the problem is, where in the code it lives,
how to reproduce it against a local instance, and what an attacker gets out
of it. A proof of concept against your own checkout is welcome — please
don't test against a running site you don't own.

## Scope

In scope:

- the code in this repository, and
- the instances of Plantagenet that we run.

Out of scope:

- third-party dependencies — report those to the projects that maintain
  them; if a published advisory affects a version pinned in
  `requirements.txt` or `dev_requirements.txt`, an ordinary issue here is
  the right place for it;
- anything you would have to attack a running production system to find;
- findings that only apply to a deliberately insecure configuration, such
  as running with `--debug` exposed to the internet.

## What to Expect

- an acknowledgement that the report arrived;
- an assessment, and a fix when the finding is real and the fix is within
  reach of a small project;
- credit in the advisory and in [the changelog](CHANGELOG.md), if you want
  it.

This is a small project maintained by one person in their spare time. There
is no bounty, and no promise about how quickly a reply comes — only that
reports get read and that real problems get fixed.
