import os
import sqlite3
import xml.etree.ElementTree as ET
import sys


def main():
    dbname = 'truth.db'
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
		novelty REAL,
		iteration_ct INTEGER,
		no_feedback_ct TEXT,
                current_subtopic_id TEXT,
		dealed_subtopics TEXT,
		untouched_subtopics TEXT,
		PRIMARY KEY (topic_id,run_id,novelty)
	    )
	'''
    ]
    tree = ET.parse(sys.argv[1])
    root = tree.getroot()

    if os.path.isfile(dbname):
        os.remove(dbname)
    con = sqlite3.connect(dbname)
    cur = con.cursor()

    for table in tables:
        cur.execute('CREATE TABLE %s' % table)

    novelties = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
    runs = ["alg0", "alg1", "alg2", "alg3", "alg4", "alg5"]  # can parallizingly run 6 algorithems

    f = False
    domain_nodes = root.findall('.//domain')
    for domain_node in domain_nodes:
        did = int(domain_node.get('id'))
        cur.execute('INSERT INTO domain VALUES(?, ?)', [did, domain_node.get('name')])
        topic_nodes = domain_node.findall('./topic')
        for topic_node in topic_nodes:
            tid = topic_node.get('id')
            cur.execute('INSERT INTO topic VALUES(?, ?, ?)', [tid, topic_node.get('name'), did])
            subtopic_nodes = topic_node.findall('./subtopic')

            untouched_subtopics = "";

            for subtopic_node in subtopic_nodes:
                sid = subtopic_node.get('id')
                if untouched_subtopics != "":
                    untouched_subtopics = untouched_subtopics + ","
                untouched_subtopics = untouched_subtopics + sid

                cur.execute('INSERT INTO subtopic VALUES(?, ?, ?)', [sid, subtopic_node.get('name'), tid])
                passages = subtopic_node.findall('./passage')
                for passage in passages:
                    pid = passage.get('id')
                    docno = passage.find('./docno').text
                    text = passage.find('./text').text
                    rating = int(passage.find('./rating').text)
                    type = passage.find('./type').text
                    if type == 'MATCHED':
                        score == float(passage.find('./score').text)
                    else:
                        score = None
                    cur.execute('INSERT INTO passage VALUES(?, ?, ?, ?, ?, ?, ?, ?)',
                                [pid, sid, tid, docno, rating, type, score, text])
            for novelty in novelties:
                for run in runs:
                    cur.execute('INSERT INTO topic_status VALUES(?,?,?,?,?,?,?,?)',
                                [tid, run, novelty, 0, "", None, "", untouched_subtopics])

    con.commit()
    con.close()


if __name__ == '__main__':
    main()
