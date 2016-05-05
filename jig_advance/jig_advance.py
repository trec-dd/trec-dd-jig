'''trec_dd.harness.run provides an evaluation jig for TREC Dynamic Domain systems

..This software is released under an MIT/X11 open source license. Copyright 2015 @ Diffeo Inc and Georgetown University

'''

from __future__ import absolute_import, print_function


import json
import logging
import os
import sqlite3
import random
import click


logger = logging.getLogger(__name__)


def query_to_topic_id(query):
    return query.replace(' ', '_')


def topic_id_to_query(topic_id):
    return topic_id.replace('_', ' ')

TIRED_THRESHOLD = 3  #get tired of staying in the same subtopic (or over_all mode) for too long
NO_FEEDBACK_TOLERATE = 'NN'  #get sick if continuously no positive feedback

SHIFT_OR_ALL = 0.5


truth_data_path = 'truth.db'
batch_size = 5


def step(topic_id, novelty, results):
    if not os.path.exists(truth_data_path):
        return {'error': 'Please run config.sh first'}

    con = sqlite3.connect(truth_data_path)
    cur = con.cursor()

    cur.execute('SELECT topic_id, iteration_ct, no_feedback_ct, current_subtopic_id, dealed_subtopics, untouched_subtopics FROM topic_status WHERE topic_id=? AND novelty=?', [topic_id, novelty])
    row = cur.fetchone()

    if isTired(row) :
        if random.random() <= SHIFT_OR_ALL:  #randome decimal in [0,1)
            #shift
            current_subtopic, dealed_topics = shiftSubtopic(row)
        else:
            #all
            current_subtopic, dealed_topics = shiftSubtopic(row)
        iteration_ct = 1
        no_feedback_ct = ""
    else:
        iteration_ct = row[1] + 1
        no_feedback_ct = row[2]
        current_subtopic = row[3]
        dealed_topics = row[4]

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
        no_feedback_ct = no_feedback_ct + 'F'  #N stands for no feedback
    else:
        no_feedback_ct = no_feedback_ct + 'N'  #F stands for feedback

    cur.execute('UPDATE topic_status SET iteration_ct=?, no_feedback_ct=?, current_subtopic_id=?, dealed_subtopics=? WHERE topic_id=? AND novelty=?'
            , [iteration_ct, no_feedback_ct, current_subtopic, dealed_topics, topic_id, novelty])

    con.commit()

    return rlist


def shiftSubtopic(row):
    if row[5] != "":
        untouched_topics = row[5].split(',')
        untouched_topics.append("all")
        m = len(untouched_topics)
        random_index = random.randrange(0,m) % m
        next_topic = untouched_topics[random_index];
        if row[4] != "":
            dealed_topics = row[4]+ "(" + `row[1]` + ":" + row[2] + ")" + "," + next_topic
        else:
            dealed_topics = next_topic
    return next_topic, dealed_topics


def isTired(row):
    #no current subtopic yet
    if row[3] is None:
        return True
    # stay on the same mode/subtopic for too long
    if row[1] >= TIRED_THRESHOLD:
        return True
    # no positive feedback for current subtopic for several iteration, enough is enough
    if row[2].endswith(NO_FEEDBACK_TOLERATE):
        return True

    return False


# should be modified
usage = ''' See Readme on Github: https://github.com/trec-dd/trec-dd-jig
        '''


@click.command()
@click.option('-runid', type=click.STRING, help='Run Identifier')
@click.option('-topic', type=click.STRING, help='Topic ID')
@click.option('-novelty', type=click.INT, help='Novelty')
@click.option('-docs', nargs=5, type=click.Tuple([unicode, unicode, unicode, unicode, unicode]),
              help='Returned document lists')
def main(runid, topic, novelty, docs):
    feedback = step(topic, novelty, docs)
    print(runid)
    for f in feedback:
        print(json.dumps(f))
            

if __name__ == '__main__':
    main()
