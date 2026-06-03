#!/usr/bin/env bash
# SoloPi 数据拉取与图表生成（使用相对路径）
BASEDIR="$(cd "$(dirname "$0")" && pwd)"
python3 "${BASEDIR}/changeFile.py"
python3 "${BASEDIR}/csvToChart.py"