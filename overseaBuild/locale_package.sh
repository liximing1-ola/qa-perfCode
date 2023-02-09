#!/usr/bin/env bash
projectPath=`pwd`

# shellcheck disable=SC2162
read -p "打包平台：1.All  2.Android 3.iOS : " buildPlatform
# shellcheck disable=SC2162
read -p "BuildType：1.debug  2.release 3.store : " buildType
# shellcheck disable=SC2162
read -p "versionName: " versionName
# shellcheck disable=SC2162
read -p "versionCode: " versionCode
# shellcheck disable=SC2162
read -p "EnableDebug: 1.enable 2.disable" debugModel
# shellcheck disable=SC2162
read -p "CI_NUM: " ciNum
if [ "$buildType" = 3 ]
then
read -p "releaseNotes: " releaseNotes
fi

#declare -A platformMap
platformMap=(["1"]="All" ["2"]="Android" ["3"]="iOS")
#declare -A typeMap
typeMap=(["1"]="debug" ["2"]="release" ["3"]="store")

releaseNotes="Happy New Year  Partyingers !\nBug fixes and improvements."

echo "${platformMap[*]}"
echo "$releaseNotes"

./build_app.sh "${platformMap[$buildPlatform]}" "${typeMap[$buildType]}" "$versionName" "$versionCode" "$debugModel" "$releaseNotes" "$ciNum"
