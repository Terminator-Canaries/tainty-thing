"""
analyze.py

"""

import sys
import os
import click
import pickle
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from interpreter import *

# How to execute.

# analyzer.py pickle_jar --memory_graph --register_graph

class Analyzer():
    def __init__(self, pickle_jar):
        self.pickle_jar = pickle_jar
        self.wd = os.getcwd()
        self.interpreterers = []

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
            self.interpreterers.append(intr)
        print("Loaded {} interpreterers".format(len(self.interpreterers)))
        return

    def plot_register_taint(self):
        path = "{}/{}/data".format(self.wd, self.pickle_jar)

        y = [intr.tracker.percentage_tainted_registers() for intr in self.interpreterers]
        x = list(range(len(self.interpreterers)))
        plt.plot(x,y)
        plt.savefig('{}/registers_taint_graph.jpg'.format(path))
        plt.close()

    def plot_memory_taint(self):
        path = "{}/{}/data".format(self.wd, self.pickle_jar)

        y = [intr.tracker.percentage_tainted_memory() for intr in self.interpreterers]
        x = list(range(len(self.interpreterers)))
        plt.plot(x,y)
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
