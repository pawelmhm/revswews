"""
Initiate sample datatabase on dev server.
"""

from utilities.manipulate_db import populateDb
from src.config import DevelopmentConfig

if __name__ == "__main__":
    populateDb(DevelopmentConfig.DATABASE)
