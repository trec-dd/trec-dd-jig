"""
sDCG
Copyright 2017 @ Georgetown University
"""
from reader import *
from truth import *
import math
import statistics
import sys
import argparse

def sDCG(run_file_path, truth_xml_path, bq=4, b=2, cutoff=10, verbose=False):
    """
    :param run_file_path:
    :param truth_xml_path:
    :param bq: discount base of query in a session
    :param b: discount base of docs returned by a query
    :param cutoff: number of iterations taken into evaluation
    :param verbose: if print verbose information
    :return: average sDCG and nDCG over all topics
    """
    if verbose:
        print(run_file_path)
        print('topic-id', 'sDCG', sep='\t')
    truth = DDTruth(truth_xml_path)
    run_result = DDReader(run_file_path).run_result

    # sort by topic no
    sorted_results = sorted(run_result.items(), key=lambda x: int(x[0].split('-')[1]))

    sdcg_list = []
    for topic_id, topic_result in sorted_results:
        topic_truth = truth.truth4SDCG(topic_id)
        sdcg = sDCG_per_topic(topic_truth, topic_result, bq, b, cutoff)
        sdcg_list.append(sdcg)

        if verbose:
            print(topic_id, sdcg, sep='\t')

    if verbose:
        print('all', statistics.mean(sdcg_list))

    return sdcg_list

def sDCG_per_topic(topic_truth, topic_result, bq, b, cutoff):
    """return sDCG of one topic"""

    sorted_result = sorted(topic_result.items(), key=lambda x: x[0])  # sort by iterations
    sdcg = 0
    for query_pos, doc_list in sorted_result:  # query position starts from 0
        if query_pos >= cutoff:
            break
        query_discount = 1 + math.log(query_pos + 1, bq)
        for doc_pos, doc_no in enumerate(doc_list):  # doc position also starts from 0
            sdcg += topic_truth[doc_no] / (1 + math.log(doc_pos + 1, b)) / query_discount
        return sdcg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--runfile", required=True, help="run file path")
    parser.add_argument("--topics", required=True, help="topic xml file path")
    parser.add_argument("--cutoff", required=True, type=int, help="first # iterations are taken into evaluation")

    params = parser.parse_args(sys.argv[1:])
    sDCG(params.runfile, params.topics, cutoff=params.cutoff, verbose=True)

    # sDCG('../sample_run/runfile', '../sample_run/topic.xml', cutoff=10, verbose=True)
