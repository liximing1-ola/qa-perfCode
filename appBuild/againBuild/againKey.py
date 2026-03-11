import os
import sys


def reSign1():
    if len(sys.argv) != 3:
        print('--------Please input two path--------')
        exit(1)
    # 华为空包限制用D:\android-sdk-windows\build-tools\27.0.3
    # apksigner路径
    sdk_path = 'D:/build-tools/build-tools/29.0.2/apksigner.bat'
    # sdk_path = 'D:\AndroidSDK/build-tools/27.0.3/apksigner.bat'

    # keystore路径
    # keystore_path = 'D:/keystore/my-release-key.keystore'
    # password
    keystore_pass = 'imee2016'
    # 不夜星球
    keystore_path = 'D:\keystore\slp.keystore'
    keystore_pass = 'PLS_699'
    # 彩虹星球
    # keystore_path = 'D:\keystore/rbp.keystore'
    # keystore_pass = '634rbp'
    # 加固包路径
    apk_path = sys.argv[1]
    # 重签包路径
    out_path = sys.argv[2]
    cmd = sdk_path + ' sign --ks ' + keystore_path + ' --ks-pass pass:' + keystore_pass + ' --out ' + out_path + ' ' + apk_path
    os.system(cmd)

    # verify
    os.system(sdk_path + " verify -v {}".format(out_path))
    print('-----------------------sign-----------------------')


import os
import sys
import subprocess


def reSign():
    if len(sys.argv) != 3:
        # Improved error message with clear argument instructions
        print('--------Please provide input APK path and output APK path as arguments--------')
        exit(1)  # Use non-zero exit code for errors

    # Use raw strings for Windows paths to avoid escape character issues
    sdk_path = r'D:/build-tools/build-tools/29.0.2/apksigner.bat'
    # keystore_path = r'D:/keystore/my-release-key.keystore'
    # keystore_pass = 'imee2016'
    # 不夜星球
    keystore_path = r'D:\keystore\slp.keystore'
    keystore_pass = 'PLS_699'
    # 彩虹星球
    # keystore_path = r'D:\keystore/rbp.keystore'
    # keystore_pass = '634rbp'

    apk_path = sys.argv[1]
    out_path = sys.argv[2]

    # Check if input APK exists
    if not os.path.exists(apk_path):
        print(f"Error: Input APK file not found - {apk_path}")
        exit(1)

    # Use subprocess with argument list for safer execution (handles spaces in paths)
    sign_cmd = [
        sdk_path,
        'sign',
        '--ks', keystore_path,
        '--ks-pass', f'pass:{keystore_pass}',
        '--out', out_path,
        apk_path
    ]

    try:
        # Execute sign command with error checking
        subprocess.run(sign_cmd, check=True, capture_output=True, text=True)
        print("Signing completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Signing failed: {e.stderr}")
        exit(1)

    # Verify command with subprocess
    verify_cmd = [sdk_path, "verify", "-v", out_path]
    try:
        subprocess.run(verify_cmd, check=True, capture_output=True, text=True)
        print("Verification successful")
    except subprocess.CalledProcessError as e:
        print(f"Verification failed: {e.stderr}")
        exit(1)

    print('-----------------------sign-----------------------')


if __name__ == '__main__':
    reSign()
