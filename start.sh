#!/bin/bash
cd "$(dirname "$0")"
export PATH="$HOME/Library/Python/3.9/bin:$PATH"
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
streamlit run app.py --server.port 8501 --server.address 127.0.0.1 --server.headless true
