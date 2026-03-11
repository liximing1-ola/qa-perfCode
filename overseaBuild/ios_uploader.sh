#!/usr/bin/env bash
#!/usr/local/bin

apiKey="6B93LS89J7" #this private key is only developr role, move the priavte keys to HOME
apiIssuer="5d0506b3-c4f1-4ce3-b34e-845de814f1ef"

function upload_ipa() {
    local ipa_file=${1}
    # shellcheck disable=SC2154
    if [ ! -f "$ipa" ];then
        echo -e "033[31m file $ipa_file not exists \033[0m"
        return 
    fi

  upload="xcrun altool --upload-app -f $ipa_file -t iOS --apiKey $apiKey --apiIssuer $apiIssueq!A`q` r --verbose"
    echo "run upload cmd" "$upload"
    uploadApp="$($upload)"
    echo uploadApp
    if [ -z "$uploadApp" ]; then
        echo -e "\033[31m upload failed \033[0m"
    else
        echo -e "\033[46;30m upload success \033[0m"
    fi
}

function validate_and_upload(){
    local ipa_file=${1}
    if [ ! -f "$ipa" ];then
        echo -e "033[31m file $ipa_file not exists \033[0m" 
        return 
    fi


    validate="xcrun altool --validate-app -f $ipa_file -t iOS --apiKey $apiKey --apiIssuer $apiIssuer --verbose"
    echo "running validate cmd" "$validate"

    runValidate="$($validate)"
    echo "$runValidate"

    if [ -z "$runValidate" ]; then
        echo -e "033[31m validate failed \033[0m"
    else
        upload_ipa "$ipa_file"
    fi
}



function enter_api_key() {
    if [ -z "$1" ]; then
        echo -e "\033[31m Please enter apiKey \033[0m"
        # shellcheck disable=SC2162
        read key
        # shellcheck disable=SC2233
        while ([ -z "$key" ]); do
            echo -e "\033[31m Please enter apiKey \033[0m"
            # shellcheck disable=SC2162
            read key
        done
        apiKey=$key
    else
        apiKey=$1
    fi

    if [ -z "$2" ]; then
        echo -e "\033[31m Please enter apiIssuer \033[0m"
        # shellcheck disable=SC2162
        read issuer
        # shellcheck disable=SC2233
        while ([ -z "$issuer" ]); do
            echo -e "\033[31m Please enter apiIssuer \033[0m"
            # shellcheck disable=SC2162
            read issuer
        done
        apiIssuer=$issuer
    else
    apiIssuer=$2
    fi

    echo -e "\033[46;30m apiKey is: $apiKey -- apiIssuer is: $apiIssuer \033[0m"
}