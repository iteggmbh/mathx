#!/bin/sh
#
# Build and possible run docker image in development
#

cd $(dirname $0)

do_run=0
do_npm=0

while test $# -gt 0
do
    case $1 in
        -r|--run)
            do_run=1
            shift
            ;;
        -n|--npm)
            do_npm=1
            shift
            ;;
        *)
            echo "Unknown option $1"
            exit 64
            ;;
    esac
done

if test $do_npm -eq 1
then
    echo '***** Building mathx npm package...'

    rm -rf web/dist
    (cd web && npm ci)
    (cd web && npm run build)
fi

echo '***** Building mathx docker image...'

rm -rf $(find src -name __pycache__ )

docker build -t mathx:latest .

if test $? -eq 0
then
    echo '***** Sucessfully built mathx docker image.'
    if test $do_run -eq 1
    then
        echo '***** Running mathx development setup.'
        docker run --rm -p 8011:8011 mathx:latest
    fi
else
    echo '***** Failed to build mathx docker image.'
fi
