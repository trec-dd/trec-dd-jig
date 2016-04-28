# trec-dd-jig

##### This is the readme file of  the user simulator (jig) package for the TREC 2016 Dynamic Domain (DD) Track.
##### The package is for research use only.

##### For technical questions, please submit your request to google group https://groups.google.com/forum/#!forum/trec-dd

**************************************************************************

### What are inside this package:

* a user simulator (jig),
* a sample search system (built on top of Lemur) interacting with the jig,
* a scorer outputs the cubetest scores,

**************************************************************************

### Packages needs to installed before using the jig:
##### Required:
 1. Pip

    Install pip (or pip3 for python3) if it is not already installed:

    - Ubuntu/Linux 64-bit
         > $ sudo apt-get install python-pip python-dev

    - Mac OS X
          >$ sudo easy_install pip

 2. Virtualenv

     A Virtual Environment is a tool to keep the dependencies required by different projects in separate places, by creating virtual Python environments for them.
    - Ubuntu/Linux 64-bit
         > $ sudo apt-get install python-dev python-virtualenv

    - Mac OS X
         > $ sudo pip install --upgrade virtualenv
3. Dossier.label

    - Brief introduction

    -  Mac OS X
         > $ sudo pip install --upgrade dossier.label


##### Optional:
lemur/Indri (You can use lemur as a sample search system to interact with jig).
  - Download the Lemur/Indri software package indri-5.0.tar.gz from https://sourceforge.net/projects/lemur/files/lemur/indri-5.0/. Or, you can use the one provided in our package.
   - Unpack the Lemur/Indri software package
   - Assume you put Lemur/Indri into a directory named /yourhomedirectory/indri-5.0/, install it by the following commands. Note you will need to enable the --with-lemur option.
        > cd indri-5.0
        > mkdir install
        > chmod +x ./configure
        > ./configure --prefix=/yourhomedirectory/indri-5.0/install/ --with-lemur=/yourhomedirectory/indri-5.0/install/
        > make
        > make install

### System requirement for installing the jig:
- Works best under Python 2.7.

### Input:

- Topics (ground truth) must be the one downloaded from NIST. (http://trec.nist.gov/act_part/tracks16.html)

### Outputs:
- Intermedia feedback
    + See http://trec-dd.org/guideline.html#run_format
    + Final output (not decided yet, could be the same as above). (http://trec-dd.org/guideline.html#run_format)

### Installation steps:
- Download trec_dd.tar.gz and unpack it.
- Move the unpacked directory under the lemur(or your trec-dd system) directory, that is,
        > mv trec_dd_2015_release /yourhomedirectory/indri-5.0/
- Go to the trec_dd_2015_release directory
        > cd  /yourhomedirectory/indri-5.0/trec_dd_2015_release
- Download your topics (with ground truth)  from the TREC Active Participants Home Page. Copy it and put it under
        > ./trec_dd_2015_release/topics/
- Setup a sqlite database in ./trec_dd_2015_release/jig/truth.db
        > sh config.sh --topics yourtopicfile.xml
- (Optional) Install the lemur/indri sample DD system. If you make any changes to the sample system, you will need to run this install.sh again to see the effects
        > sh install.sh
- You will see a bin directory in /yourhomedirectory/indri-5.0/trec_dd_2015_release.
Test the sample DD system:
        > sh run_lemur_dd.sh
-  Please remember to change this shell script so that it contains the correct paths to your topic file and to your index/indices

 Congratulations for a successful installation!!

**************************************************************************
### Running Jig
- Your systems should call python jig/jig.py to get feedback for each iteration of retrieval. The program outputs a json dumped string. It provides feedback to your returned documents. Only positive feedback will be shown be shown.  Use the following command:
    > python jig/jig.py -c config_file step topic_id docno1 docno2 docno3 docno4 docno5

    where:
    + config_file: the path of the configuration file, default is ./trec_dd_2015_release/topics/config.yaml.
    + topic_id: the id of the topic you are working on
    + docno1, docno2 ...: the five document ids that your system returned. It needs to be the document ids in TREC DD datasets.

- Each feedback is a tuple of (docid, subtopic_id, passage_text, rating) for a document, where:
    + docid: the id of a returned document
    + subtopic_id: the id of a relevant subtopic that your returned document covers
    + passage_text: the content of a relevant passage that your returned document covers
    + rating: the relevance grade provided by NIST assessors. -1/0/1: marginally relevant (Note that: ratings -1 or 0 or 1 all mean marginally relevant), 2: relevant, 3: highly relevant, 4: key results. The relevance grades refer to the relevance level of your document to the whole topic.

- Note that subtopic_ids are global ids, i.e., a certain topic might contains subtopic with id 12, 45, 101, 103...

**************************************************************************
### A Sample Use
-- Remain to be added. --

**************************************************************************

### Metrics
- We support five metrics as follows:
    + Cube Test
    + Stage-aware Cube Test
    + Alpha-nDCG per iteration
    + Nerr-ia per iteration
    + SnDCG per iteration

