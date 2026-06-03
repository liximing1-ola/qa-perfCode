@echo off
cls
echo.
echo =========================================
echo         APK Build Toolset
echo =========================================
echo.
echo [againBuild] APK Processing Tools
echo   againKey      - Re-sign APK
echo   changeApk     - Decompile/Compile APK
echo   changeRes     - Modify APP Resources
echo.
echo [DaBao] Channel Packaging Tools
echo   batchChannelV2    - Single channel ops
echo   changeChannelList - Batch channel build
echo   getAppInfo        - View APK info
echo.
echo =========================================
echo.

:: Switch to project directory (works from any location)
cd /d "%~dp0"
echo Current: %cd%
echo.
echo Usage:
echo   python againBuild\againKey.py    - Re-sign APK
echo   python againBuild\changeApk.py   - Decompile/Compile APK
echo   python againBuild\changeRes.py   - Modify resources
echo   python DaBao\batchChannelV2.py   - Channel ops
echo   python DaBao\changeChannelList.py - Batch build
echo   python DaBao\getAppInfo.py      - APK info
echo.

cmd /k
