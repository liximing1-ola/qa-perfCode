import os
import sys


def reSign():
    if len(sys.argv) != 3:
        print('--------Please Input Two Path--------')
        exit(0)
    # 本机配置环境路径
    # 华为空包限制用D:\android-sdk-windows\build-tools\27.0.3
    # apksigner路径
    sdk_path = 'D:/build-tools/build-tools/29.0.2/apksigner.bat'
    # sdk_path = 'D:\AndroidSDK/build-tools/27.0.3/apksigner.bat'

    # 老项目keystore路径
    # keystore_path = 'D:/keystore/my-release-key.keystore'
    # password
    # keystore_pass = 'imee2016'
    # 不夜星球
    # keystore_path = 'D:\keystore\slp.keystore'
    # keystore_pass = 'PLS_699'
    # 彩虹星球
    keystore_path = 'D:\keystore/rbp.keystore'
    keystore_pass = '634rbp'
    # 加固包路径
    apk_path = sys.argv[1]
    # 重签包路径
    out_path = sys.argv[2]
    cmd = sdk_path + ' sign --ks ' + keystore_path + ' --ks-pass pass:' + keystore_pass + ' --out ' + out_path + ' ' + apk_path
    os.system(cmd)

    # 验证
    os.system(sdk_path + " verify -v {}".format(out_path))
    print('--------------------------重签完毕--------------------------')


if __name__ == '__main__':
    reSign()
