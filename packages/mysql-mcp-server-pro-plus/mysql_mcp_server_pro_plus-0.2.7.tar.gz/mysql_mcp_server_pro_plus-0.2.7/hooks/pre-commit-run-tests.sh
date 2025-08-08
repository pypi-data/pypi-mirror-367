#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running critical unit tests...${NC}"

# Check if we're in a git repository
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
  echo -e "${RED}Not in a git repository.${NC}"
  exit 1
fi

# Get the list of changed Python files
CHANGED_PY_FILES=$(git diff --cached --name-only --diff-filter=ACMR | grep -E '\.py$' || true)

if [ -z "$CHANGED_PY_FILES" ]; then
  echo -e "${GREEN}No Python files changed. Skipping tests.${NC}"
  exit 0
fi

# Determine which directories have changes
if echo "$CHANGED_PY_FILES" | grep -q "^src/"; then
  echo -e "${YELLOW}Running tests...${NC}"
  cd src && python -m pytest tests/critical -v || { echo -e "${RED}Tests failed!${NC}"; exit 1; }
  cd ..
fi

echo -e "${GREEN}All critical tests passed!${NC}"
exit 0
