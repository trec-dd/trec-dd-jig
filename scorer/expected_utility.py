"""
Expected Utility
Copyright 2017 @ Georgetown University
"""
from truth import *
from reader import *
from collections import Counter, defaultdict
import statistics
import sys
import argparse

PROB = defaultdict(dict)


def eu(run_file_path, truth_xml_path, dd_info_path, cutoff=10, a=0.001, gamma=0.5, p=0.5, verbose=False):
    """

    :param run_file_path:
    :param truth_xml_path:
    :param dd_info_path:
    :param cutoff: only the first #cutoff iterations will be calculated (namely, K in the paper)
    :param a: coefficient of cumulative cost
    :param gamma: discount for duplicated nugget
    :param p: probability of stopping at any position given a ranked list ( geometric distribution part in the paper)
    :param verbose: if true, print info on stdout
    :return:
    """
    PROB.clear()

    truth = DDTruth(truth_xml_path, dd_info_path)
    run_result = DDReader(run_file_path).run_result

    if verbose:
        print(run_file_path)
        print('%8s' % 'topic-id', '%10s' % ('EU@' + str(cutoff)), '%10s' % ('nEU@' + str(cutoff)),
              sep='\t')

    # sort run result by topic id
    sorted_results = sorted(run_result.items(), key=lambda x: int(x[0].split('-')[1]))

    utility_list = []
    normalized_eu_list = []
    for topic_id, topic_result in sorted_results:
        topic_truth = truth.truth4EU(topic_id)

        utility = eu_per_topic(topic_truth, topic_result, a, gamma, p, cutoff)


        upper, lower = eu_bound_per_topic(truth.truth4EU_bound(topic_id), a, gamma, p, cutoff)
        normalized_eu = (utility - lower) / (upper - lower)
        normalized_eu_list.append(normalized_eu)

        utility_list.append(utility)
        if verbose:
            print('%8s' % topic_id, '%10.7f' % utility, '%10.7f' % normalized_eu, sep='\t')

    if verbose:
        print('%8s' % 'all', '%10.7f' % statistics.mean(utility_list), '%10.7f' % statistics.mean(normalized_eu_list),
              sep='\t')

    return utility_list


def eu_per_topic(topic_truth, topic_result, a, gamma, p, cutoff):
    doc_nugget, nugget_rating, doc_length = topic_truth
    utility = expected_gain_per_topic(topic_result, doc_nugget, nugget_rating, cutoff, gamma, p) \
              - a * expected_cost_per_topic(topic_result, doc_length, cutoff, p)
    return utility


def prob_stop_at_s(p, s, l):
    """probability of stopping at s given the total length l"""
    if s in PROB:
        if l in PROB[s]:
            return PROB[s][l]

    if s < l:
        v = ((1 - p) ** (s - 1)) * p
    else:
        k = 0
        for i in range(1, l):
            k += ((1 - p) ** (i - 1)) * p
        v = 1 - k

    PROB[s][l] = v
    return v


def expected_gain_per_topic(topic_result, doc_nugget, nugget_rating, cutoff, gamma, p):
    """ following Part 4 of the paper"""

    expected_appear = defaultdict(
        float)  # expected appearance times of different nuggets in the first #cutoff iterations

    sorted_result = sorted(topic_result.items(), key=lambda x: x[0])

    for iter_num, doc_list in sorted_result:  # attention!! iter_num starts from 0
        # iter_num is actually k in the paper, doc_list is l_k
        if iter_num >= cutoff:
            break
        l = len(doc_list)
        for s in range(1, l + 1):
            prob = prob_stop_at_s(p, s, l)

            # count nuggets in the first s docs of current doc_list
            # (m function in the formula (14) of the paper)
            m = Counter()

            for i in range(s):
                m.update(doc_nugget[doc_list[i]])

            for nugget in m.keys():
                expected_appear[nugget] += prob * m[nugget]

    expected_gain = 0
    for nugget, expected_time in expected_appear.items():
        expected_gain += nugget_rating[nugget] * (1 - gamma ** expected_time) / (1 - gamma)

    return expected_gain


def expected_cost_per_topic(topic_result, doc_length, cutoff, p):
    total_len = 0

    sorted_result = sorted(topic_result.items(), key=lambda x: x[0])
    for iter_num, doc_list in sorted_result:
        if iter_num >= cutoff:
            break
        l = len(doc_list)

        cumulated_len = 0
        expected_len = 0
        for s in range(1, l + 1):
            if doc_list[s - 1] not in doc_length:
                # print(doc_list[s - 1])
                continue
            cumulated_len += doc_length[doc_list[s - 1]]
            prob = prob_stop_at_s(p, s, l)
            expected_len += (prob * cumulated_len)

        total_len += expected_len

    return total_len

def eu_bound_per_topic(topic_truth, a, gamma, p, cutoff):
    """
    return the upper bound of expected utility score in the first $(cutoff) iterations
    :param topic_truth: doc_no : rating
    :param a: coefficient of cost
    :param gamma: discount base
    :param p: probability of stopping at each document
    :param cutoff: iteration that stops at
    :return: upper bound and lower bounds for EU score in the first $(cutoff) iterations
    """
    M = 1 + (1 - p) + (1 - p) ** 2 + (1 - p) ** 3 + (1 - p) ** 4
    nugget_doc, nugget_rating, doc_length = topic_truth
    upper_bound = 0
    for nugget_id, nugget_rel in nugget_rating.items():
        l = min(5 * cutoff, len(nugget_doc[nugget_id]))  # max number of docs that can be related to this subtopic
        s = (l // 5) * M  # gain from complete document ranking list
        base = 1
        for _ in range(l % 5):
            s += base
            base *= (1 - p)

        upper_bound += nugget_rel * (1 - gamma ** s)
    upper_bound = upper_bound / (1 - gamma)

    # doc_len = sorted(doc_length.items(), key=lambda x: x[1])  # sort in ascending order
    forward_iter = iter(doc_length)
    backward_iter = reversed(doc_length)
    min_cost = 0
    max_cost = 0
    # print(doc_len)
    l = min(len(doc_length), 5 * cutoff)
    last = l % 5  # position of the last document in the last ranking list, start from 0
    ct = 0
    for doc_rank in range(5):
        if doc_rank <= last:
            k = cutoff
        else:
            k = cutoff - 1
        # print(doc_rank, k)
        for query_rank in range(k):
            # print(ct)
            _, min_doc_cost = next(forward_iter)
            _, max_doc_cost = next(backward_iter)
            min_cost += (1 - p) ** doc_rank * min_doc_cost
            max_cost += (1 - p) ** doc_rank * max_doc_cost
            ct += 1
            # print(ct, l)
            if ct == l:
                break
        if ct == l:
            break
    upper_bound -= a * min_cost
    lower_bound = - a * max_cost

    return upper_bound, lower_bound

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--runfile", required=True, help="run file path")
    parser.add_argument("--topics", required=True, help="topic xml file path")
    parser.add_argument("--params", required=True, help="file containing parameters for evaluation")
    parser.add_argument("--cutoff", required=True, type=int, help="first # iterations are taken into evaluation")

    params = parser.parse_args(sys.argv[1:])

    if params.cutoff <= 0:
        parser.error("cutoff value must be greater than 0")

    eu(params.runfile, params.topics, params.params, cutoff=params.cutoff, verbose=True)
    # eu('../sample_run/runfile', '../sample_run/topic.xml', '../sample_run/doc_len.json', cutoff=10, verbose=True)
