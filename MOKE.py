# -*- coding: utf-8 -*-

from os import listdir, walk
from os.path import isdir, join
import sys
import glob
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as lines

class single_mes:  # class for single measurement
    def __init__(self, name, path=None, phi=None, H=None):
        self.name = name
        self.path = path
        self.phi = phi
        self.H = H

    def read_file (self):
        f = open(self.path, 'r')
        phi = []
        H = []
        for line in f:
            phi.append(float(line.split()[1]))
            H.append(float(line.split()[0]))
        f.close()
        self.phi = phi
        self.H = H

    def single_pic (self, name = None):
        if name == None:
            name = self.name
        exit_file = name + '.png'
        fig, ax = plt.subplots(1, 1, figsize=(8, 8))
        ax.set_ylabel("phi, milidegree")
        ax.set_xlabel("H, Oe")
        ax.plot(self.H, self.phi, label=name)
        ax.legend()
        fig.savefig(exit_file)
        plt.close()

def read_dir (path):
    files = glob.glob(path + "/*.DAT")
    mes = []
    for file in files:
        name = file.replace(path + '/', '')
        name = name.replace(".DAT", '')
        a = single_mes(name, file)
        a.read_file()
        mes.append(a)
    return mes


mypath = "{}".format(sys.argv[1])
mes = read_dir(mypath)
exit_file = 'exit.png'
fig, ax = plt.subplots(1, 1, figsize=(10, 10))
ax.set_ylabel("phi, milidegree")
ax.set_xlabel("H, Oe")
for leaf in mes:
    ax.plot(leaf.H, leaf.phi, label=leaf.name)
ax.legend()
fig.savefig(exit_file)
plt.close()