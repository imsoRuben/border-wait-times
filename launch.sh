#!/bin/bash

if [ -z "$PORT" ]; then
  echo "🚨 \$PORT is not set! Defaulting to 10000"
  PORT=10000
fi

echo "✅ Starting app on PORT $PORT"
uvicorn border_app:app --host 0.0.0.0 --port $PORT