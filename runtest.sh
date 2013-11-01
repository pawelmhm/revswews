#!/bin/bash

export FLASK_CONF=TEST 
echo "FLASK CONF is: $FLASK_CONF"
python -m tests/test_all -vf && python tests/test_modele -vf && python -m tests/test_login
export FLASK_CONF=DEV
echo "FLASK CONF is now: $FLASK_CONF"
