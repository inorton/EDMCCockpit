from pathlib import Path
import sys

HERE = Path(__file__).parent.absolute()
PACKAGES = str(HERE / "packages")

if PACKAGES not in sys.path:
    # nobody has shipped flask, we need to use our bundled copy
    sys.path.append(PACKAGES)

from flask import Flask
from flask_sock import Sock


