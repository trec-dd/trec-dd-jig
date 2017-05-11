"""
sDCG
https://pdfs.semanticscholar.org/eaf0/44e9f8fef5f9dacdfc609668f4697842e8e7.pdf
"""
from reader import *
from truth import *
import math
import statistics


def sDCG(run_file_path, truth_xml_path, bq=4, b=2, cutoff=10, verbose=False):
    """
    :param run_file_path:
    :param truth_xml_path:
    :param bq: discount base of query in a session
    :param b: discount base of docs returned by a query
    :param query_pos: the position (in the session) of the query that needs to be calculated (starting from 1)
    :return: average sDCG and nDCG over all topics
    """
    if verbose:
        print(run_file_path)
        print('topic-id', 'sDCG', 'nsDCG', sep='\t')
    truth = DDTruth(truth_xml_path)
    run_result = DDReader(run_file_path).run_result
    sorted_results = sorted(run_result.items(), key=lambda x: int(x[0].split('-')[1]))

    sdcg_list, nsdcg_list = [], []
    for topic_id, topic_result in sorted_results:
        topic_truth = truth.truth_4_sDCG(topic_id)
        sdcg, nsdcg = sDCG_per_topic(topic_truth, topic_result, bq, b, cutoff)
        sdcg_list.append(sdcg)
        nsdcg_list.append(nsdcg)
        """
        if not math.isnan(sdcg):
            total_sdcg += sdcg
        if not math.isnan(nsdcg):
            total_nsdcg += nsdcg
        """
        if verbose:
            print(topic_id, sdcg, nsdcg, sep='\t')

    if verbose:
        print('all', statistics.mean(sdcg_list), statistics.mean(nsdcg_list))
    return sdcg_list, nsdcg_list


def sDCG_per_topic(topic_truth, topic_result, bq, b, cutoff):
    """return sDCG and nsDCG of one topic"""

    sorted_result = sorted(topic_result.items(), key=lambda x: x[0])
    sdcg, isdcg = 0, 0
    for query_pos, doc_list in sorted_result:  # query position starts from 0
        if query_pos >= cutoff:
            break

        query_discount = 1 + math.log(query_pos + 1, bq)
        for doc_pos, doc_no in enumerate(doc_list):  # doc position also starts from 0
            sdcg += topic_truth[doc_no] / (1 + math.log(doc_pos + 1, b)) / query_discount
        ideal_doclist = sorted(doc_list, key=lambda x: topic_truth[x], reverse=True)
        for doc_pos, doc_no in enumerate(ideal_doclist):
            isdcg += topic_truth[doc_no] / (1 + math.log(doc_pos + 1, b)) / query_discount
    if isdcg <= 0.000000000000001 and isdcg >= -0.000000000000001:  # ideal_sdcg = sdcg =0
        assert sdcg == isdcg
        return sdcg, 1
    else:
        return sdcg, sdcg / isdcg


if __name__ == '__main__':
    sDCG('data/trec_dd_16/runs/UL_LDA_200', 'data/trec_dd_16/truth/dynamic-domain-2016-truth-data.xml', cutoff=1)
