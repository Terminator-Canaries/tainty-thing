"""
backtrack.py

"""

import sys
import os
import click
import pickle
from interpreter import *

# Example Execution.
#python backtrack.py --pickle_path=pickle_cabinet/jar_get_loc/pickles/state-instr008-line009

def fetch_interpreter(pickle_path):
    file = open("{}".format(pickle_path), 'rb')
    return pickle.load(file)

def backtrack(pickle_path):
    interpreter = fetch_interpreter(pickle_path)

    # Run interpreter.
    while(interpreter.run()):
        print("")

    return


@click.command()
@click.option('--pickle_path', required=True, help='Requires a path to a specific pickle.')

def main(pickle_path):

    backtrack(pickle_path)
    return

if __name__ == '__main__':
    main()
