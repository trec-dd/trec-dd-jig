"""
Jig configuration of TREC 2017 DD
Copyright 2017 @ Georgetown University
"""

import sys

import argparse
from setup_db import *
from doc_len import *
import pickle
import json


def main():
    parser = argparse.ArgumentParser()

    # topic.xml file
    parser.add_argument("--topics", required=True, help="topic xml file path")

    # trectext directories
    parser.add_argument("--trecdirec", nargs='+', required=True, help="directories of trectext files")

    # info.pkl path
    parser.add_argument("--params", required=True, help="file containing parameters for evaluation")

    params = parser.parse_args(sys.argv[1:])

    print("Setting up the databse ... ")
    setup_db(params.topics)

    print("Computing the document length ... ")
    doc_length = doc_len(params.trecdirec)
    # doc_length = json.load(open("sample_run/doc_len.json"))

    print("Dumping ...")
    pickle.dump(doc_length, file=open(params.params, 'wb'))

    print("Done!")


if __name__ == "__main__":
    main()
