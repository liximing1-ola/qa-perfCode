#!/usr/bin/env bash
set -e
source ios_uploader.sh

buildType=$1
versionName=$2
versionCode=$3
debugModel=$4
# shellcheck disable=SC2034
releaseNotes=$5
ciNum=$6

projectPath=$(dirname "$PWD")

function buildStore() {
    cd "$projectPath"
    flutter clean
    flutter pub get
    cd ios
    arch -x86_64 pod install --repo-update

    ipaPath=$projectPath/build/ios/ipa/Partying.ipa
    
    # shellcheck disable=SC2086
    flutter build ios --release --build-number $versionCode --build-name $versionName
    bundle exec fastlane ios store

    cd "$projectPath"/ci
    upload_ipa "$ipaPath"

    # upload dSYM
    uploadymbolsPath=$projectPath/ios/Pods/FirebaseCrashlytics/upload-symbols
    plistPath=$projectPath/ios/Runner/GoogleService-Info.plist
    dsymPath=$projectPath/build/ios/archive/Runner.xcarchive/dSYMs/Runner.app.dSYM
    if [ -f "$dsymPath" ];then
      $uploadymbolsPath -gsp "$plistPath" -p ios "$dsymPath"
    fi
}

cd "$projectPath"

if [ "$buildType" == "debug" ]; then
    ipaPath="$projectPath/build/ios/ipa/Partying.ipa"
    if [ -d "$projectPath/build/ios" ]; then
        rm -rf "$projectPath"/build/ios
    fi
    if [[ "$debugModel" == "enable" ]]; then
        flutter build ios --profile --build-number "$versionCode" --build-name "$versionName" --dart-define=DEBUG_MODE=true --dart-define=CI_NUM="$ciNum"
    else
        # shellcheck disable=SC2086
        flutter build ios --profile --build-number $versionCode --build-name $versionName --dart-define=DEBUG_MODE=false
    fi
    cd ios
    bundle exec fastlane ios test

    if [ -f "$ipaPath" ]; then
        curl -O -F "file=@${ipaPath}" -F '_api_key=f81f472078152a37cdcd1f56f8697147' https://www.pgyer.com/apiv2/app/upload
    fi
elif [ "$buildType" == "release" ]; then
    ipaPath="$projectPath/build/ios/ipa/Partying.ipa"
    if [ -d "$projectPath/build/ios" ]; then
        rm -rf "$projectPath"/build/ios
    fi

    if [[ "$debugModel" == "enable" ]]; then
        # shellcheck disable=SC2086
        flutter build ios --release --build-number $versionCode --build-name $versionName --dart-define=DEBUG_MODE=true --dart-define=CI_NUM="$ciNum"
    else
        flutter clean
        # shellcheck disable=SC2086
        flutter build ios --release --build-number $versionCode --build-name $versionName --dart-define=DEBUG_MODE=false
    fi
    cd ios
    bundle exec fastlane ios test
    if [ -f "$ipaPath" ]; then
        curl -O -F "file=@${ipaPath}" -F '_api_key=f81f472078152a37cdcd1f56f8697147' https://www.pgyer.com/apiv2/app/upload
    fi
else
    buildStore
fi
