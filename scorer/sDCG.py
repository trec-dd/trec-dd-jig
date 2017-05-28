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

    can_normalize = False
    if cutoff <= truth.max_cutoff:
        can_normalize = True

    if verbose:
        print(run_file_path)
        if can_normalize:
            print('topic-id', 'sDCG@' + str(cutoff), 'normalized sDCG@' + str(cutoff), sep='\t')
        else:
            print('topic-id', 'sDCG@' + str(cutoff), sep='\t')

    # sort by topic no
    sorted_results = sorted(run_result.items(), key=lambda x: int(x[0].split('-')[1]))

    sdcg_list = []
    nsdcg_list = []
    for topic_id, topic_result in sorted_results:
        topic_truth = truth.truth4SDCG(topic_id)
        sdcg = sDCG_per_topic(topic_truth, topic_result, bq, b, cutoff)

        normalized_sdcg = None
        if can_normalize:
            bound = truth.sdcg_bound[topic_id][cutoff]
            normalized_sdcg = sdcg / bound
            nsdcg_list.append(normalized_sdcg)

        sdcg_list.append(sdcg)

        if verbose:
            if can_normalize:
                print(topic_id, sdcg, normalized_sdcg, sep='\t')
            else:
                print(topic_id, sdcg, sep='\t')

    if verbose:
        if can_normalize:
            print('all', statistics.mean(sdcg_list), statistics.mean(nsdcg_list))
        else:
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
    parser.add_argument("--dd-info-pkl", required=True, help="pickle file containing document length and bounds")
    parser.add_argument("--cutoff", required=True, type=int, help="first # iterations are taken into evaluation")

    params = parser.parse_args(sys.argv[1:])

    if params.cutoff <= 0:
        parser.error("cutoff value must be greater than 0")

    sDCG(params.runfile, params.topics, params.dd_info_pkl, cutoff=params.cutoff, verbose=True)

    # sDCG('../sample_run/runfile', '../sample_run/topic.xml', cutoff=10, verbose=True)
