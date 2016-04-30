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
import random

#from trec_dd.harness.truth_data import parse_truth_data

logger = logging.getLogger(__name__)


def query_to_topic_id(query):
    return query.replace(' ', '_')


def topic_id_to_query(topic_id):
    return topic_id.replace('_', ' ')


TOPIC_IDS = 'trec_dd_harness_topic_ids'
EXPECTING_STOP = 'trec_dd_harness_expecting_stop'
TIRED_THRESHOLD = 3 #get tired of staying in the same subtopic (or over_all mode) for too long
NO_FEEDBACK_TOLORATE = 'NN' #get sick if continuously no positive feedback

SHIFT_OR_ALL = 0.5

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

    def verify_label_store(self):
        ls = iter(self.label_store.everything())
        try:
            ls.next()
        except StopIteration:
            sys.exit('The label store is empty.  Have you run `trec_dd_harness load`?')
        else:
            return True

    def init(self, topic_ids=None):
        '''Initialize the DB table of topics to apply to the engine under test.
        '''
        self.kvl.clear_table(TOPIC_IDS)
        all_topics = dict()
        for label in self.label_store.everything():
            all_topics[(label.meta['topic_id'],)] = label.meta['topic_name']
        # allow in-process caller to init with topic ids of its choosing
        if topic_ids is not None:
            self.topic_ids = set(topic_ids)
        if self.topic_ids:
            for topic_id in all_topics.keys():
                if topic_id not in self.topic_ids:
                    all_topics.pop(topic_id)
        self.kvl.put(TOPIC_IDS, *all_topics.items())
        return {'num_topics': len(all_topics)}

    def check_expecting_stop(self):
        for (topic_id,), _ in self.kvl.scan(EXPECTING_STOP):
            sys.exit('Harness was expecting you to call stop because you '
                     'submitted fewer than batch_size results.  Fix your '
                     'system and try again.')

    def unset_expecting_stop(self):
        self.kvl.clear_table(EXPECTING_STOP)

    def set_expecting_stop(self, topic_id):
        self.kvl.put(EXPECTING_STOP, ((topic_id,), 'YES'))

    def start(self):
        '''initiates a round of feedback to recommender under evaluation.
        '''
        self.check_expecting_stop()
        self.verify_label_store()
        for (topic_id,), query_string in self.kvl.scan(TOPIC_IDS):
            return {'topic_id': topic_id, 'query': query_string}

        # finished all the topics, so end.
        return {'topic_id': None, 'query': None}

    def stop(self, topic_id):
        '''ends a round of feedback
        '''
        self.unset_expecting_stop()
        for idx, ((_topic_id,), query_string) in enumerate(self.kvl.scan(TOPIC_IDS)):
            if idx == 0:
                if topic_id != _topic_id:
                    sys.exit('%d != %d, which is where the database says we are'
                             % (topic_id, _topic_id))
                self.kvl.delete(TOPIC_IDS, (topic_id,))
                logger.info("Finished with topic: '%s'", topic_id)
        return {'finished': topic_id, 'num_remaining': idx }

    def step(self, topic_id, novelty, results):
        if not os.path.exists(self.truth_data_path):
            return {'error': 'Please run config.sh first'}
        if len(results) > 2 * self.batch_size:
            return {'error': 'MUST EXIT: submitted too many results'}

        con = sqlite3.connect(self.truth_data_path)
        cur = con.cursor()

        cur.execute('SELECT topic_id, iteration_ct, no_feedback_ct, current_subtopic_id, dealed_subtopics, untouched_subtopics FROM topic_status WHERE topic_id=? AND novelty=?', [topic_id, novelty])
        row = cur.fetchone()

        if self.isTired(row) :
            if random.random() <= SHIFT_OR_ALL : #randome decimal in [0,1)
            #shift
                current_subtopic, dealed_topics = self.shiftSubtopic(row)
            else:
            #all
                current_subtopic, dealed_topics = self.shiftSubtopic(row)
            iteration_ct = 1
            no_feedback_ct = ""
        else:
            iteration_ct = row[1] + 1
            no_feedback_ct = row[2]
            current_subtopic = row[3]
            dealed_topics = row[4]

        #f = open('log.txt','a')
        #f.write("subtopic is %s \n"%(current_subtopic))
        rlist = []
        hasFeedback = False
        for result in results:
            if current_subtopic == "all":
                cur.execute('SELECT docno, subtopic_id, text, rating FROM passage WHERE topic_id=? AND docno=?', [topic_id, result])
            else:
                cur.execute('SELECT docno, subtopic_id, text, rating FROM passage WHERE topic_id=? AND docno=? AND subtopic_id=?', [topic_id, result, current_subtopic])
            feedbacks = cur.fetchall()
            if not hasFeedback:
                for feedback in feedbacks:
                    if feedback[2] != "":
                        hasFeedback = True
                        break
            rlist.append(feedbacks)

        if hasFeedback:
            no_feedback_ct = no_feedback_ct + 'F'#N stands for no feedback
        else:
            no_feedback_ct = no_feedback_ct + 'N' #F stands for feedback

        '''for line in rlist:
               for row in line:
                print("test topic_id docno: %s , %s"%(topic_id , result))
                print(row[0])'''

        cur.execute('UPDATE topic_status SET iteration_ct=?, no_feedback_ct=?, current_subtopic_id=?, dealed_subtopics=? WHERE topic_id=? AND novelty=?'
                , [iteration_ct, no_feedback_ct, current_subtopic, dealed_topics, topic_id, novelty])

        #f.write("update topic_status SET iteration_ct=%s, no_feedback_ct=%s, current_subtopic_id=%s, dealed_subtopics=%s WHERE topic_id=%s AND novelty=%s"%(iteration_ct, no_feedback_ct, current_subtopic, dealed_topics, topic_id, novelty))

        con.commit()

        return rlist

    def shiftSubtopic(self, row):
        if row[5] != "":
           #row structure: topic_id, iteration_ct, no_feedback_ct, current_subtopic_id, dealed_subtopics, untouched_topics
            untouched_topics = row[5].split(',')
            untouched_topics.append("all")
            m = len(untouched_topics)
            random_index = random.randrange(0,m) % m
            next_topic = untouched_topics[random_index];
            if row[4] != "":
                dealed_topics = row[4]+ "(" + `row[1]` + ":" + row[2] + ")" + "," + next_topic
            else:
                dealed_topics = next_topic
            #iteration_ct:no_feedbacl_ct
        return next_topic, dealed_topics

    def isTired(self, row):
        #no current subtopic yet
        if row[3] is None:
            return True
        # stay on the same mode/subtopic for too long
        if row[1] >= TIRED_THRESHOLD :
            return True
        # no positive feedback for current subtopic for several iteration, enough is enough
        if row[2].endswith(NO_FEEDBACK_TOLORATE):
            return True

        return False


    def write_feedback_to_run_file(self, feedback):
        if self.run_file_path is None:
            return

        # *append* to the run file
        run_file = open(self.run_file_path, 'a')

        for entry in feedback:
            subtopic_stanza = 'NULL'
            if entry['subtopics']:
                subtopic_tuples = []
                for subtopic in entry['subtopics']:
                    subtopic_tuple = ':'.join([subtopic['subtopic_id'],
                                               str(subtopic['rating'])])
                    subtopic_tuples.append(subtopic_tuple)
                subtopic_stanza = '|'.join(subtopic_tuples)

            # <topic> <document-id> <confidence> <on_topic> <subtopic data>
            run_file_line = ('%(topic_id)s\t%(stream_id)s\t%(confidence).6f'
                             '\t%(on_topic)d\t%(subtopic_stanza)s\n')
            output_dict = {'subtopic_stanza': subtopic_stanza,
                           'topic_id': entry['topic_id'],
                           'stream_id': entry['stream_id'],
                           'confidence': entry['confidence'],
                           'on_topic': entry['on_topic'],
                           }
            to_write = run_file_line % output_dict

            assert len(run_file_line.split()) == 5

            run_file.write(to_write)

        run_file.close()

# should be modified
usage = '''The purpose of this harness is to interact with your TREC DD system
by issuing queries to your system, and providing feedback (truth data)
for the results produced by your system. 

The harness is run via command:
    > python jig/jig.py -c config step topic_id doc1 doc2 doc3 ... doc5

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
    parser.add_argument('command', help='must be "load", "init", "start", "step", or "stop"')
    parser.add_argument('novelty', help='must be novelty')
    parser.add_argument('exploit', help='how much jig want to stay on the same subtopic')
    parser.add_argument('args', help='input for given command',
                        nargs=argparse.REMAINDER)
    modules = [yakonfig, kvlayer, Harness]
    args = yakonfig.parse_args(parser, modules)

    logging.basicConfig(level=logging.DEBUG)

    if args.command not in set(['load', 'init', 'start', 'step', 'stop']):
        sys.exit('The only valid commands are "load", "init", "start", "step", and "stop".')

    config = yakonfig.get_global_config('harness')
    harness = Harness(config, None, None)

    novelty = args.novelty
    TIRED_THRESHOLD = args.exploit

    if args.command == 'load':
        if not config.get('truth_data_path'):
            sys.exit('Must provide --truth-data-path as an argument')
        if not os.path.exists(config['truth_data_path']):
            sys.exit('%r does not exist' % config['truth_data_path'])
        parse_truth_data(label_store, config['truth_data_path'])
        logger.info('Done!  The truth data was loaded into this '
                     'kvlayer backend:\n%s',
                     json.dumps(yakonfig.get_global_config('kvlayer'),
                                indent=4, sort_keys=True))

    elif args.command == 'init':
        response = harness.init()
        print(json.dumps(response))

    elif args.command == 'start':
        response = harness.start()
        print(json.dumps(response))

    elif args.command == 'stop':
        response = harness.stop(args.args[0])
        print(json.dumps(response))

    if args.command == 'step':
        parts = args.args
        topic_id = parts.pop(0)
        feedback = harness.step(topic_id,novelty, parts)
        print(json.dumps(feedback))
            

if __name__ == '__main__':
    main()
