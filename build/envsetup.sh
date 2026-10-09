BUILD_PATH=$(cd "$(dirname "$BASH_SOURCE")" && pwd)

pathadd() {
    if [ -d "$1" ] && [[ ":$PATH:" != *":$1:"* ]]; then
        PATH="$1${PATH:+":$PATH"}"
    fi
}
pathadd "$BUILD_PATH"
