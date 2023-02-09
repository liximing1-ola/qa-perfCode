#!/usr/bin/env bash
# shellcheck disable=SC2046
# shellcheck disable=SC2164
# shellcheck disable=SC2006
basedir=`cd $(dirname "$0"); pwd -P`
python "$basedir"/tools/changeFile.py
python "$basedir"/tools/csvToChart.py cpu
# shellcheck disable=SC2086
python $basedir/tools/csvToChart.py fps
python "$basedir"/tools/csvToChart.py mem
python "$basedir"/tools/csvToChart.py temp