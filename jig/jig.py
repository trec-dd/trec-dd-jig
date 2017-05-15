"""
    trec_dd_jig provides an evaluation jig for TREC Dynamic Domain systems

    Copyright 2017 @ Georgetown University
"""

from __future__ import absolute_import, print_function

import os
import sqlite3
import click
import json

truth_data_path = 'jig/truth.db'


def step(runid, topic_id, results):
    if not os.path.exists(truth_data_path):
        return {'error': 'Please run config.sh first'}

    con = sqlite3.connect(truth_data_path)
    cur = con.cursor()

    # iteration count for this run_id
    cur.execute('SELECT iteration_ct FROM topic_status WHERE run_id=? AND topic_id=?', [str(runid), str(topic_id)])
    tmp = cur.fetchone()
    if not tmp:
        cur.execute('INSERT INTO topic_status VALUES(?, ?, ?)', [topic_id, runid, 0])
        con.commit()
        ct = 0
    else:
        ct, = tmp

    rlist = []
    f = open(runid + '.txt', 'a')
    for result_pair in results:
        result = result_pair.split(':')  # result[0]: docno, result[1]: ranking score
        cur.execute('SELECT subtopic_id, rating, text FROM passage WHERE topic_id=? AND docno=?',
                    [str(topic_id), result[0]])
        rs = cur.fetchall()
        feedback = {'topic_id': topic_id, 'doc_id': result[0], 'ranking_score': result[1]}
        wline = topic_id + '\t' + str(ct) + '\t' + result[0] + '\t' + result[1] + '\t'
        if rs:
            feedback['on_topic'] = '1'
            feedback['subtopics'] = []
            wline += '1' + '\t'
            for r in rs:
                sid, rating, text = r
                subtopic = {'subtopic_id': sid, 'rating': rating, 'passage_text': text}
                feedback['subtopics'].append(subtopic)
                wline += str(sid) + ':' + str(rating) + '|'
            rlist.append(feedback)
            wline = wline[:-1]
        else:
            feedback.update({'on_topic': '0'})
            rlist.append(feedback)
            wline += '0'
        f.write(wline)
        f.write('\n')
    # print(rlist)
    cur.execute('UPDATE topic_status SET iteration_ct=?  WHERE run_id=? AND topic_id=?',
                [ct + 1, str(runid), str(topic_id)])
    con.commit()

    return rlist


@click.command()
@click.option('-runid', type=click.STRING, help='Run Identifier')
@click.option('-topic', type=click.STRING, help='Topic ID')
@click.option('-docs', nargs=5, type=click.Tuple([str, str, str, str, str]),
              help='Returned document lists')
def main(runid, topic, docs):
    feedback = step(runid, topic, docs)
    print(runid)
    for f in feedback:
        print(json.dumps(f, indent=4, separators=(',', ': ')))


if __name__ == '__main__':
    main()
