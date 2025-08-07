# Contributing Guide

Modified from [here](https://github.com/cncf/project-template/blob/main/CONTRIBUTING.md#contributing-guide).

* [Ways to Contribute](#ways-to-contribute)
* [Find an Issue](#find-an-issue)
* [Ask for Help](#ask-for-help)
* [Pull Request Lifecycle](#pull-request-lifecycle)
* [Development Environment Setup](#development-environment-setup)
* [Sign Your Commits](#sign-your-commits)
* [Pull Request Checklist](#pull-request-checklist)

Welcome! We are glad that you want to contribute to Hein Analytical Control! 💖

As you get started, you are in the best position to give us feedback on areas of
our project that we need help with including:

* Problems found during setting up a new developer environment
* Gaps in our Quickstart Guide or documentation
* Bugs in our Python scripts

If anything doesn't make sense, or doesn't work when you run it, please open a
bug report and let us know!

## Ways to Contribute

We welcome many different types of contributions including:

* New features
* Bug fixes
* Documentation

## Find an Issue

If there are currently issues present, please feel free to take one! 
Comment with something like "I would like to take this issue", 
and our team will communicate further with you in that issue.

## Ask for Help

The best way to reach us with a question when contributing is to ask on:

* The original GitLab issue
* Via email at: hao.lucyy@gmail.com (only inquiries sent to this email regarding this library will be answered)

## Pull Request Lifecycle

⚠️ **Explain your pull request process**

## Development Environment Setup

First, clone this repo. All required packages are specified in `pyproject.toml`. 
We use [poetry](https://python-poetry.org/), but you can adjust the `pyproject.toml` to 
work with your Python package manager. Activate your environment via your package manager's instructions
and this should be all you need to start development.

To update documentation, we use [Sphinx](https://www.sphinx-doc.org/en/master/). Install via instructions on
Sphinx's website. If you want a local version of the documentation website, then `cd docs`, `make clean`, `make html`.
Then within `docs/build`, open `index.html` in your browser.

## Sign Your Commits

### DCO
Licensing is important to open source projects. It provides some assurances that
the software will continue to be available based under the terms that the
author(s) desired. We require that contributors sign off on commits submitted to
our project's repositories. The [Developer Certificate of Origin
(DCO)](https://probot.github.io/apps/dco/) is a way to certify that you wrote and
have the right to contribute the code you are submitting to the project.

You sign-off by adding the following to your commit messages. Your sign-off must
match the git user and email associated with the commit.

    This is my commit message

    Signed-off-by: Your Name <your.name@example.com>

Git has a `-s` command line option to do this automatically:

    git commit -s -m 'This is my commit message'

If you forgot to do this and have not yet pushed your changes to the remote
repository, you can amend your commit with the sign-off by running 

    git commit --amend -s 

## Pull Request Checklist

When you submit your pull request, or you push new commits to it, our automated
systems will run some checks on your new code. We require that your pull request
passes these checks, but we also have more criteria than just that before we can
accept and merge it. We recommend that you check the following things locally
before you submit your code:

- have you provided a doc string for new functionality OR if you have extended an existing function,
ensure the doc string is still valid 
- are you using type annotations? 
- are your commit messages following the mentioned conventions?