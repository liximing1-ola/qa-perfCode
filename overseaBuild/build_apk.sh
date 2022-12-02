#!/usr/bin/env bash
buildType=$1
versionName=$2
versionCode=$3
debugModel=$4
releaseNotes=$5
ciNum=$6

projectPath=$(dirname "$PWD")

if [ $buildType == "debug" ]; then
    apkPath="$projectPath/build/app/outputs/apk/banban_locale/profile/app-banban_locale-profile.apk"
    if [ -d "$projectPath/build/app/outputs" ]; then
        rm -rf $projectPath/build/app/outputs
    fi
    cur_timestamp=$(date +%s)
    flutter build apk --profile --build-number $versionCode --build-name $versionName --flavor banban_locale --dart-define=BUILD_TIME="$cur_timestamp" --dart-define=DEBUG_MODE=true --dart-define=CI_NUM="$ciNum" --target-platform=android-arm64 -v
    if [ -f "$apkPath" ]; then
        curl -O -F "file=@${apkPath}" -F '_api_key=f81f472078152a37cdcd1f56f8697147' https://www.pgyer.com/apiv2/app/upload
    fi

    mv $apkPath $projectPath/build/app/outputs/apk/partying_${buildType}_${ciNum}.apk
elif [ $buildType == "release" ]; then
    apkPath="$projectPath/build/app/outputs/apk/banban_locale/release/app-banban_locale-release.apk"
    if [ -d "$projectPath/build/app/outputs" ]; then
        rm -rf $projectPath/build/app/outputs
    fi
    if [[ "$debugModel" == "enable" ]]; then
        cur_timestamp=$(date +%s)
        flutter build apk --release --build-number $versionCode --build-name $versionName --flavor banban_locale --dart-define=BUILD_TIME="$cur_timestamp" --dart-define=DEBUG_MODE=true --dart-define=CI_NUM="$ciNum" --target-platform=android-arm64 -v
    else
        flutter clean
        flutter build apk --release --build-number $versionCode --build-name $versionName --flavor banban_locale --dart-define=DEBUG_MODE=false --target-platform=android-arm64 -v
    fi
    if [ -f "$apkPath" ]; then
        curl -O -F "file=@${apkPath}" -F '_api_key=f81f472078152a37cdcd1f56f8697147' https://www.pgyer.com/apiv2/app/upload
    fi
    mv $apkPath $projectPath/build/app/outputs/apk/partying_${buildType}_${ciNum}.apk
elif [ $buildType == "store" ]; then
    cd $projectPath
    
    flutter clean

    bundlePath="$projectPath/build/app/outputs/bundle/banban_localeRelease/app-banban_locale-release.aab"

    flutter build appbundle --release --build-number $versionCode --build-name $versionName --dart-define=ABI_FILTERS="armeabi-v7a;arm64-v8a" --flavor banban_locale --target-platform=android-arm,android-arm64 -v

    mv $bundlePath $projectPath/build/app/outputs/bundle/partying_$versionName.aab

    package="com.imbb.oversea.android"
    uploadPath="$projectPath/build/app/outputs/bundle/partying_$versionName.aab"

    cd $projectPath/ci/upload_gp
    python3 upload_apks_with_listing.py $package $uploadPath $versionName "$releaseNotes"
    cd $projectPath
fi
