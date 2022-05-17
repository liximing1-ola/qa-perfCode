# curdir=$(pwd)
# dir=$curdir/test
# echo $dir
# export PATH=$PATH:$curdir/test
# echo $PATH
# # text="what is your name?"
# # python3 upload_apks_with_listing.py com.imbb.oversea.android pt_178.aab test "$text"
read -p $'选择应用： \n1.Partying 2.Party Stars ：' app
read -p "草稿名称 ：" drafName
read -p "Bundle路径： ：" bundlePath
# read -p $'ReleaseNotes ：\n'
# read -r releaseNotes 
releaseNotes='''To make Party Stars work better for you, we deliver updates regularly. These updates include bug fixes and improvements for speed and reliability.'''

package="com.imbb.oversea.android"
if [ $app = 1 ]
then
package="com.imbb.oversea.android"
elif [ $app = 2 ]
then
package="sg.partying.lcb.android"
fi

python3 upload_apks_with_listing.py $package $bundlePath $drafName "$releaseNotes" 
