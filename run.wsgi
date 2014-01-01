import site
import sys
import os
sys.path.append(os.path.dirname(__file__))
from src import app as application

if __name__ == "__main__":
    application.run()
