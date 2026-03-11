import sys
import os


def unZip():
    """Handle APK unzipping and zipping operations based on user choice"""
    if len(sys.argv) < 2:
        print("Error: Please provide a file path as an argument")
        return

    try:
        # Get and validate user choice
        choose_input = input('please choose 1=UnZip[1], 2=Zip[2]: ')
        choose = int(choose_input)

        if choose == 1:
            apk_path = sys.argv[1]
            # 12.19号新增参数--only-main-classes 处理dex包的函数数量超过限制无法正常解包
            cmd = f'java -jar apktool_2.6.1.jar d --only-main-classes {apk_path}'
            os.system(cmd)
        elif choose == 2:
            file_path = sys.argv[1]
            apk_path = f"{file_path}.apk"
            print(apk_path)
            # 2.5.0要移除 -c
            cmd = f'java -jar apktool_2.6.1.jar b {file_path} -c -o {apk_path}'
            os.system(cmd)
        elif choose == 3:
            pass
        else:
            print("Invalid choice. Please enter 1 or 2")

    except ValueError:
        print(f"Please enter a number (1 or 2)")
    except Exception as error:
        print(f"Operation failed: {error}")


if __name__ == '__main__':
    unZip()
