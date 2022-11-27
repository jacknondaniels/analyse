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
    def __init__(self, name, path=None, phi_b=None, H_b=None, phi_f=None, H_f=None):
        self.name = name
        self.path = path
        self.phi_b = phi_b
        self.H_b = H_b
        self.phi_f = phi_f
        self.H_f = H_f

    def read_file (self):
        f = open(self.path, 'r')
        phi_b = []
        H_b = []
        phi_f = []
        H_f = []
        cur = 2000
        for line in f:
            h = float(line.split()[0])
            if (h <= cur):
                phi_b.append(float(line.split()[1]))
                H_b.append(h)
            else:
                phi_f.append(float(line.split()[1]))
                H_f.append(h)
            cur = h
        f.close()
        self.phi_b = phi_b
        self.H_b = H_b
        self.phi_f = phi_f
        self.H_f = H_f

    def single_pic (self, ax, name = None):
        if name == None:
            name = self.name
        exit_file = name + '.png'
        ax.plot(self.H_b, self.phi_b, label=name+' backwards')
        ax.plot(self.H_f, self.phi_f, label=name+' forwards')        

    def optimize (self, plt):
        popt, pcov = curve_fit(arc, self.H, self.phi)
        plt.plot (self.H, arc(np.array(self.H), *popt), label = 'fit: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt))
        plt.plot (self.H, self.phi-arc(np.array(self.H), *popt), label = 'minus')
        return popt

    def normalize (self, ax = None):
        upper_h = []
        upper_phi =[]
        lower_h = []
        lower_phi = []
        border = 200
        for i in range(len(self.H_b)):
            h = self.H_b[i]
            if (h > border):
                upper_h.append(h)
                upper_phi.append(self.phi_b[i])
            elif (h< ( -1*border)):
                lower_h.append(h)
                lower_phi.append(self.phi_b[i])

        for i in range(len(self.H_f)):
            h = self.H_f[i]
            if (h > border):
                upper_h.append(h)
                upper_phi.append(self.phi_f[i])
            elif (h < (-1*border)):
                lower_h.append(h)
                lower_phi.append(self.phi_f[i])

        popt_up, _ = curve_fit(linear, upper_h, upper_phi)
        popt_low, _ = curve_fit(linear, lower_h, lower_phi)
        a = (popt_up[0]+popt_low[0])/2
        b = abs(popt_up[1] - popt_low[1])/2
        print ('steep: a=%5.3f, saturation b=%5.3f' %tuple([a, b]))
        if (ax):
            h1 = np.arange(-1000, 1000, 20)
            ax.plot(h1, popt_up[0]*h1 + popt_up[1], label='fit upper')
            ax.plot(h1, popt_low[0]*h1 + popt_low[1], label='fit lower')             
            ax.plot (self.H_f, np.array(self.phi_f)-a*np.array(self.H_f), label = 'normalized_fw')



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
exit_file = 'fitting_1.png'
fig, ax = plt.subplots(1, 1, figsize=(10, 10))
for leaf in mes:
    leaf.single_pic(ax)
    leaf.normalize(ax)
    break
ax.set_ylabel("phi, milidegree")
ax.set_xlabel("H, Oe")
ax.legend()
fig.savefig(exit_file)
plt.close()