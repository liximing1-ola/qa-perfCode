# test if the branch is in the local repository.
# return 1 if the branch exists in the local, or 0 if not.
function branch_is_in_local() {
    local branch=${1}
    local git_dir='./.git/'
    
    # if $2 is set, git_dir=$2
    [ -z "${2}" ] || git_dir=${2}

    # shellcheck disable=SC2155
    # shellcheck disable=SC2006
    local existed_in_local=`git --git-dir "${git_dir}" branch --list "${branch}"`
    if [[ -z ${existed_in_local} ]]; then
        echo 0
    else
        echo 1
    fi
}

# test if the branch is in the remote repository.
# return 1 if its remote branch exists, or 0 if not.
function branch_is_in_remote() {
    local branch=${1}
    local git_dir='./.git/'
    
    # if $2 is set, git_dir=$2
    [ -z "${2}" ] || git_dir=${2}

    # shellcheck disable=SC2155
    local existed_in_remote=$(git --git-dir "${git_dir}" ls-remote --heads origin "${branch}")

    if [[ -z ${existed_in_remote} ]]; then
        echo 0
    else
        echo 1
    fi
}

# test if the branch is in the remote repository.
# return 1 if its remote branch exists, or 0 if not.
function is_branch_exist() {
    local branch=${1}
    local git_dir='./.git/'
    
    # if $2 is set, git_dir=$2
    [ -z "${2}" ] || git_dir=${2}

    retval=1
    # shellcheck disable=SC2086
    branch_exist=$( branch_is_in_local $BRANCH_NAME $git_dir)
    if [[ $branch_exist == 0 ]]; then
        # shellcheck disable=SC2086
        branch_exist=$( branch_is_in_remote "$BRANCH_NAME" $git_dir)
        if [[ $branch_exist == 0 ]]; then
            retval=0
        fi
    fi

    echo $retval
}


function checkout_and_pull() {
    local branch=${1}
    local git_dir='./.git/'

    # if $2 is set, git_dir=$2
    [ -z "${2}" ] || git_dir=${2}

    # clear all local changes
    git --git-dir "$git_dir" checkout .
    # shellcheck disable=SC2086
    git --git-dir $git_dir clean -df

    # fetch new branch that might not in local
    git --git-dir "$git_dir" fetch origin "$branch"

    # force to checkout the $branch
    # shellcheck disable=SC2086
    git --git-dir $git_dir checkout -f $branch

    # clear all changes inclueds by checkouting new branch
    git --git-dir "$git_dir" checkout .
    # shellcheck disable=SC2086
    git --git-dir $git_dir clean -df

    # pull the new changes into local
    # shellcheck disable=SC2086
    git --git-dir $git_dir pull origin $branch --progress -v
} 