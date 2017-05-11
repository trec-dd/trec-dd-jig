"""
Read, parse run file
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
            topic_id, iter_num, doc_no = parts[0], int(parts[1]), parts[2]
            if topic_id not in self.run_result:
                self.run_result[topic_id] = {}
            if iter_num not in self.run_result[topic_id]:
                self.run_result[topic_id][iter_num] = []

            self.run_result[topic_id][iter_num].append(doc_no)

            line = f.readline().strip()

        f.close()

    def get_iter_num(self):
        """return iteration number of every topic"""
        iter_num = {}
        for topic_id, topic_data in self.run_result.items():
            iter_num[topic_id] = len(topic_data)

        return iter_num


if __name__ == '__main__':
    reader = DDReader('data/trec_dd_16/runs/LDA_Indri73')
    from pprint import pprint

    pprint(reader.run_result)
