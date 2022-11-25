import os
import shutil
import sys


def changeRes():
    if len(sys.argv) != 3:
        print('--------Please Input Two Path--------')
        exit(0)
    # 解压包路径
    res_path = sys.argv[1]
    # 新资源路径
    res_name_path = sys.argv[2]
    # 解压包res下路径
    pkg_res_path = res_path + '/res'
    # 解压包下assets下路径
    base_logo_path = res_path + '/assets/flutter_assets/assets/module/banban_base'
    # 一键登录webp路径
    base_webp_path = res_path + '/assets/flutter_assets/assets\module\login'

    checkIconPath(res_name_path)
    # 替换资源
    new_res_path_72 = res_name_path + '/72.png'
    new_res_path_96 = res_name_path + '/96.png'
    new_res_path_144 = res_name_path + '/144.png'
    new_res_path_192 = res_name_path + '/192.png'
    # 新增432icon,处理原生安卓8以上桌面icon问题
    new_res_path_432 = res_name_path + '/432.png'
    new_res_path_512 = res_name_path + '/512.png'
    new_res_path_1080 = res_name_path + '/1080.png'
    # 新增webp文件。处理闪屏
    # https://squoosh.app/
    new_res_path_webp = res_name_path + '/1080.webp'
    # 新增login_btn和logo.png 处理一键登录页面
    new_res_path_logo = res_name_path + '/logo.png'
    new_res_path_login_btn = res_name_path + '/login_btn.png'

    # 替换路径
    res_path_hdpi_72 = pkg_res_path + '/mipmap-hdpi'
    res_path_xhdpi_96 = pkg_res_path + '/mipmap-xhdpi'
    res_path_xxhdpi_144 = pkg_res_path + '/mipmap-xxhdpi'
    res_path_xxxhdpi_192 = pkg_res_path + '/mipmap-xxxhdpi'
    res_path_xxhdpi_splash = pkg_res_path + '/mipmap-xxhdpi'
    res_path_drawable_512 = pkg_res_path + '/drawable'

    res_path_list = {
        new_res_path_72: res_path_hdpi_72,
        new_res_path_96: res_path_xhdpi_96,
        new_res_path_144: res_path_xxhdpi_144,
        new_res_path_192: res_path_xxxhdpi_192,
        new_res_path_1080: res_path_xxhdpi_splash,
    }

    for k, v in res_path_list.items():
        if not os.path.exists(k):
            print('需更换资源包地址错误！')
        if not os.path.exists(v):
            print('地址错误！')

    try:
        shutil.copy(new_res_path_72, res_path_hdpi_72)
        shutil.move(res_path_hdpi_72 + '/72.png', res_path_hdpi_72 + '/ic_launcher.png')
    except Exception as error:
        print(error)
    else:
        print('mipmap-hdpi: 72px  资源更换成功')

    try:
        shutil.copy(new_res_path_96, res_path_xhdpi_96)
        shutil.move(res_path_xhdpi_96 + '/96.png', res_path_xhdpi_96 + '/ic_launcher.png')
    except Exception as error:
        print(error)
    else:
        print('mipmap-xhdpi: 96px  资源更换成功')

    try:
        shutil.copy(new_res_path_144, res_path_xxhdpi_144)
        shutil.move(res_path_xxhdpi_144 + '/144.png', res_path_xxhdpi_144 + '/ic_launcher.png')
    except Exception as error:
        print(error)
    else:
        print('mipmap-xxhdpi: 144px  资源更换成功')

    try:
        shutil.copy(new_res_path_192, res_path_xxxhdpi_192)
        shutil.move(res_path_xxxhdpi_192 + '/192.png', res_path_xxxhdpi_192 + '/ic_launcher.png')
    except Exception as error:
        print(error)
    else:
        print('mipmap-xxxhdpi: 192px  资源更换成功')

    try:
        shutil.copy(new_res_path_1080, res_path_xxhdpi_splash)
        shutil.move(res_path_xxhdpi_splash + '/1080.png', res_path_xxhdpi_splash + '/splash.png')
    except Exception as error:
        print(error)
    else:
        print('mipmap-xxhdpi: 1080px  资源更换成功')

    if not os.path.exists(res_path_drawable_512):
        print('res_path_drawable_512 地址错误！')
    try:
        shutil.copy(new_res_path_512, res_path_drawable_512)
        shutil.move(res_path_drawable_512 + '/512.png', res_path_drawable_512 + '/ic_launcher.png')
    except Exception as error:
        print(error)
    else:
        print('drawable: 512px  资源更换成功')

    if not os.path.exists(base_logo_path):
        print('base_logo_path 地址错误！')
    try:
        shutil.copy(new_res_path_144, base_logo_path)
        shutil.move(base_logo_path + '/144.png', base_logo_path + '/logo.png')
    except Exception as error:
        print(error)
    else:
        print('banban_base: 144px  资源更换成功')

    # 11.1新增处理ic_launcher_foreground.png
    try:
        shutil.copy(new_res_path_432, res_path_drawable_512)
        shutil.move(res_path_drawable_512 + '/432.png', res_path_drawable_512 + '/ic_launcher_foreground.png')
    except Exception as error:
        print(error)
    else:
        print('drawable ic_launcher_foreground: 432px  资源更换成功')

    # 2020-7.22新增处理ic_launcher_foreground.png放在mipmap-xxxhdpi中
    try:
        shutil.copy(new_res_path_432, res_path_xxxhdpi_192)
        shutil.move(res_path_xxxhdpi_192 + '/432.png', res_path_xxxhdpi_192 + '/ic_launcher_foreground.png')
    except Exception as error:
        print(error)
    else:
        print('xxxhdpi ic_launcher_foreground: 432px  资源更换成功')

    # 2020-7.23 新增处理一键登录默认icon
    try:
        shutil.copy(new_res_path_webp, base_webp_path)
        shutil.move(base_webp_path + '/1080.webp', base_webp_path + '/login_splash.webp')
    except Exception as error:
        print(error)
    else:
        print('一键登录:1080.webp 资源更换成功')

    try:
        shutil.copy(new_res_path_logo, res_path_drawable_512)
        shutil.move(res_path_drawable_512 + '/logo.png', res_path_drawable_512 + '/logo.png')
    except Exception as error:
        print(error)
    else:
        print('一键登录:logo.png 资源更换成功')

    try:
        shutil.copy(new_res_path_login_btn, res_path_drawable_512)
        shutil.move(res_path_drawable_512 + '/login_btn.png', res_path_drawable_512 + '/login_btn.png')
    except Exception as error:
        print(error)
    else:
        print('一键登录:login_btn.png 资源更换成功')


def checkIconPath(p_path):
    p_list = ['72.png', '96.png', '144.png', '192.png', '432.png', '512.png', '1080.png', '1080.webp', 'login_btn.png',
              'logo.png']
    for p in os.listdir(p_path):
        if p not in p_list:
            raise EnvironmentError('{}--名称错误'.format(p))
        elif len(os.listdir(p_path)) != 10:
            raise EnvironmentError('资源不足')
    return True


if __name__ == '__main__':
    # python changeResOld.py 解压包地址 资源地址
    # 修改背景色值
    changeRes()
