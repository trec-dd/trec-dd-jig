'''
    trec_dd_jig provides an evaluation jig for TREC Dynamic Domain systems

    This software is released under an MIT/X11 open source license. Copyright 2016 @ Georgetown University
'''


from __future__ import absolute_import, print_function

import logging
import os
import sqlite3
import click
import json

logger = logging.getLogger(__name__)


truth_data_path = 'truth.db'


def step(topic_id, results):
    if not os.path.exists(truth_data_path):
        return {'error': 'Please run config.sh first'}

    con = sqlite3.connect(truth_data_path)
    cur = con.cursor()

    rlist = []
    for result_pair in results:
        result = result_pair.split(':') # result[0]: docno, result[1]: ranking score
        cur.execute('SELECT subtopic_id, rating, text FROM passage WHERE topic_id=? AND docno=?', [str(topic_id), result[0]])
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

    return rlist


@click.command()
@click.option('-runid', type=click.STRING, help='Run Identifier')
@click.option('-topic', type=click.STRING, help='Topic ID')
@click.option('-docs', nargs=5, type=click.Tuple([unicode, unicode, unicode, unicode, unicode]),
              help='Returned document lists')
def main(runid, topic, docs):
    feedback = step(topic, docs)
    print(runid)
    for f in feedback:
        print(json.dumps(f))


if __name__ == '__main__':
    main()