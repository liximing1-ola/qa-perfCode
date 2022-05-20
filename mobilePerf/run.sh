#!/usr/bin/env bash
basedir=`cd $(dirname $0); pwd -P`
python $basedir/tools/changeFile.py
python $basedir/tools/csvToChart.py cpu
python $basedir/tools/csvToChart.py fps
python $basedir/tools/csvToChart.py mem