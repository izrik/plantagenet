#!/bin/bash

coverage run --source=plantagenet -m pytest run_tests.py test_extern.py "$@" && \
    coverage html && \
    flake8 plantagenet.py run_tests.py test_extern.py && \
    shellcheck run_tests_with_coverage.sh && \
    pymarkdown scan README.md && \
    csslint static/plantagenet.css && \
    pip-audit && \
    dockerlint Dockerfile && \
    dockerfile_lint Dockerfile &&
    echo Success
