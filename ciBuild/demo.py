# -*- coding: utf-8 -*-
# -*- author: LinXunFeng -*-

from ciBuild.utils import upload_pgyer as PgyerUtil

if __name__ == "__main__":

    def upload_complete_callback(isSuccess, result):
        if isSuccess:
            print('upload success')
            _data = result['data']
            _url = _data['buildShortcutUrl'].strip()
            _appVer = _data['buildVersion']
            _buildVer = _data['buildBuildVersion']
            print('link: https://www.pgyer.com/%s' % _url)
            print('build: %s (build %s)' % (_appVer, _buildVer))
        else:
            print('upload fail')


    app_path = '<your app path>'
    pgyer_api_key = '<your api key>'
    pgyer_password = '<your app install password>'

    PgyerUtil.upload_to_pgyer(
        path=app_path,
        api_key=pgyer_api_key,
        password=pgyer_password,
        callback=upload_complete_callback)
