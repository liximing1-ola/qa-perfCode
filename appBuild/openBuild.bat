@echo off
chcp 65001 >nul
echo.
echo =========================================
echo         APK 构建工具集
echo =========================================
echo.
echo [againBuild] APK 处理工具
echo   againKey      - 重签名 APK
echo   changeApk     - 反编译/打包 APK
echo   changeRes     - 修改 APP 资源
echo.
echo [DaBao] 渠道包工具
echo   batchChannelV2    - 单个渠道包操作
echo   changeChannelList - 批量生成渠道包
echo   getAppInfo        - 查看 APK 信息
echo.
echo =========================================
echo.

:: 切换到脚本所在目录
cd /d "%~dp0"
cmd /k