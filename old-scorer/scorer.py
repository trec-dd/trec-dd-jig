# -*- coding: utf-8 -*-
# Run all the old-scorer in one trial
from subprocess import call
import click


def run_all():
    cubetest()
    stage_aware_cubetest()
    nDCG()
    snDCG()


def cubetest(truth, run):
    print 'Calling cubetest'
    # results print to screen
    call(["perl", "cubeTest_dd.pl", truth, run, '50', '>'])


def stage_aware_cubetest(truth, run):
    print 'Calling stage aware cubetest'
    # results print to screen
    call(["perl", "cubeTest_dd_s.pl", truth, run, '50'])


def nDCG(truth, run):
    print 'Calling nDCG'
    # results written into file
    call(["./ndeval", truth, run])
    # ndeval [options] qrels.txt run (-help for full usage information)


def snDCG(truth, run):
    print 'Calling snDCG'
    # results written into file
    call(["perl", "snDCG_per_iteration.pl", truth, run, '5'])

def pr(truth, run):
    print 'Calling P@R'
    # results print to screen
    call(["perl", "cubeTest_dd.pl", truth, run, '50'])

choice = {
    'cubetest': cubetest,
    'stage_aware_cubetest': stage_aware_cubetest,
    'nDCG': nDCG,
    'snDCG': snDCG,
    'PR': pr,
}


@click.command()
@click.option('-truth', type=click.Path(exists=True), help='ground truth file path')
@click.option('-run', type=click.Path(exists=True), help='run file path')
# @click.option('-config', '-c',
#               type=click.Choice(['all', 'cubetest', 'stage_aware_cubetest',
#                                 'nDCG', 'SnDCG']),
#               default='all',  help='config option')

def score(truth, run):
    for key, func in choice.iteritems():
        func(truth, run)


if __name__ == '__main__':
    score()
