"""
analyze.py

* class Analyzer - Uploads the snapshotted state from the specified pickle_jar.
Provides abstractions for plotting the change in register/memory taint across the 
execution of the program. 
Outputs generated graphs to the directory <pickle_jar_path>/data/
--memory_graph and --register_graph flags determine which graphs to generate.

# Example Execution.
# analyzer.py --pickle_jar=<pickle_jar_path> --memory_graph --register_graph
"""

import sys
import os
import click
import pickle
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from interpreter import *

class Analyzer():
    def __init__(self, pickle_jar):
        self.pickle_jar = pickle_jar
        self.wd = os.getcwd()
        self.interpreters = []

        # Load the pickles
        self.load_pickled_state()

    def load_pickle(self, filename):
        file = open("{}/pickles/{}".format(self.pickle_jar, filename), 'rb')
        return pickle.load(file)

    def load_pickled_state(self):
        path = "{}/{}/pickles".format(self.wd, self.pickle_jar)
        pickles = os.listdir(path)
        for pfile in pickles:
            intr = self.load_pickle(pfile)
            self.interpreters.append(intr)
        print("Loaded {} interpreters".format(len(self.interpreters)))
        return

    def plot_register_taint(self):
        path = "{}/{}/data".format(self.wd, self.pickle_jar)

        y = [intr.tracker.percentage_tainted_registers() for intr in self.interpreters]
        x = list(range(len(self.interpreters)))
        plt.plot(x, y)
        plt.savefig('{}/registers_taint_graph.jpg'.format(path))
        plt.close()

    def plot_memory_taint(self):
        path = "{}/{}/data".format(self.wd, self.pickle_jar)

        y = [intr.tracker.percentage_tainted_memory() for intr in self.interpreters]
        x = list(range(len(self.interpreters)))
        plt.plot(x, y)
        plt.savefig('{}/memory_taint_graph.jpg'.format(path))
        plt.close()


@click.command()
@click.option('--pickle_jar', required=True, help='Requires a path to a pickle jar.')
@click.option('--memory_graph/--no-memory_graph', default=False)
@click.option('--register_graph/--no-register_graph', default=False)
def main(pickle_jar, memory_graph, register_graph):
    analyzer = Analyzer(pickle_jar)

    if register_graph:
        analyzer.plot_register_taint()

    if memory_graph:
        analyzer.plot_memory_taint()

    return


if __name__ == '__main__':
    main()
