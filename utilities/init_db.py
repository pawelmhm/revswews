""" 
Initiate sample datatabase on dev server.
"""

from manipulate_db import populate_db
from src.config import DevelopmentConfig

if __name__ == "__main__":
	populate_db(DevelopmentConfig.DATABASE)