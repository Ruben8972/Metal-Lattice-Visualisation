from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vis.interactive_viewer import run_interactive_viewer

if __name__ == "__main__":
    run_interactive_viewer()
