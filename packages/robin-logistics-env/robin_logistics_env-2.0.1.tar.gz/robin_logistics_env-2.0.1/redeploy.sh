#!/bin/bash

echo "🧹 Cleaning old build artifacts..."
rm -rf dist/ build/ robin_logistics_env.egg-info/

echo "🔨 Building package..."
python -m build

echo "📦 Uploading to PyPI..."
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-AgEIcHlwaS5vcmcCJGM4ZWMzMzAwLTNjZmItNDJiMy04ZWJmLTIyYjRiMTFjMjJkNAACKlszLCI2NzVlNDU2Zi02ODdjLTRjMTYtYjU0YS0zNGIyYTE0NGU2ZTAiXQAABiCqrtdhsX2HqXAEkXV1NyRf7G4iLGZFv-5V9kFsxVULwQ
twine upload dist/*

echo "✅ Package deployed! New version available."
echo ""
echo "To test:"
echo "  pip install --upgrade robin-logistics-env"
echo "  cd contestant_example"
echo "  python my_solver.py"