import os, sys
_dir = os.path.dirname(os.path.abspath(__file__))
if _dir not in sys.path: sys.path.insert(0, _dir)
from app import app

if __name__ == '__main__':
    app.run()
