#!/bin/bash

# Exit on error and print each command
set -ex

# Define colors for output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}Running user-service tests...${NC}"
cd user-service && pytest tests/ -v --cov=app --cov-report=term-missing

echo -e "${GREEN}Running api-gateway tests...${NC}"
cd ../api-gateway && pytest tests/ -v

echo -e "${GREEN}All tests completed successfully!${NC}"
