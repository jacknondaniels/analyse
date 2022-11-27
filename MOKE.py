# -*- coding: utf-8 -*-

from os import listdir, walk
from os.path import isdir, join
import sys
import glob
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as lines
from scipy.optimize import curve_fit

border = 300 #border between tail and fit 
def linear(x, a, b):
    return a*x + b

def arc(x, a, b, c):
    return c*np.tanh(a*x + b)



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
        ax.plot(self.H_b, self.phi_b, label=name+' b')
        ax.plot(self.H_f, self.phi_f, label=name+' f')        

    def optimize (self, plt):
        fit_phi = []
        fit_h = []
        for i in range(len(self.H_f)):
            h = self.H_f[i]
            if (abs(h) < border):
                fit_h.append(h)
                fit_phi.append(self.phi_f[i])
        popt_f, _ = curve_fit(arc, fit_h, fit_phi)
        plt.plot (self.H_f, arc(np.array(self.H_f), *popt_f), label = 'fit c*tanh(ax+b): a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt_f))
        fit_phi.clear()
        fit_h.clear()
        for j in range(len(self.H_b)):
            h = self.H_b[j]
            if (abs(h) < border):
                fit_h.append(h)
                fit_phi.append(self.phi_b[j])
        popt_b, _ = curve_fit(arc, fit_h, fit_phi)
        plt.plot (self.H_b, arc(np.array(self.H_b), *popt_b), label = 'fit c*tanh(ax+b): a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt_b))
        coer = (abs(popt_f[1]/popt_f[0])+ abs(popt_b[1]/popt_b[0]))/2
        return coer

    def normalize (self, ax = None):
        upper_h = []
        upper_phi =[]
        lower_h = []
        lower_phi = []
        border1 = 300 #border for tail part
        for i in range(len(self.H_b)):
            h = self.H_b[i]
            if (h > border1):
                upper_h.append(h)
                upper_phi.append(self.phi_b[i])
            elif (h< ( -1*border1)):
                lower_h.append(h)
                lower_phi.append(self.phi_b[i])

        for i in range(len(self.H_f)):
            h = self.H_f[i]
            if (h > border1):
                upper_h.append(h)
                upper_phi.append(self.phi_f[i])
            elif (h < (-1*border1)):
                lower_h.append(h)
                lower_phi.append(self.phi_f[i])

        popt_up, _ = curve_fit(linear, upper_h, upper_phi)
        popt_low, _ = curve_fit(linear, lower_h, lower_phi)
        a = (popt_up[0]+popt_low[0])/2
        b = (popt_up[1] + popt_low[1])/2
        sat = (popt_up[1] - popt_low[1])/2
        print ('steep: a=%5.3f, shift b=%5.3f, sat=%5.3f' %tuple([a, b, sat]))
        norm = single_mes(name = self.name + ' sat=%5.3f mdg' %sat, path=None, phi_b=np.array(self.phi_b)-a*np.array(self.H_b) - b, H_b=self.H_b, phi_f=np.array(self.phi_f)-a*np.array(self.H_f) - b, H_f=self.H_f)
        if (ax):            
            norm.single_pic(ax)
        return norm, sat


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
exit_file = 'dif_thickness_new.png'
fig, ax = plt.subplots(1, 6, figsize = (160, 20))
saturation = {}
coer = {}
counter = 0
for leaf in mes:
    norm, b = leaf.normalize(ax[counter])
    c = norm.optimize(ax[counter])
    saturation[leaf.name] = b
    coer[leaf.name] = c
    ax[counter].set_title(leaf.name)
    ax[counter].legend()
    counter = counter+1
#ax.set_ylabel("phi, milidegree")
#ax.set_xlabel("H, Oe")
#ax.legend()
fig.savefig(exit_file)
plt.close()
print (saturation)
print (coer)
