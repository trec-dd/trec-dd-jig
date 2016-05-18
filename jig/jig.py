'''
    trec_dd_jig provides an evaluation jig for TREC Dynamic Domain systems

    Copyright 2016 @ Georgetown University
'''


from __future__ import absolute_import, print_function

import os
import sqlite3
import click
import json

truth_data_path = 'jig/stage_truth.db'
step_size = 3


def step_stage(runid, topic_id, results):
    if not os.path.exists(truth_data_path):
        return {'error': 'Please run config.sh first'}

    con = sqlite3.connect(truth_data_path)
    cur = con.cursor()

    rlist = []

    # subtopic sequence under this topic_id
    cur.execute('SELECT sequence FROM subtopic_sequences WHERE topic_id=?', [str(topic_id)])
    sequence, = cur.fetchone()
    subtopics = sequence.split('\t')[:-1]

    # iteration count for this run_id
    cur.execute('SELECT iteration_ct FROM topic_status WHERE run_id=?', [str(runid)])
    tmp = cur.fetchone()
    if not tmp:
        cur.execute('INSERT INTO topic_status VALUES(?, ?, ?)', [topic_id, runid, 0])
        con.commit()
        ct = 0
    else:
        ct, = tmp
    # The file that records results with feedback into file named after runid
    f = open(runid+'.txt', 'a')
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
        # feedback: Immediate feedback that will be printed to screen.
        feedback = {'topic_id': topic_id, 'doc_id': result[0], 'ranking_score': result[1]}
        # Each line represent a feedback for one document
        wline = topic_id + '\t' + str(ct) + '\t' + result[0] + '\t' + result[1] + '\t'
        # topic id, iteration id, doc no, doc ranking score given by participating system
        if rs:
            wline += '1' + '\t'
            # 1: on topic
            feedback['on_topic'] = '1'
            feedback['subtopics'] = []
            for r in rs:
                sid, rating, text = r
                subtopic = {'subtopic_id': sid, 'rating': rating, 'passage_text': text}
                feedback['subtopics'].append(subtopic)
                wline += str(sid) + ':' + str(rating) + '|'
                # subtopic is and the relevance score for this subtopic
            rlist.append(feedback)
            wline = wline[:-1]
            # get rid of the '|'
        else:
            # off topic
            feedback.update({'on_topic': '0'})
            wline += '0' + '\t'
            rlist.append(feedback)
        f.write(wline)
        f.write('\n')

    # Update the iteration count for current run_id in the database, only needed in stage aware jig
    cur.execute('UPDATE topic_status SET iteration_ct=?  WHERE run_id=?', [ct+1, str(runid)])
    con.commit()
    return rlist


def step(runid, topic_id, results):
    if not os.path.exists(truth_data_path):
        return {'error': 'Please run config.sh first'}

    con = sqlite3.connect(truth_data_path)
    cur = con.cursor()

    # iteration count for this run_id
    cur.execute('SELECT iteration_ct FROM topic_status WHERE run_id=?', [str(runid)])
    tmp = cur.fetchone()
    if not tmp:
        cur.execute('INSERT INTO topic_status VALUES(?, ?, ?)', [topic_id, runid, 0])
        con.commit()
        ct = 0
    else:
        ct, = tmp

    rlist = []
    f = open(runid+'.txt', 'a')
    for result_pair in results:
        result = result_pair.split(':')  # result[0]: docno, result[1]: ranking score
        cur.execute('SELECT subtopic_id, rating, text FROM passage WHERE topic_id=? AND docno=?', [str(topic_id), result[0]])
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
    cur.execute('UPDATE topic_status SET iteration_ct=?  WHERE run_id=?', [ct+1, str(runid)])
    con.commit()

    return rlist


@click.command()
@click.option('-runid', type=click.STRING, help='Run Identifier')
@click.option('-topic', type=click.STRING, help='Topic ID')
@click.option('-stage', help='Choose stage/ not_stage')
@click.option('-docs', nargs=5, type=click.Tuple([unicode, unicode, unicode, unicode, unicode]),
              help='Returned document lists')
def main(runid, topic, stage, docs):
    if stage == 'stage':
        feedback = step_stage(runid, topic, docs)
    elif stage == 'normal':
        feedback = step(runid, topic, docs)
    else:
        print('Please choose the correct type of jig! See https://github.com/trec-dd/trec-dd-jig')
        return
    print(runid)
    for f in feedback:
        print(json.dumps(f, indent=4, separators=(',', ': ')))


if __name__ == '__main__':
    main()