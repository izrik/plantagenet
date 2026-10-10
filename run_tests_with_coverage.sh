#!/bin/bash

coverage run --source=plantagenet -m pytest tests/ "$@" && \
    coverage html && \
    flake8 plantagenet.py tests/ && \
    bandit plantagenet.py && \
    shellcheck run_tests_with_coverage.sh && \
    pymarkdown scan README.md && \
    pip-audit && \
    echo Success

# TODO: add Dockerfile linting (hadolint is the standard tool but has no pip
# package; options include the hadolint binary, Docker image, or GitHub Action)
# TODO: add CSS linting (no well-maintained Python CSS linter exists on PyPI;
# csslint and stylelint are Node.js-based alternatives)
