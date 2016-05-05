'''
    trec_dd_jig_stage_aware provides an evaluation jig for TREC Dynamic Domain systems
    Copyright 2016 @ Georgetown University
'''


from __future__ import absolute_import, print_function

import logging
import os
import sqlite3
import click
import json

logger = logging.getLogger(__name__)


truth_data_path = 'stage_truth.db'
step_size = 3


def step(runid, topic_id, results):
    if not os.path.exists(truth_data_path):
        return {'error': 'Please run config.sh first'}

    con = sqlite3.connect(truth_data_path)
    cur = con.cursor()

    rlist = []

    # subtopic sequence under this topic_id
    cur.execute('SELECT sequence FROM subtopic_sequences WHERE topic_id=?', [str(topic_id)])
    sequence, = cur.fetchone()
    subtopics = sequence.split('\t')[:-1]
    print(subtopics)

    # iteration count for this run_id
    cur.execute('SELECT iteration_ct FROM topic_status WHERE run_id=?', [str(runid)])
    tmp = cur.fetchone()
    if not tmp:
        cur.execute('INSERT INTO topic_status VALUES(?, ?, ?)', [topic_id, runid, 0])
        con.commit()
        ct = 0
    else:
        ct, = tmp

    for result_pair in results:
        result = result_pair.split(':') # result[0]: docno, result[1]: ranking score
        if (ct+1) % (step_size+1) == 0:
            # return relevance judgement about all subtopics
            # print(ct, 'all')
            cur.execute('SELECT subtopic_id, rating, text FROM passage WHERE topic_id=? AND docno=?',
                        [str(topic_id), result[0]])
        if (ct+1) % (step_size+1) != 0:
            current_subtopic = subtopics[(ct/4) % len(subtopics)]
            # print(ct, current_subtopic)
            cur.execute('SELECT subtopic_id, rating, text FROM passage WHERE topic_id=? AND docno=? AND subtopic_id=?',
                        [topic_id, result[0], current_subtopic])

        rs = cur.fetchall()
        feedback = [str(topic_id), result[0], result[1]]
        if rs:
            feedback.append('1')
            for r in rs:
                sid, rating, text = r
                full_feedback = feedback + [str(sid), str(rating), text]
                rlist.append(full_feedback)
        else:
            feedback += '0'
            rlist.append(feedback)

    cur.execute('UPDATE topic_status SET iteration_ct=?  WHERE run_id=?', [ct+1, str(runid)])
    con.commit()
    return rlist


@click.command()
@click.option('-runid', type=click.STRING, help='Run Identifier')
@click.option('-topic', type=click.STRING, help='Topic ID')
@click.option('-docs', nargs=5, type=click.Tuple([unicode, unicode, unicode, unicode, unicode]),
              help='Returned document lists')
def main(runid, topic, docs):
    feedback = step(runid, topic, docs)
    # print(runid)
    # for f in feedback:
    #     print(json.dumps(f))


if __name__ == '__main__':
    main()