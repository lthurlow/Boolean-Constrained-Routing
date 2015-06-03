#!/bin/bash

for PY in py25 py26 py26d py27 py32 py33
do
    if [ $PY == py25 ]; then
        export CC='gcc -arch i386'
    else
        unset CC
    fi
    export PYTHON=$HOME/$PY/bin/python
    make clean
    make test || exit 1
done
