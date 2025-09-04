#!/bin/bash

# Start FastAPI backend on port 8001
uvicorn backend.api.api_server:app --host 0.0.0.0 --port 8001 &

# Start Streamlit frontend on port 8501
streamlit run app.py --server.port=8501 --server.address=0.0.0.0
