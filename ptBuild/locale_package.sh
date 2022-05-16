#!/usr/bin/env bash
projectPath=`pwd`

read -p "打包平台：1.All  2.Android 3.iOS : " buildPlatform
read -p "BuildType：1.debug  2.release 3.store : " buildType
read -p "versionName: " versionName
read -p "versionCode: " versionCode
read -p "EnableDebug: 1.enable 2.disable" debugModel
read -p "CI_NUM: " ciNum
if [ $buildType = 3 ]
then
read -p "releaseNotes: " releaseNotes
fi

#declare -A platformMap
platformMap=(["1"]="All" ["2"]="Android" ["3"]="iOS")
#declare -A typeMap
typeMap=(["1"]="debug" ["2"]="release" ["3"]="store")

releaseNotes="Happy New Year  Partyingers !\nBug fixes and improvements."

echo ${platformMap[*]}
echo "$releaseNotes"

./build_app.sh ${platformMap[$buildPlatform]} ${typeMap[$buildType]} $versionName $versionCode $debugModel "$releaseNotes" $ciNum
