import argparse
import sys
import truth, reader, sDCG, cubetest, expected_utility



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runfile", required=True, help="run file path")
    parser.add_argument("--topics", required=True, help="topic xml file path")
    parser.add_argument("--doc-len", required=True, help="document length json file path")
    parser.add_argument("--metric", nargs='+')












