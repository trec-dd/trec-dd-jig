from collections import defaultdict
import click

def preProcess(run, ct):
    runfile = open(run)
    output = open(run + '_' + str(ct), 'w')
    while 1:
        line = runfile.readline()
        if not line:
            break
        else:
            result = line.split('\t')
            if int(result[1]) <= int(ct):
                output.write(line)

@click.command()
@click.option('-run', type=click.Path(exists=True))
@click.option('-ct', type=click.INT)
def main(run, ct):
    runfile = open(run, 'r')
    preProcess(run, ct)

if __name__ == '__main__':
    main()
