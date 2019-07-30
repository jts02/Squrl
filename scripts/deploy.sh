#! /bin/bash

case $CODEBUILD_INITIATOR in
    codepipeline/squrl)
        echo do epic shit
        ;;
    *)
        echo do epic shit in a default manner
        ;;
esac
