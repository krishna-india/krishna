from importlib import import_module
import sys
from pathlib import Path

# ensure project root is importable
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

# lazily load utils to avoid heavy imports during startup
def __getattr__(name):
    if name == 'utils':
        return import_module('utils')
    raise AttributeError(name)
