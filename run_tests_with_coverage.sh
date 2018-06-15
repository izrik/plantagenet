#!/bin/bash

coverage run --source=plantagenet ./run_tests.py "$@" && \
    coverage html && \
    flake8 plantagenet.py run_tests.py
    shellcheck run_tests_with_coverage.sh
    markdownlint README.md
