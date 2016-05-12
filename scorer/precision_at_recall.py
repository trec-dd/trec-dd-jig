from collections import defaultdict

def loadGroundTruth(ground_truth, qrel):

    for line in qrel:
        elements = line.split()
        ground_truth[elements[0]].add(elements[2])

def computePrecisionAtRecall(ground_truth, runfile, iteration=-1):

    last_topic_id = None
    on_topic = 0
    precision_at_recall = {}

    for line in runfile:
        elements = line.split()

        if elements[0] != last_topic_id: # first line of the topic
            if last_topic_id:
                precision_at_recall[last_topic_id] = on_topic / float(dcount)
                #print last_topic_id, on_topic, dcount
            last_topic_id = elements[0]
            dcount = 1
            on_topic = 0
        else:
            dcount += 1

        if elements[2] in ground_truth[elements[0]]: on_topic += 1

    return sum(precision_at_recall.values()) / len(precision_at_recall)
    #return precision_at_recall


def main():
    qrel = open('qrel.txt','r')
    runfile = open('ul_combi_roc.2', 'r')
    ground_truth = defaultdict(set)

    loadGroundTruth(ground_truth, qrel)

    print computePrecisionAtRecall(ground_truth, runfile)

main()
