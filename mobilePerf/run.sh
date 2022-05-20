#!/usr/bin/env bash
basedir=`cd $(dirname $0); pwd -P`
echo $basedir
echo 11111
python ~/PycharmProjects/perfCode/mobilePerf/tools/changeFile.py
python ~/PycharmProjects/perfCode/mobilePerf/tools/csvToChart.py cpu
python ~/PycharmProjects/perfCode/mobilePerf/tools/csvToChart.py fps
python ~/PycharmProjects/perfCode/mobilePerf/tools/csvToChart.py mem