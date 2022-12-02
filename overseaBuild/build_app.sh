buildPlatform=$1
buildType=$2
versionName=$3
versionCode=$4
debugModel=$5
releaseNotes=$6
ciNum=$7
buildUser=$8
buildBranch=$9

projectPath=$(dirname "$PWD")

last_build_info="$projectPath/ci/build/last_build.txt"
last_commit_id="$projectPath/ci/build/last_commit_id.txt"
last_branch_commit_id="$projectPath/ci/build/${versionName}_commit_id.txt"

if [ ! -d "$projectPath/ci/build/" ]; then
    mkdir $projectPath/ci/build
fi

echo "" >$last_commit_id

build_info="version: $versionName"

# save last_base_commit of submodule banban_base
last_commit=$(git log -1 --pretty=%h)
# save the last commit for rollback
echo "$last_commit" >$last_commit_id

if [ -f "$last_branch_commit_id" ]; then
    last_commit="$(cat $last_branch_commit_id)"
fi

# send success msg to wecom
python3 wechat_notify.py 0 "Start Building $ciNum 号包..." "" "" "" "" 0 "$buildUser" "$buildBranch"

apkPath="$projectPath/build/app/outputs/apk/partying_${buildType}_${ciNum}.apk"
ipaPath="$projectPath/build/ios/ipa/Partying.ipa"
if [ $buildPlatform == 'Android' ]; then
    ./build_apk.sh $buildType $versionName $versionCode $debugModel "$releaseNotes" $ciNum
    if [ $buildType == 'store' ];then
        bundlePath="$projectPath/build/app/outputs/bundle/partying_$versionName.aab"
        if [[ ! -f $bundlePath ]]; then
            msg="**Android 打包失败**，[请检查](http://ola.nat300.top/job/Package%20App/)"
            python3 wechat_notify.py -1 "$msg" '' '' "" "" 0 "$buildUser" "$buildBranch"
            exit 1
        fi
    elif [[ ! -f $apkPath ]]; then
        msg="**Android 打包失败**，[请检查](http://ola.nat300.top/job/Package%20App/)"
        python3 wechat_notify.py -1 "$msg" '' '' "" "" 0 "$buildUser" "$buildBranch"
        exit 1
    fi
elif [ $buildPlatform == 'iOS' ]; then
    ./build_ipa.sh $buildType $versionName $versionCode $debugModel "$releaseNotes" $ciNum
    if [[ ! -f "$ipaPath" ]]; then
        msg="**iOS 打包失败**，[请检查](http://ola.nat300.top/job/Package%20App/)"
        python3 wechat_notify.py -1 "$msg" '' '' "" "" 0 "$buildUser" "$buildBranch"
        exit 1
    fi
else
    errorCount=0
    ./build_apk.sh $buildType $versionName $versionCode $debugModel "$releaseNotes" $ciNum
    if [ $buildType == 'store' ];then
        bundlePath="$projectPath/build/app/outputs/bundle/partying_$versionName.aab"
        if [[ ! -f $bundlePath ]]; then
            msg="**Android 打包失败**，[请检查](http://ola.nat300.top/job/Package%20App/)"
            python3 wechat_notify.py -1 "$msg" '' '' "" "" 0 "$buildUser" "$buildBranch"
            errorCount=$((errorCount + 1))
            exit 1
        fi
    elif [[ ! -f $apkPath ]]; then
        msg="**Android 打包失败**，[请检查](http://ola.nat300.top/job/Package%20App/)"
        python3 wechat_notify.py -1 "$msg" '' '' "" "" 0 "$buildUser" "$buildBranch"
        errorCount=$((errorCount + 1))
        exit 1
    fi

    ./build_ipa.sh $buildType $versionName $versionCode $debugModel "$releaseNotes" $ciNum
    if [[ ! -f "$ipaPath" ]]; then
        msg="**iOS 打包失败**，[请检查](http://ola.nat300.top/job/Package%20App/)"
        python3 wechat_notify.py -1 "$msg" '' '' "" "" 0 "$buildUser" "$buildBranch"
        errorCount=$((errorCount + 1))
    fi
    if [ $errorCount -ge 2];then
        exit 1
    fi
fi

lastest_commit=$(git log -1 --pretty=%h)
CHANGE_LOG=$(git shortlog --pretty=format:"- **%s** %ar" $last_commit..$lastest_commit)

# send success msg to wecom
python3 wechat_notify.py $versionCode "$CHANGE_LOG" $buildType $versionName "$buildPlatform" "$build_info" $ciNum "$buildUser" "$buildBranch"

# save the latest commit id into local file.
last_commit=$(git log -1 --pretty=%h)
echo "$last_commit" >$last_branch_commit_id