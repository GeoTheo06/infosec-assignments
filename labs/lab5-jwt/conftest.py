import sys
from pathlib import Path

# Make jwtlab / ta / student / grader importable when pytest is run from the
# repo root or anywhere else.
sys.path.insert(0, str(Path(__file__).resolve().parent))
