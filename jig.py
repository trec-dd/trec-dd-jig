'''trec_dd.harness.run provides an evaluation jig for TREC Dynamic Domain systems

..This software is released under an MIT/X11 open source license. Copyright 2015 @ Diffeo Inc and Georgetown University

'''

from __future__ import absolute_import, print_function
import argparse
from collections import defaultdict
from dossier.label import LabelStore, Label, CorefValue
import json
import itertools
import kvlayer
import logging
import os
import sys
import time
import yakonfig
import sqlite3

# from trec_dd.harness.truth_data import parse_truth_data

logger = logging.getLogger(__name__)


def query_to_topic_id(query):
    return query.replace(' ', '_')


def topic_id_to_query(topic_id):
    return topic_id.replace('_', ' ')


TOPIC_IDS = 'trec_dd_harness_topic_ids'
EXPECTING_STOP = 'trec_dd_harness_expecting_stop'
SEEN_DOCS = 'trec_dd_harness_seen_docs'
run_file_path = ''


class Harness(object):
    tables = {
        TOPIC_IDS: (str,),
        EXPECTING_STOP: (str,),
    }

    def __init__(self, config, kvl, label_store):
        self.kvl = kvl
        self.label_store = label_store
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
        confidence = '50' # remain to be changed
        for result in results:
            #cur.execute('SELECT docno, subtopic_id, text, rating FROM passage WHERE topic_id=? AND docno=?',
            #            [str(topic_id), result])
            #rlist.append(cur.fetchall())
            cur.execute('SELECT subtopic_id, rating FROM passage WHERE topic_id=? AND docno=?',[str(topic_id), result])
            rs = cur.fetchall()
            feedback = str(topic_id) + '\t' + result + '\t' + confidence + '\t'
            if rs:
                feedback = feedback + '1' + '\t'
                for r in rs:
                    sid, rating = r
                    feedback += str(topic_id) + '-' + str(sid) + ':' + str(rating) + '|'
                feedback = feedback[:-1]
            else:
                feedback += '0'
            rlist.append(feedback)
        return rlist



# should be modified
usage = '''The purpose of this harness is to interact with your TREC DD system
by issuing queries to your system, and providing feedback (truth data)
for the results produced by your system. 

The harness is run via command:
    > python jig/jig.py -c config_file topic_id doc1 doc2 doc3 ... doc5

Every invocation  must include the  -c argument  with a
path   to    a   valid    config.yaml   file,   as    illustrated   in
jig/config.yaml. 

Each of the five commands returns a JSON dictionary which your system
can read using a JSON library.  The harness always provides feedback
for every result, even if the feedback is that the system has no truth
data for that result.

'''


def main():
    parser = argparse.ArgumentParser(
        'Command line interface to the office TREC DD jig.',
        usage=usage,
        conflict_handler='resolve')
    parser.add_argument('args', help='input for given command',
                        nargs=argparse.REMAINDER)
    modules = [yakonfig, kvlayer, Harness]
    args = yakonfig.parse_args(parser, modules)

    logging.basicConfig(level=logging.DEBUG)

    kvl = kvlayer.client()
    label_store = LabelStore(kvl)
    config = yakonfig.get_global_config('harness')

    harness = Harness(config, kvl, label_store)

    parts = args.args
    topic_id = parts.pop(0)
    feedback = harness.step(topic_id, parts)
    for f in feedback:
        print(f)


if __name__ == '__main__':
    main()
