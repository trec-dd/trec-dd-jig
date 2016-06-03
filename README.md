# trec-dd-jig

##### This is the readme file of  the user simulator (jig) package for the TREC 2016 Dynamic Domain (DD) Track.
##### The package is for research use only.

##### For technical questions, please send your request to google group https://groups.google.com/forum/#!forum/trec-dd

**************************************************************************

### What's inside the package:

* the jig (jig/jig.py)
* task measure scripts
* sample run files
**************************************************************************

### Requirements

#### 1. System requirements
- Works under Mac OS, Windows, and Linux.
- Python. Works best under Python 2.7.


#### 2. Download the TREC DD Topics:

- Topics (ground truth) must be the one downloaded from NIST. (http://trec.nist.gov/act_part/tracks16.html)


### Installation

#### 0. Quick install all the python packages needed:

    > pip install -r requirements.txt


##### 1. Download the jig package:

  ``` shell
    > git clone https://github.com/trec-dd/trec-dd-jig
  ```

##### 2. Configuration and set up
- Move the directory under the your trec-dd system directory, that is,
  ``` shell
        > mv trec-dd-jig /yourhomedirectory/your_dd_directory/
  ```

- Put your downloaded topics (with ground truth) from the TREC Active Participants Home Page under
  ``` shell
        > mv topic_file.xml ./trec-dd-jig/jig/topics/
  ```

- Setup a topic database

  ``` shell
    >$ sh jig/config.sh --topics topic_file.xml
  ```
  This will set up a sqlite database at ./trec-dd-jig/jig/truth.db

 Congratulations for a successful installation!!

**************************************************************************
### Run the Jig
- Your systems should call python jig/jig.py to get feedback for each iteration of retrieval. The program outputs a json dumped string. It provides feedback to your returned documents. Only positive feedback will be shown be shown.  Use the following command:

- Call the Jig
  ``` shell
    >$ python jig/jig.py -r runid -topic topic_id -docs docno1:rankingscore docno2:rankingscore docno3:rankingscore docno4:rankingscore docno5:rankingscore
  ```

    + where:

        - runid: An identifier used to declare run
        - topic_id: the id of the topic you are working on
        - docno1, docno2 ...: the five document ids that your system returned. It needs to be the document ids in TREC DD datasets.
        - ranking score: the ranking score of each document given from your sysetm

- Each feedback is a json format for each document in the following a document
    ``` shell
    [
     {
         "topic_id": "DD15-1"
         "ranking_score": "123",
         "on_topic": "1",
         "doc_id": "1335424206-b5476b1b8bf25b179bcf92cfda23d975",
         "subtopics": [
             {
                 "passage_text": "this is a passage of relevant text from the document 'stream_id', relevant to the 'subtopic_id' below with the 'rating' below",
                 "rating": 3,
                 "subtopic_id": "DD15-1.4",
             }
         ],
     },
     { ... }
    ]

    ```
    + where:
        - docid: the id of a returned document
        - subtopic_id: the id of a relevant subtopic that your returned document covers
        - passage_text: the content of a relevant passage that your returned document covers
        - rating: the relevance grade provided by NIST assessors. -1/0/1: marginally relevant (Note that: ratings -1 or 0 or 1 all mean marginally relevant), 2: relevant, 3: highly relevant, 4: key results. The relevance grades refer to the relevance level of your document to the whole topic.
        - ranking score: the ranking score of each document given from your system

- Each run will generate a run file, format as follows. A sample run can be found under the sample_run directory.
    ``` shell
        DD15-19	0	1321539720-bda73abbdc0976a22fdcf2867bcba50c	369.000000	1	DD15-19.2:2|DD15-19.3:3|DD15-19.1:2
        DD15-19	0	1321528320-95095422b0dca9302b91f9366080a465	997.000000	1	DD15-19.1:3|DD15-19.1:2|DD15-19.1:1
        DD15-19	0	1321606560-c48d386baef428bb7b8b0ec657ca8259	643.000000	1	DD15-19.1:3|DD15-19.1:2|DD15-19.1:1
        DD15-19	0	1333190700-2395ddd7ef04f4e0346e107673709d64	754.000000	0	NULL
        DD15-19	0	1321626300-f3db383ecdaf70b993c6b16e50e40244	965.000000	1	DD15-19.1:3
    ```

    + where:
        - docid: the id of a returned document
        - subtopic_id: the id of a relevant subtopic that your returned document covers
        - passage_text: the content of a relevant passage that your returned document covers
        - rating: the relevance grade provided by NIST assessors. -1/0/1: marginally relevant (Note that: ratings -1 or 0 or 1 all mean marginally relevant), 2: relevant, 3: highly relevant, 4: key results. The relevance grades refer to the relevance level of your document to the whole topic.
        - ranking score: the ranking score of each document given from your system

- Note that subtopic_ids are global ids, i.e., a certain topic might contains subtopic with id 12, 45, 101, 103...

**************************************************************************
### A Sample Input and Output
- An intermediate step:
    + Give jig the topic id and 5 document id with their ranking score:
        ``` shell
        > python jig.py -runid gu_1 -topic DD15-1 -docs 1322120460-d6783cba6ad386f4444dcc2679637e0b:833.00 1322509200-f67659162ce908cc510881a6b6eabc8b:500.00 1321860780-f9c69177db43b0f810ce03c822576c5c:123.00 1327908780-d9ad76f0947e2acd79cba3acd5f449f7:34.00 1321379940-4227a3d1f425b32f9f8595739ef2b8c3:5.00
        ```

    + The run file generated (text content of passage are not shown in the run file):

    ``` shell
        > DD15-1 1322120460-d6783cba6ad386f4444dcc2679637e0b 833.00 1 DD15-1.1:3|DD15-1.4:2|DD15-1.4:2|DD15-1.4:2|DD15-1.4:2|DD15-1.4:2|DD15-1.2:2|DD15-1.2:2

        > DD15-1 1322509200-f67659162ce908cc510881a6b6eabc8b 500.00 1 DD15-1.1:3

        > DD15-1 1321860780-f9c69177db43b0f810ce03c822576c5c 123.00	1 DD15-1.1:3

        > DD15-1 1327908780-d9ad76f0947e2acd79cba3acd5f449f7 34.00 1 DD15-1.3:2|DD15-1.1:2

        > DD15-1 1321379940-4227a3d1f425b32f9f8595739ef2b8c3 5.00 0
    ```
**************************************************************************

### Metrics
- We support five metrics as follows, the scripts for these metrics can be found under the ./scorer directory.
- Sample truth file and run file can be found under the ./sample/directory
    + qrel.txt: a sample ground truth
    + runfile: a sample run
- Sample use of the metrics
    + Cube Test and Average Cube Test (results printing to screen)

      ``` shell
        >$ perl cubeTest_dd.pl  /path/to/truth/file /path/to/run/file 50
      ```

    + Alpha-nDCG per iteration and nERR-IA per iteration (results written in local files)

      ``` shell
        >$ ./ndeval  /path/to/truth/file /path/to/run/file
      ```

    + SnDCG per iteration (results written in local files)

      ``` shell
        >$ perl nSDCG_per_iteration.pl  /path/to/truth/file /path/to/run/file 5
      ```
    + Precision (results print to screen)

      ``` shell
        >$ python precision.py -qrel /path/to/truth/file -run /path/to/run/file
      ```
