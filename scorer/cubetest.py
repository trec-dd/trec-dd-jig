"""
Cube Test
Copyright 2017 @ Georgetown University
"""

from .truth import *
from .reader import *
from collections import Counter
import statistics


def cubetest(run_file_path, truth_xml_path, gamma=0.5, max_height=5, cutoff=10, verbose=False):
    """return ct, act over all topics"""
    if verbose:
        print(run_file_path)
        print('topic-id', 'ct@' + str(cutoff), 'act@' + str(cutoff), sep='\t')
    truth = DDTruth(truth_xml_path)
    run_result = DDReader(run_file_path).run_result

    ct_list, act_list = [], []
    gain_list = []
    sorted_results = sorted(run_result.items(), key=lambda x: int(x[0].split('-')[1]))
    for topic_id, topic_result in sorted_results:
        topic_truth = truth.truth_4_CT(topic_id)
        gain, ct, act = cubetest_per_topic(topic_truth, topic_result,
                                           gamma, max_height, cutoff)
        if verbose:
            print(topic_id, ct, act, sep='\t')

        ct_list.append(ct)
        act_list.append(act)
        gain_list.append(gain)
    if verbose:
        print('all', statistics.mean(ct_list), statistics.mean(act_list), sep='\t')
    return gain_list, ct_list, act_list


def cubetest_per_topic(topic_truth, topic_result, gamma, max_height, cutoff):
    """return ct and act of one topic"""
    subtopic_num = topic_truth[1]
    topic_truth = topic_truth[0]

    subtopic_height = Counter()  # current height of every subtopic
    subtopic_count = Counter()  # #docs found relevant to every subtopic (nrels)

    weight_per_subtopic = 1.0 / subtopic_num

    def gain_per_doc(doc_no):
        if doc_no not in topic_truth:
            return 0
        gain = 0
        for subtopic_id, rating in topic_truth[doc_no].items():
            if subtopic_height[subtopic_id] < max_height:
                discount_height = (gamma ** (subtopic_count[subtopic_id] + 1)) * rating
                if discount_height + subtopic_height[subtopic_id] > max_height:
                    discount_height = max_height - subtopic_height[subtopic_id]

                gain += weight_per_subtopic * discount_height
                # print(doc_no, subtopic_id,"original_height", rating, "discount height", discount_height)
                subtopic_height[subtopic_id] += discount_height
                subtopic_count[subtopic_id] += 1
        # print(doc_no, gain)
        return gain

    sorted_result = sorted(topic_result.items(), key=lambda x: x[0])
    time = 0.0
    total_gain = 0
    accu_gain = 0
    doc_num = 0
    for iter_num, doclist in sorted_result:
        if iter_num >= cutoff:
            break
        time += 1
        # gain_per_iteration = 0
        for doc_no in doclist:
            total_gain += gain_per_doc(doc_no)
            accu_gain += (total_gain / max_height / time)
            doc_num += 1

    # print(time)
    if time != 0:
        ct = total_gain / max_height / time
    else:
        ct = 0
    # print(doc_num)
    if doc_num > 0:
        act = accu_gain / doc_num
    else:
        act = 0
    # print( accu_gain , total_gain)
    return total_gain / max_height, ct, act


def cubetest_per_topic_no_cap(topic_truth, topic_result, gamma, cutoff):
    """return ct and act of one topic"""
    subtopic_num = topic_truth[1]
    topic_truth = topic_truth[0]

    subtopic_height = Counter()  # current height of every subtopic
    subtopic_count = Counter()  # #docs found relevant to every subtopic (nrels)

    weight_per_subtopic = 1.0 / subtopic_num

    def gain_per_doc(doc_no):
        if doc_no not in topic_truth:
            return 0
        gain = 0
        for subtopic_id, rating in topic_truth[doc_no].items():
            # if subtopic_height[subtopic_id] < max_height:
            # discount_height = (gamma ** (subtopic_count[subtopic_id] + 1)) * rating
            discount_height = (gamma ** (subtopic_count[subtopic_id])) * rating
            # if discount_height +subtopic_height[subtopic_id] >max_height:
            # discount_height=max_height-subtopic_height[subtopic_id]

            gain += weight_per_subtopic * discount_height
            # print(doc_no, subtopic_id,"original_height", rating, "discount height", discount_height)
            subtopic_height[subtopic_id] += discount_height
            subtopic_count[subtopic_id] += 1
        # print(doc_no, gain)
        return gain

    sorted_result = sorted(topic_result.items(), key=lambda x: x[0])
    time = 0.0
    total_gain = 0
    accu_gain = 0
    doc_num = 0
    for iter_num, doclist in sorted_result:
        if iter_num >= cutoff:
            break
        time += 1
        # gain_per_iteration = 0
        for doc_no in doclist:
            total_gain += gain_per_doc(doc_no)
            accu_gain += (total_gain / time)
            doc_num += 1

    # print(time)
    if time != 0:
        ct = total_gain / time
    else:
        ct = 0
    # print(doc_num)
    if doc_num > 0:
        act = accu_gain / doc_num
    else:
        act = 0
    # print( accu_gain , total_gain)
    return total_gain, ct, act


if __name__ == '__main__':
    cubetest('data/trec_dd_16/runs/rmit_oracle.lm.1000', 'data/trec_dd_16/truth/dynamic-domain-2016-truth-data.xml',
             cutoff=10, verbose=True)
