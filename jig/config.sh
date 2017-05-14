#!/bin/bash

if [ "$1" = "--topics" ]
then
    python jig/setup_db.py $2

else
    echo "Usage: sh ./config.sh --topics <yourtopicfile.xml>"
    echo ""
    echo "yourtopicfile.xml: specifies the path of the truth data XML file"
fi

