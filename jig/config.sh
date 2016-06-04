#!/bin/bash

if [ "$1" = "--topics" ]
then
    #python setup_db.py $2
    python jig/setup_db.py $2
    #python scorer/generate_qrel.py $2 > scorer/qrel.txt
else
    echo "Usage: sh ./config.sh --topics <yourtopicfile.xml>"
    echo ""
    echo "yourtopicfile.xml: specifies the path of the truth data XML file"
fi

