#!/usr/bin/env bash
# SoloPi 性能数据一键拉取和图表生成脚本

set -euo pipefail

# 获取脚本所在目录
BASEDIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== SoloPi 性能数据收集 ==="

# 拉取数据
echo "[1/5] 拉取 SoloPi 数据..."
python "${BASEDIR}/tools/changeFile.py"

# 生成图表
echo "[2/5] 生成 CPU 图表..."
python "${BASEDIR}/tools/csvToChart.py" cpu

echo "[3/5] 生成 FPS 图表..."
python "${BASEDIR}/tools/csvToChart.py" fps

echo "[4/5] 生成 MEM 图表..."
python "${BASEDIR}/tools/csvToChart.py" mem

echo "[5/5] 生成 TEMP 图表..."
python "${BASEDIR}/tools/csvToChart.py" temp

echo ""
echo "=== 全部完成 ==="