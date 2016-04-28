from subprocess import call
import click


def run_all():
    cubetest()
    stage_aware_cubetest()
    nDCG()
    snDCG()


def cubetest():
    print 'haha'
    call(["ls", "-l"])


def stage_aware_cubetest():
    pass


def nDCG():
    pass


def snDCG():
    pass

choice = {
    'cubetest': cubetest,
    'stage_aware_cubetest': stage_aware_cubetest,
    'nDCG': nDCG,
    'snDCG': snDCG,
}


@click.command()
@click.option('-truth', type=click.Path(exists=True), help='source file path')
@click.option('-run', type=click.Path(exists=True), help='target file path')
@click.option('—config', '-c', type=click.Choice(['all', 'a','b','c', 'd']), default='all',  help='config option')

def score(truth, run, config):
    # print truth
    # print run
    print config
    if config == 'all':
        for key, func in choice.iteritems():
            func()
    else:
        func = choice[config]
        func()

if __name__ == '__main__':
    score()
