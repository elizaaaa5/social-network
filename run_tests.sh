#!/bin/bash

# Exit on error and print each command
set -ex

# Define colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Function to start dependencies
start_dependencies() {
    echo -e "${GREEN}Starting database...${NC}"
    docker-compose up -d db
}

# Function to wait for database to be ready
wait_for_db() {
    echo -e "${GREEN}Waiting for database to become ready...${NC}"
    docker-compose exec db \
        bash -c "while ! pg_isready -U user -d userdb; do sleep 2; done"
}

# Function to create test database
create_test_db() {
    echo -e "${GREEN}Creating test database...${NC}"
    docker-compose exec db \
        psql -U user -d userdb -c "CREATE DATABASE userdb_test;" || true
}

# Function to run user-service tests
run_user_service_tests() {
    echo -e "${GREEN}Running user-service tests...${NC}"
    docker-compose run --rm \
        -e DATABASE_URL="postgresql://user:password@db/userdb_test" \
        -e SECRET_KEY="test-secret" \
        user-service \
        pytest tests/ -v --cov=app --cov-report=term-missing
}

# Function to run api-gateway tests
run_api_gateway_tests() {
    echo -e "${GREEN}Running api-gateway tests...${NC}"
    docker-compose run --rm \
        -e USER_SERVICE_URL="http://user-service:8000" \
        api-gateway \
        pytest tests/ -v
}

# Function to clean up
cleanup() {
    echo -e "${GREEN}Cleaning up...${NC}"
    docker-compose down -v --remove-orphans
}

# Main execution
main() {
    start_dependencies
    wait_for_db
    create_test_db
    
    case $1 in
        user)
            run_user_service_tests
            ;;
        gateway)
            run_api_gateway_tests
            ;;
        --no-cleanup)
            run_user_service_tests
            run_api_gateway_tests
            ;;
        *)
            run_user_service_tests
            run_api_gateway_tests
            ;;
    esac
    
    [[ "$1" != "--no-cleanup" ]] && cleanup
}

# Set trap to ensure cleanup happens on script exit
trap cleanup EXIT

# Run main function
main "$@"

echo -e "${GREEN}All tests completed successfully!${NC}"
