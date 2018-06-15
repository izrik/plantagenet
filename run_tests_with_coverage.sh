#!/bin/bash

coverage run --source=plantagenet ./run_tests.py "$@" && \
    coverage html
