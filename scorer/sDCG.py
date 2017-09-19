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


def sDCG(run_file_path, truth_xml_path, dd_info_path, bq=4, b=2, cutoff=10, verbose=False):
    """
    :param run_file_path:
    :param truth_xml_path:
    :param dd_info_path
    :param bq: discount base of query in a session
    :param b: discount base of docs returned by a query
    :param cutoff: number of iterations taken into evaluation
    :param verbose: if print verbose information
    :return: average sDCG and nDCG over all topics
    """
    truth = DDTruth(truth_xml_path, dd_info_path)
    run_result = DDReader(run_file_path).run_result

    if verbose:
        print(run_file_path)
        print('%8s' % 'topic-id', '%10s' % ('sDCG@' + str(cutoff)), '%10s' % ('nsDCG@' + str(cutoff)), sep='\t')

    # sort by topic no
    sorted_results = sorted(run_result.items(), key=lambda x: int(x[0].split('-')[1]))

    sdcg_list = []
    nsdcg_list = []
    for topic_id, topic_result in sorted_results:
        topic_truth = truth.truth4SDCG(topic_id)

        sdcg = sDCG_per_topic(topic_truth, topic_result, bq, b, cutoff)

        bound = sDCG_bound_per_topic(truth.truth4SDCG_bound(topic_id), bq, b, cutoff)

        normalized_sdcg = sdcg / bound
        nsdcg_list.append(normalized_sdcg)

        sdcg_list.append(sdcg)

        if verbose:
            print('%8s' % topic_id, '%10.7f' % sdcg, '%10.7f' % normalized_sdcg, sep='\t')

    if verbose:
        print('%8s' % 'all', '%10.7f' % statistics.mean(sdcg_list), '%10.7f' % statistics.mean(nsdcg_list), sep='\t')

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


def sDCG_bound_per_topic(topic_truth, bq, b, cutoff):
    """
    return the optimal sDCG value given the iteration cutoff value
    :param topic_truth: doc_no : rating
    :param bq: discounting base for the query
    :param b: discounting base for the document within each query
    :param cutoff: iteration that stops at
    :return: optimal sDCG score in the first $(cutoff) iterations
    """
    pos_list = []
    for query_rank in range(cutoff):
        for doc_rank in range(5):
            pos_list.append((query_rank + 1, doc_rank + 1))

    pos_list = sorted(pos_list, key=lambda x: 1 / ((1 + math.log(x[1], b)) * (1 + math.log(x[0], bq))), reverse=True)
    dis_list = map(lambda x: 1 / ((1 + math.log(x[1], b)) * (1 + math.log(x[0], bq))), pos_list)

    # sort in desc by relevance scores of each document
    doc_rels = sorted(topic_truth.items(), key=lambda x: x[1], reverse=True)

    optimal_score = 0

    for pos, doc_rel, discount in zip(pos_list, doc_rels, dis_list):
        optimal_score += doc_rel[1] * discount

    return optimal_score


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--runfile", required=True, help="run file path")
    parser.add_argument("--topics", required=True, help="topic xml file path")
    parser.add_argument("--params", required=True, help="file containing parameters for evaluation")
    parser.add_argument("--cutoff", required=True, type=int, help="first # iterations are taken into evaluation")

    params = parser.parse_args(sys.argv[1:])

    if params.cutoff <= 0:
        parser.error("cutoff value must be greater than 0")

    sDCG(params.runfile, params.topics, params.params, cutoff=params.cutoff, verbose=True)

    # sDCG('../sample_run/runfile', '../sample_run/topic.xml', cutoff=10, verbose=True)
