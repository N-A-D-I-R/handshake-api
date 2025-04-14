#!/bin/bash

service postgresql start
service redis start

sleep 5

# Run the application
exec uvicorn main:app --host 0.0.0.0 --port 8000