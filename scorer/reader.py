"""
Read, parse run file
Copyright 2017 @ Georgetown University
"""
import os


class DDReader:
    """
    run_result=
    {
        topic_id:
        {
            iteration# :
            [
                doc_no1, doc_no2, ... , doc_no5
            ]
        }
    }
    """

    def __init__(self, run_file_path):
        self.run_result = {}
        assert os.path.exists(run_file_path)
        f = open(run_file_path)
        line = f.readline().strip()
        while line != '':
            parts = line.split('\t')
            topic_id, iter_num, doc_no, score = parts[0], int(parts[1]), parts[2], float(parts[3])
            if topic_id not in self.run_result:
                self.run_result[topic_id] = {}
            if iter_num not in self.run_result[topic_id]:
                self.run_result[topic_id][iter_num] = []

            self.run_result[topic_id][iter_num].append((doc_no, score))

            line = f.readline().strip()

        f.close()

        # sort within each iteration
        for topic_id in self.run_result:
            for iter_num in self.run_result[topic_id]:
                sorted_run = sorted(self.run_result[topic_id][iter_num], key=lambda x: x[1], reverse=True)
                # only reserve doc no
                self.run_result[topic_id][iter_num] = [doc_no for doc_no, score in sorted_run]

        # remove duplicated doc
        for topic_id in self.run_result:
            doc_set = set()  # doc that has been found
            for iter_num in self.run_result[topic_id]:
                for i in range(len(self.run_result[topic_id][iter_num])):
                    if self.run_result[topic_id][iter_num][i] in doc_set:
                        # change the doc no of duplicated doc, so it will become irrelevant
                        self.run_result[topic_id][iter_num][i] += '_dup'
                    else:
                        doc_set.add(self.run_result[topic_id][iter_num][i])

        # fill blank iteration
        for topic_id in self.run_result:
            l = max(self.run_result[topic_id].keys()) + 1  # number of iterations for current topic
            for i in range(l):
                if i not in self.run_result[topic_id]:
                    self.run_result[topic_id][i] = ['fill-non-relevant-doc']

    def get_iter_num(self):
        """return iteration number of every topic"""
        iter_num = {}
        for topic_id, topic_data in self.run_result.items():
            iter_num[topic_id] = len(topic_data)

        return iter_num


if __name__ == '__main__':
    reader = DDReader('../sample_run/runfile')
    from pprint import pprint

    pprint(reader.run_result)
    print(len(reader.run_result))
