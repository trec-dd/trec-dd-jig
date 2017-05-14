from collections import defaultdict
import click

def preProcess(run, ct):
    runfile = open(run)
    output_path = run + '_' + str(ct)
    output = open(output_path, 'w')
    while 1:
        line = runfile.readline()
        if not line:
            break
        else:
            result = line.split('\t')
            if int(result[1]) <= int(ct):
                output.write(line)
    return output_path



def loadGroundTruth(ground_truth, qrel):
    for line in qrel:
        elements = line.split()
        ground_truth[elements[0]].add(elements[2])


def computePrecision(ground_truth, runfile,):
    runfile = open(runfile, 'r')
    last_topic_id = None
    on_topic = 0
    precision = {}

    for line in runfile:
        elements = line.split()

        if elements[0] != last_topic_id: # first line of the topic
            if last_topic_id:
                precision[last_topic_id] = on_topic / float(dcount)
                #print last_topic_id, on_topic, dcount
            last_topic_id = elements[0]
            dcount = 1
            on_topic = 0
        else:
            dcount += 1

        if elements[2] in ground_truth[elements[0]]: on_topic += 1

    if last_topic_id:
        precision[last_topic_id] = on_topic / float(dcount)

    for key in precision.keys():
        print  key, "\t" , precision[key]

    return sum(precision.values()) / len(precision)
    #return precision_at_recall


@click.command()
@click.option('-qrel', type=click.Path(exists=True))
@click.option('-run', type=click.Path(exists=True))
@click.option('-ct', type=click.INT)
def main(qrel, run, ct):
    qrel = open(qrel,'r')
    ground_truth = defaultdict(set)

    loadGroundTruth(ground_truth, qrel)

    # get scores for all iterations
    p = computePrecision(ground_truth, run)
    print "mean	\t", p

    # If need to get P@R score before (including) certain iteration
    # print computePrecisionAtRecall(ground_truth, preProcess(run, ct))

if __name__ == '__main__':
    main()
