"""
Expected Utility
Copyright 2017 @ Georgetown University
"""
from .truth import *
from .reader import *
from collections import Counter
import statistics
import sys

PROB = defaultdict(dict)


def eu(run_file_path, truth_xml_path, doc_length_path, cutoff=10, a=0.000005, gamma=0.5, p=0.5, verbose=False):
    """

    :param run_file_path:
    :param truth_xml_path:
    :param cutoff: only the first #cutoff iterations will be calculated (namely, K in the paper)
    :param a: coefficient of cumulative cost
    :param gamma: discount for duplicated nugget
    :param p: probability of stopping at any position given a ranked list ( geometric distribution part in the paper)
    :param verbose: if true, print info on stdout
    :return:
    """
    PROB.clear()
    if verbose:
        print(run_file_path)
        print('topic_id', 'expected_utility', sep='\t')
    truth = DDTruth(truth_xml_path, doc_length_path)
    run_result = DDReader(run_file_path).run_result

    # sort run result by topic id
    sorted_results = sorted(run_result.items(), key=lambda x: int(x[0].split('-')[1]))

    utility_list = []
    for topic_id, topic_result in sorted_results:
        topic_truth = truth.truth_4_EU(topic_id)

        utility = eu_per_topic(topic_truth, topic_result, a, gamma, p, cutoff)

        utility_list.append(utility)
        if verbose:
            print(topic_id, utility, sep='\t')

    if verbose:
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
                # print('doc not found: ', doc_list[s-1], file=sys.stderr)
                pass
            cumulated_len += doc_length.get(doc_list[s - 1], 949)  # 949 is the average length of trecdd15 documents
            prob = prob_stop_at_s(p, s, l)
            expected_len += (prob * cumulated_len)

        total_len += expected_len

    return total_len


def test_a():
    """test different parameter a"""
    run_paths, truth_xml, doc_length, max_iter = util.get_data('trec_dd_16')

    truth = DDTruth(truth_xml, doc_length)

    # max_iter = 10

    all_results = {}  # all_results={run_id: topic_id: {cutoff: {metric1:xx, metric2:xx,...}}}
    for run_file_path in run_paths:
        run = DDReader(run_file_path).run_result

        run_name = os.path.split(run_file_path)[1]

        print(run_name, file=sys.stderr)

        all_results[run_name] = {}

        # sort by topic id
        sorted_run = sorted(run.items(), key=lambda x: int(x[0].split('-')[1]))

        for topic_id, topic_result in sorted_run:

            all_results[run_name][topic_id] = {}

            for cutoff in range(1, max_iter + 1):

                eu_1 = eu_per_topic(truth.truth_4_EU(topic_id), topic_result, a=0.0013, gamma=0.5, p=0.5,
                                    cutoff=cutoff)
                eu_2 = eu_per_topic(truth.truth_4_EU(topic_id), topic_result, a=0.0011, gamma=0.5, p=0.5,
                                    cutoff=cutoff)
                eu_3 = eu_per_topic(truth.truth_4_EU(topic_id), topic_result, a=0.0010, gamma=0.5, p=0.5,
                                    cutoff=cutoff)
                eu_4 = eu_per_topic(truth.truth_4_EU(topic_id), topic_result, a=0.0009, gamma=0.5, p=0.5,
                                    cutoff=cutoff)
                eu_5 = eu_per_topic(truth.truth_4_EU(topic_id), topic_result, a=0.0007, gamma=0.5, p=0.5,
                                    cutoff=cutoff)

                all_results[run_name][topic_id][cutoff] ={
                    'eu_1':eu_1,
                    'eu_2':eu_2,
                    'eu_3':eu_3,
                    'eu_4':eu_4,
                    'eu_5':eu_5,
                }

    metric_order = ['eu_1', 'eu_2', 'eu_3', 'eu_4', 'eu_5']
    util.output(all_results, metric_order=metric_order, output_path='results/eu_a_compare.csv')


if __name__ == '__main__':
    """
    eu('data/trec_dd_16/runs/ufmgHM2', 'data/trec_dd_16/truth/dynamic-domain-2016-truth-data.xml',
       'data/trec_dd_16/doc_length.json', cutoff=10, verbose=True)


    for p in pattern_generator([5, 5, 5]):
        print(p)
    """

    test_a()