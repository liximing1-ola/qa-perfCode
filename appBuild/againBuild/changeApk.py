import sys
import os
def unZip():
    try:
        choose = int(input('please choose 1=UnZip[1], 2=Zip[2]: '))
        if choose == 1:
            apk_path = sys.argv[1]
            # 12.19号新增参数--only-main-classes 处理dex包的函数数量超过限制无法正常解包
            cmd = 'java -jar apktool_2.6.1.jar d --only-main-classes {} '.format(apk_path)
            os.system(cmd)
        elif choose == 2:
            file_path = sys.argv[1]
            apk_path = sys.argv[1] + '.apk'
            print(apk_path)
            # 2.5.0要移除 -c
            cmd = 'java -jar apktool_2.6.1.jar b {} -c -o {}'.format(file_path, apk_path)
            os.system(cmd)
    except Exception as error:
        print(error, 'LOCK PATH')


if __name__ == '__main__':
    unZip()



