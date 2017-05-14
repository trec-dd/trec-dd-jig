"""
Jig configuration of TREC 2017 DD
Copyright 2017 @ Georgetown University
"""

import os
import sqlite3
import xml.etree.ElementTree as ET
import sys
import re
import json
import argparse


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


def doc_len_single_file(filepath):
    content = open(filepath).read()
    for doc in re.findall(r"<DOC>.*?</DOC>", content, re.DOTALL | re.IGNORECASE):
        # extract docno and text
        docno = re.search(r"<DOCNO>(.*?)</DOCNO>", doc, re.IGNORECASE | re.DOTALL).group(1)
        text = re.search(r"<TEXT>(.*?)</TEXT>", doc, re.DOTALL | re.IGNORECASE).group(1)

        # remove <style> </style> in text
        text = re.sub(r'<style.*?</style>', '', text, re.DOTALL)

        # remove <classifier> </classifier> in text
        text = re.sub(r'<classifier.*?</classifier>', '', text, re.DOTALL)

        # remove all the other tags
        text = re.sub(r'<.*?>', ' ', text, re.DOTALL)

        yield docno, len(text.split())


def doc_len(direcs):
    doc_length = {}
    for direc in direcs:
        for root, _, files in os.walk(direc):
            for file in files:
                for docno, length in doc_len_single_file(os.path.join(root, file)):
                    doc_length[docno] = length

    json.dump(doc_length, open("topics/doc_len.json", "w"))


def main():
    parser = argparse.ArgumentParser()

    # topic.xml file
    parser.add_argument("--topics", required=True, help="topic xml file path")

    # trectext directories
    parser.add_argument("--trecdirec", nargs='+', required=True, help="directories of trectext files")

    params = vars(parser.parse_args(sys.argv[1:]))
    setup_db(params['topics'])
    doc_len(params['trecdirec'])


if __name__ == "__main__":
    main()
