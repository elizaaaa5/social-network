#!/bin/bash

# Exit on error and print each command
set -ex

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the project root directory
PROJECT_ROOT=$(pwd)

# Install dependencies if needed
echo -e "${YELLOW}Checking dependencies...${NC}"
if [ ! -d "user-service/venv" ]; then
    echo -e "${YELLOW}Creating virtual environment for user-service...${NC}"
    cd user-service
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    pip install -e .
    pip install pytest-cov
    deactivate
    cd "$PROJECT_ROOT"
fi

if [ ! -d "api-gateway/venv" ]; then
    echo -e "${YELLOW}Creating virtual environment for api-gateway...${NC}"
    cd api-gateway
    python -m venv venv
    source venv/bin/activate
    pip install pytest requests-mock httpx
    deactivate
    cd "$PROJECT_ROOT"
fi

# Run user-service tests
echo -e "${GREEN}Running user-service tests...${NC}"
cd user-service
source venv/bin/activate
export SECRET_KEY="test-secret-key"
export DATABASE_URL="sqlite:///:memory:"
python -m pytest tests/ -v --cov=app --cov-report=term-missing
TEST_RESULT_USER=$?
deactivate
cd "$PROJECT_ROOT"

# Run api-gateway tests
echo -e "${GREEN}Running api-gateway tests...${NC}"
cd api-gateway
source venv/bin/activate
export USER_SERVICE_URL="http://user-service:8000"
python -m pytest tests/ -v
TEST_RESULT_API=$?
deactivate
cd "$PROJECT_ROOT"

# Check if any tests failed
if [ $TEST_RESULT_USER -ne 0 ] || [ $TEST_RESULT_API -ne 0 ]; then
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
else
    echo -e "${GREEN}All tests completed successfully!${NC}"
fi
