#!/bin/bash
echo "PORT is: $PORT"
uvicorn border_app:app --host 0.0.0.0 --port $PORT