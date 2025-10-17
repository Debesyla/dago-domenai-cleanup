#!/bin/bash
set -e

echo "🧹 Running Domain Cleaner..."
python3 src/domain_cleaner.py

echo "✅ Done! Check assets/output.txt"