# Ensure Django apps under kermartin_backend are importable as top-level packages
import os
import sys

PROJECT_ROOT = os.path.dirname(__file__)
BACKEND_DIR = os.path.join(PROJECT_ROOT, "kermartin_backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
