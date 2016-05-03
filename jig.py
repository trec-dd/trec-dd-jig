'''trec_dd_stage_aware_jig provides an evaluation jig for TREC Dynamic Domain systems

..This software is released under an MIT/X11 open source license. Copyright 2016 @ Georgetown University

'''

from __future__ import absolute_import, print_function
import argparse
import kvlayer
import logging
import os
import yakonfig
import sqlite3


logger = logging.getLogger(__name__)


def query_to_topic_id(query):
    return query.replace(' ', '_')


def topic_id_to_query(topic_id):
    return topic_id.replace('_', ' ')


TOPIC_IDS = 'trec_dd_harness_topic_ids'
EXPECTING_STOP = 'trec_dd_harness_expecting_stop'
SEEN_DOCS = 'trec_dd_harness_seen_docs'


class Jig(object):
    tables = {
        TOPIC_IDS: (str,),
        EXPECTING_STOP: (str,),
    }

    def __init__(self, config):
        self.truth_data_path = config.get('truth_data_path')
        self.run_file_path = config.get('run_file_path')
        self.topic_ids = set(config.get('topic_ids', []))
        self.batch_size = int(config.get('batch_size', 5))

    config_name = 'harness'

    def step(self, topic_id, results):
        if not os.path.exists(self.truth_data_path):
            return {'error': 'Please run config.sh first'}
        if len(results) > 2 * self.batch_size:
            return {'error': 'MUST EXIT: submitted too many results'}

        con = sqlite3.connect(self.truth_data_path)
        cur = con.cursor()

        rlist = []
        for result_pair in results:
            result = result_pair.split(':')
            cur.execute('SELECT subtopic_id, rating FROM passage WHERE topic_id=? AND docno=?',[str(topic_id), result[0]])
            rs = cur.fetchall()
            feedback = str(topic_id) + '\t' + result[0] + '\t' + result[1] + '\t'
            if rs:
                feedback = feedback + '1' + '\t'
                for r in rs:
                    sid, rating = r
                    feedback += str(sid) + ':' + str(rating) + '|'
                feedback = feedback[:-1]
            else:
                feedback += '0'
            rlist.append(feedback)
        return rlist


def main():
    parser = argparse.ArgumentParser(
        'Command line interface to the office TREC DD jig.',
        conflict_handler='resolve')
    parser.add_argument('args', help='input for given command',
                        nargs=argparse.REMAINDER)
    modules = [yakonfig, kvlayer, Jig]
    args = yakonfig.parse_args(parser, modules)

    logging.basicConfig(level=logging.DEBUG)

    config = yakonfig.get_global_config('harness')
    jig = Jig(config)

    parts = args.args
    topic_id = parts.pop(0)
    feedback = jig.step(topic_id, parts)
    for f in feedback:
        print(f)


if __name__ == '__main__':
    main()
