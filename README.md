# perfCode

# appBuild/againBuild
# againKey.py 
用于apk重新签名
# changeApk.py 
用于反编译apk
# changeRes.py 
用于直接修改app内各路径下资源文件

# appBuild/DaBao
# batchChannelV2.py 
利用walle修改channel
# changeChannelList.py 
利用walle批量修改channel，用于国内Android开发者提审
# getAppInfo.py 
用于获取当前apk的包名和版本
# changeImage.py 
将图片批量置灰

# ciBuild
jenkin打包成功后直接上传到蒲公英方法

# mobilePerf app性能数据获取脚本
# 工具获取
1.https://github.com/alipay/SoloPi  路径下载最新版本
2.代码仓库直接下载安装
3.安装成功后看下使用教程，目前仅支持安卓
4.使用工具获取到app的性能数据后，使用run.sh(mac)/openPerf.bat(windows)将数据生成折线图用于分析
5.可以通过工具获取Android端的内存，FPS，CPU等数据

# 冷启动和热启动时间
可以用testPhoneTime获取，使用时需要修改app的包名和activity

# 拿到脚本后可以根据自己需要修改，如果有更好的方案，可以群里一起沟通下，iOS方案和工具还在验证

