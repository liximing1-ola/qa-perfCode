import os
import sys
import subprocess


def reSign():
    if len(sys.argv) != 3:
        print('--------Please provide input APK path and output APK path as arguments--------')
        exit(1)

    # Use raw strings for Windows paths to avoid escape character issues
    sdk_path = r'D:/build-tools/build-tools/29.0.2/apksigner.bat'
    # 不夜星球
    keystore_path = r'D:\keystore\slp.keystore'
    keystore_pass = 'PLS_699'
    # 彩虹星球
    # keystore_path = r'D:\keystore/rbp.keystore'
    # keystore_pass = '634rbp'

    apk_path = sys.argv[1]
    out_path = sys.argv[2]

    if not os.path.exists(apk_path):
        print(f"Error: Input APK file not found - {apk_path}")
        exit(1)

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
