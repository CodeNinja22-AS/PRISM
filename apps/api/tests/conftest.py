import sys
import os

# Get the path to the root PRISM directory
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# Insert the root directory and services directly into the Python path
sys.path.insert(0, base_dir)
sys.path.insert(0, os.path.join(base_dir, 'services'))

