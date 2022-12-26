from pathlib import Path
import sys

HERE = Path(__file__).parent

try:
    import flask
except ImportError:
    flask = None

if flask is None:
    # nobody has shipped flask, we need to use our bundled copy
    sys.path.append(str(HERE / "packages"))

try:
    from flask import Flask
except ImportError:
    Flask = None  # wont happen, just to placate PyCharm

