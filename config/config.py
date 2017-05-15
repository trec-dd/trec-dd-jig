"""
Jig configuration of TREC 2017 DD
Copyright 2017 @ Georgetown University
"""


import sys

import argparse
from .setup_db import *
from .doc_len import *
from .bound import get_bound
import json




def main():
    parser = argparse.ArgumentParser()

    # topic.xml file
    parser.add_argument("--topics", required=True, help="topic xml file path")

    # trectext directories
    parser.add_argument("--trecdirec", nargs='+', required=True, help="directories of trectext files")

    # info.json path
    parser.add_argument("--output", required=True, help="json file containing document length and bounds")

    params = vars(parser.parse_args(sys.argv[1:]))
    setup_db(params['topics'])
    doc_length = doc_len(params['trecdirec'])
    sdcg, ct, eu = get_bound()
    json.dump([doc_length, sdcg, ct, eu], fp=open(params['output'], 'w'))



if __name__ == "__main__":
    main()
