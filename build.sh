#!/bin/bash
set -e
pip3 install pyinstaller

pyinstaller \
    --onefile --windowed \
    --add-data "config:config" \
    --name="AI-Analytics" \
    src/main.py

echo "Build complete. Output: dist/AI-Analytics"
