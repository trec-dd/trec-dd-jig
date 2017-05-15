"""
Computing the document length
Copyright 2017 @ Georgetown University
"""

import re
import os


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
    """return {doc_no: length}"""
    doc_length = {}
    for direc in direcs:
        for root, _, files in os.walk(direc):
            for file in files:
                for docno, length in doc_len_single_file(os.path.join(root, file)):
                    doc_length[docno] = length

    return doc_length
