"""
Computing the bounds of metrics
Copyright 2017 @ Georgetown University
"""
from bound_truth import *
import math
import json
import pickle


def sDCG(topic_truth, bq, b, cutoff):
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


def sdcg_bound(ground_truth):
    result = {}
    sdcg_bq, sdcg_b = 4, 2
    for topic_id in ground_truth.truth:
        print(topic_id)
        result[topic_id] = {}
        sdcg_truth = ground_truth.truth4SDCG(topic_id)
        for cutoff in range(1, 11):
            print(cutoff)
            opt_sdcg = sDCG(sdcg_truth, sdcg_bq, sdcg_b, cutoff)
            result[topic_id][cutoff] = opt_sdcg

    # json.dump(result, fp=open("bound/sdcg.json", "w"))

    return result


def eu(topic_truth, a, gamma, p, cutoff):
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

    doc_len = sorted(doc_length.items(), key=lambda x: x[1])  # sort in ascending order
    forward_iter = iter(doc_len)
    backward_iter = reversed(doc_len)
    min_cost = 0
    max_cost = 0

    l = min(len(doc_length), 5 * cutoff)
    last = l % 5  # position of the last document in the last ranking list, start from 0
    for doc_rank in range(5):
        if doc_rank <= last:
            k = cutoff
        else:
            k = cutoff - 1
        for query_rank in range(k):
            _, min_doc_cost = next(forward_iter)
            _, max_doc_cost = next(backward_iter)
            min_cost += (1 - p) ** doc_rank * min_doc_cost
            max_cost += (1 - p) ** doc_rank * max_doc_cost
    upper_bound -= a * min_cost
    lower_bound = - a * max_cost

    return upper_bound, lower_bound


def eu_bound(ground_truth):
    result = {}
    eu_a, eu_p, eu_gamma = 0.001, 0.5, 0.5
    for topic_id in ground_truth.truth:
        print(topic_id)
        result[topic_id] = {}
        eu_truth = ground_truth.truth4EU_bound(topic_id)
        for cutoff in range(1, 11):
            print(cutoff)
            opt_eu = eu(eu_truth, eu_a, eu_gamma, eu_p, cutoff)
            result[topic_id][cutoff] = opt_eu

    # json.dump(result, fp=open("bound/eu1.json", "w"))
    return result


def ct(topic_truth, gamma, max_height, cutoff):
    doc_sub_rel, subtopic_num = topic_truth
    # print(len(doc_sub_rel))
    gain = 0
    subtopic_set = set()
    for doc_no in doc_sub_rel:
        for subtopic_id in doc_sub_rel[doc_no]:
            subtopic_set.add(subtopic_id)
    for subtopic_id in subtopic_set:
        subtopic_gain = 0
        rels = [doc_sub_rel[doc_no][subtopic_id] if subtopic_id in doc_sub_rel[doc_no]
                else 0
                for doc_no in doc_sub_rel]
        rels = sorted(rels, reverse=True)
        for i, rel in enumerate(rels):
            h = rel * (gamma ** i)
            if subtopic_gain + h >= max_height:
                h = max_height - subtopic_gain
            subtopic_gain += h
            if i >= cutoff * 5:
                break
        gain += subtopic_gain / subtopic_num

    opt_ct = gain / max_height / cutoff

    return opt_ct


def ct_bound(ground_truth):
    result = {}
    gamma = 0.5
    max_height = 5
    for topic_id in ground_truth.truth:
        print(topic_id)
        result[topic_id] = {}
        ct_truth = ground_truth.truth4CT(topic_id)
        for cutoff in range(1, 11):
            print(cutoff)
            opt_ct = ct(ct_truth, gamma, max_height, cutoff)
            result[topic_id][cutoff] = opt_ct
    # json.dump(result, fp=open("bound/new_ct.json", "w"))
    return result


def get_bound(topic_xml, doc_len):
    ground_truth = Truth(topic_xml, doc_len)
    print("sDCG")
    sdcg = sdcg_bound(ground_truth)
    print("CT")
    ct = ct_bound(ground_truth)
    print("EU")
    eu = eu_bound(ground_truth)
    # eu = None
    return sdcg, ct, eu


if __name__ == "__main__":
    """
    sdcg, ct, eu = get_bound('../sample_run/topic.xml', json.load(open('../sample_run/doc_len.json')))
    # data = {'sdcg':sdcg, 'ct': ct, 'eu': eu}
    data = [sdcg, ct, eu]
    # json.dump(data, open('../topics/bound.json', 'w'))
    pickle.dump(data, open('../topics/bound.pkl', 'wb'))
    """
    ground_truth = Truth('../sample_run/topic.xml', json.load(open('../sample_run/doc_len.json')))
    ct(ground_truth.truth4CT('DD16-5'), 0.5, 5, 1)
