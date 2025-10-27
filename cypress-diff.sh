#!/bin/bash

# Find the two most recent commits that changed reports/cypress/cypress.csv
commits=$(git log -n 2 --pretty=format:%H -- reports/cypress/cypress.csv)

# Get the most recent and previous commit
latest=$(echo "$commits" | head -n 1)
previous=$(echo "$commits" | tail -n 1)

# If we found both commits, show the diff
if [ -n "$latest" ] && [ -n "$previous" ] && [ "$latest" != "$previous" ]; then
    git diff $previous $latest -- reports/cypress/cypress.csv
else
    echo "Not enough commit history found for reports/cypress/cypress.csv"
fi
