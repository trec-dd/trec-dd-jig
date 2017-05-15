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
    can_normalize = False
    if cutoff <= 10:
        can_normalize = True
    if verbose:
        print(run_file_path)
        if can_normalize:
            print('topic_id', 'eu@' + str(cutoff), 'normalized_eu@' + str(cutoff), sep='\t')
        else:
            print('topic_id', 'eu@' + str(cutoff), sep='\t')
    truth = DDTruth(truth_xml_path, dd_info_path)
    run_result = DDReader(run_file_path).run_result

    # sort run result by topic id
    sorted_results = sorted(run_result.items(), key=lambda x: int(x[0].split('-')[1]))

    utility_list = []
    normalized_eu_list = []
    for topic_id, topic_result in sorted_results:
        topic_truth = truth.truth4EU(topic_id)

        utility = eu_per_topic(topic_truth, topic_result, a, gamma, p, cutoff)

        normalized_eu = None

        if can_normalize:
            upper, lower = truth.eu_bound[topic_id][cutoff]
            normalized_eu = (utility - lower) / (upper - lower)
            normalized_eu_list.append(normalized_eu)

        utility_list.append(utility)
        if verbose:
            if can_normalize:
                print(topic_id, utility, normalized_eu, sep='\t')
            else:
                print(topic_id, utility, sep='\t')

    if verbose:
        if can_normalize:
            print(topic_id, statistics.mean(utility_list), statistics.mean(normalized_eu_list), sep='\t')
        else:
            print('all', statistics.mean(utility_list), sep='\t')
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
                print(doc_list[s - 1])
                continue
            cumulated_len += doc_length[doc_list[s - 1]]
            prob = prob_stop_at_s(p, s, l)
            expected_len += (prob * cumulated_len)

        total_len += expected_len

    return total_len


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--runfile", required=True, help="run file path")
    parser.add_argument("--topics", required=True, help="topic xml file path")
    parser.add_argument("--dd-info-pkl", required=True, help="pickle file containing document length and bounds")
    parser.add_argument("--cutoff", required=True, type=int, help="first # iterations are taken into evaluation")

    params = parser.parse_args(sys.argv[1:])

    eu(params.runfile, params.topics, params.dd_info_pkl, cutoff=params.cutoff, verbose=True)
    # eu('../sample_run/runfile', '../sample_run/topic.xml', '../sample_run/doc_len.json', cutoff=10, verbose=True)
