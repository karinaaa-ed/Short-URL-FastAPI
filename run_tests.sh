#!/bin/bash

# Unit tests
echo "Running unit tests..."
coverage run -m pytest tests/unit/ -v

# Functional tests
echo "Running functional tests..."
coverage run -a -m pytest tests/functional/ -v

# Generate coverage report
coverage html
echo "Coverage report generated at htmlcov/index.html"

# Load testing (optional)
echo "To run load tests, execute: locust -f tests/load/locustfile.py"