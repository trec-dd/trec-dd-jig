# -*- coding: utf-8 -*-

from subprocess import call
import click


def run_all():
    cubetest()
    stage_aware_cubetest()
    nDCG()
    snDCG()


def cubetest(truth, run):
    print 'Calling cubetest'
    call(["perl", "cubeTest_dd.pl", truth, run, '50'])


def stage_aware_cubetest(truth, run):
    print 'Calling stage aware cubetest'
    call(["perl", "cubeTest_dd_s.pl", truth, run, '50'])


def nDCG(truth, run):
    print 'Calling nDCG'
    call(["./ndeval", truth, run])
    # ndeval [options] qrels run (-help for full usage information)


def snDCG(truth, run):
    print 'Calling snDCG'
    call(["perl", "nSDCG_per_iteration.pl", truth, run, '5'])


choice = {
    # 'cubetest': cubetest,
    # 'stage_aware_cubetest': stage_aware_cubetest,
    'nDCG': nDCG,
    # 'snDCG': snDCG,
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

        # print truth
        # print run
        # print config
        # if config == 'all':
        #     for key, func in choice.iteritems():
        #         func()
        # else:
        #     func = choice[config]
        #     func()


if __name__ == '__main__':
    score()
