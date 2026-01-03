#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python mcp_host.py
