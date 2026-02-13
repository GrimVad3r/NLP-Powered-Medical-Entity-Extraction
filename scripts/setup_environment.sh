#!/bin/bash
# Create __init__.py files for all packages

mkdir -p src/core
mkdir -p src/extraction
mkdir -p src/nlp
mkdir -p src/database
mkdir -p src/transformation
mkdir -p src/api/routes
mkdir -p src/dashboard/pages
mkdir -p src/utils
mkdir -p tests/unit
mkdir -p tests/integration
mkdir -p tests/performance

# Create __init__.py files
touch src/__init__.py
touch src/core/__init__.py
touch src/extraction/__init__.py
touch src/nlp/__init__.py
touch src/database/__init__.py
touch src/transformation/__init__.py
touch src/api/__init__.py
touch src/api/routes/__init__.py
touch src/dashboard/__init__.py
touch src/dashboard/pages/__init__.py
touch src/utils/__init__.py
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py
touch tests/performance/__init__.py

echo "✅ All __init__.py files created"