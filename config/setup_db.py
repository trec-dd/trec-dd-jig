"""
Initialize database
Copyright 2017 @ Georgetown University
"""

import sqlite3
import xml.etree.ElementTree as ET
import os


def setup_db(topic_xml):
    dbname = 'jig/truth.db'
    tables = [
        '''
            domain(
                domain_id INTEGER PRIMARY KEY,
                domain_name TEXT
            )
        ''',

        '''
            topic(
                topic_id  TEXT PRIMARY KEY,
                topic_name TEXT,
                domain_id INTEGER
            )
        ''',

        '''
            subtopic(
                subtopic_id TEXT PRIMARY KEY,
                subtopic_name TEXT,
                topic_id TEXT
            )
        ''',

        '''
            passage(
                passage_id INTEGER PRIMARY KEY,
                subtopic_id TEXT,
                topic_id TEXT,
                docno TEXT,
                rating INTEGER,
                type TEXT,
                score FLOAT,
                text TEXT
            )
        ''',

        '''
            topic_status(
                topic_id TEXT,
                run_id TEXT,
                iteration_ct INTEGER,
                PRIMARY KEY (topic_id,run_id)
                )
            ''',
        '''
            subtopic_sequences(
                topic_id TEXT PRIMARY KEY,
                sequence TEXT
                )
            '''

    ]
    tree = ET.parse(topic_xml)
    root = tree.getroot()

    if os.path.isfile(dbname):
        os.remove(dbname)
    con = sqlite3.connect(dbname)
    cur = con.cursor()

    for table in tables:
        cur.execute('CREATE TABLE %s' % table)

    domain_nodes = root.findall('.//domain')
    for domain_node in domain_nodes:
        did = int(domain_node.get('id'))
        cur.execute('INSERT INTO domain VALUES(?, ?)', [did, domain_node.get('name')])
        topic_nodes = domain_node.findall('./topic')
        for topic_node in topic_nodes:
            tid = topic_node.get('id')
            cur.execute('INSERT INTO topic VALUES(?, ?, ?)', [tid, topic_node.get('name'), did])
            subtopics = ""
            subtopic_nodes = topic_node.findall('./subtopic')
            for subtopic_node in subtopic_nodes:
                sid = subtopic_node.get('id')
                cur.execute('INSERT INTO subtopic VALUES(?, ?, ?)', [sid, subtopic_node.get('name'), tid])
                passages = subtopic_node.findall('./passage')
                subtopics += sid + '\t'
                for passage in passages:
                    pid = passage.get('id')
                    docno = passage.find('./docno').text
                    text = passage.find('./text').text
                    rating = int(passage.find('./rating').text)
                    type = passage.find('./type').text
                    if type == 'MATCHED':
                        score = float(passage.find('./score').text)
                    else:
                        score = None
                    cur.execute('INSERT INTO passage VALUES(?, ?, ?, ?, ?, ?, ?, ?)',
                                [pid, sid, tid, docno, rating, type, score, text])
            cur.execute('INSERT INTO subtopic_sequences VALUES(?, ?)', [tid, subtopics])

    con.commit()
    con.close()
