#!/bin/sh

set -eu

PYTHON=${PYTHON:-/usr/local/Caskroom/miniconda/base/bin/python3}

"$PYTHON" -m pip install -r requirements.txt
"$PYTHON" -m fetch.hse
"$PYTHON" -m fetch.fipi
"$PYTHON" -m parse.hse
"$PYTHON" -m parse.fipi
"$PYTHON" coverage.py
"$PYTHON" cohort.py
"$PYTHON" rank.py
"$PYTHON" route_ability.py
"$PYTHON" plot.py
"$PYTHON" -m unittest discover
