# -*- coding: utf-8 -*-

from os import listdir, walk
from os.path import isdir, join
import sys
import glob
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as lines
from scipy.optimize import curve_fit

def linear(x, a, b):
    return a*x + b

def arc(x, a, b, c):
    return c*np.tanh(a*x) + b



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
            h = float(line.split()[0])
            if (h >= -250) and (h <= 250):
                phi.append(float(line.split()[1]))
                H.append(h)
        f.close()
        self.phi = np.array(phi)
        self.H = np.array(H)

    def single_pic (self, ax, name = None):
        if name == None:
            name = self.name
        exit_file = name + '.png'
        ax.plot(self.H, self.phi, label=name)

    def optimize (self, plt):
        popt, pcov = curve_fit(arc, self.H, self.phi)
        plt.plot (self.H, arc(self.H, *popt), label = 'fit: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt))
        plt.plot (self.H, self.phi-arc(self.H, *popt), label = 'minus')
        return popt

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
exit_file = 'fitting.png'
fig, ax = plt.subplots(1, 1, figsize=(10, 10))
for leaf in mes:
    leaf.single_pic(ax)
    leaf.optimize(ax)
ax.set_ylabel("phi, milidegree")
ax.set_xlabel("H, Oe")
ax.legend()
fig.savefig(exit_file)
plt.close()