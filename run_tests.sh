#!/bin/bash

source user-service/venv/bin/activate
pytest user-service
pytest api-gateway
