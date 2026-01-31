#!/bin/bash
echo "Starting Mushroom Farming API Server..."
echo ""
echo "Server will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
uvicorn main:app --reload

