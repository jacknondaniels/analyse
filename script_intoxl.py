# -*- coding: utf-8 -*-

from os import listdir, walk
from os.path import isfile, join
import sys
import glob
import pandas as pd

count = 1
smooth = 1


class single_mes:  # class for single measurement
    def __init__(self, wl, depth, path=None, mes=None):
        self.wl = wl
        self.depth = depth
        self.path = path
        self.mes = mes

    def read(self):
        f = open(self.path, 'r')
        x = []
        get_smooth = []
        local_count = 1
        for line in f:
            if smooth == 1:
                x.append(float(line.split()[1]))
            else:
                if (local_count % smooth) == 0:
                    av = sum(get_smooth) / len(get_smooth)
                    x.append(av)
                    get_smooth = [float(line.split()[1])]
                else:
                    get_smooth.append(float(line.split()[1]))
                local_count = local_count + 1
        f.close()
        x.reverse()
        self.mes = x


def reading_meta_dir(path):  # reading directory with all the dirs
    dirs = next(walk(path))[1]
    return dirs


def reading_dir(mypath):
    onlyfiles = glob.glob(mypath + "/*.txt")
    mes = []
    range_of_depth_to_sort = set()
    range_of_labels = set()
    for file in onlyfiles:
        split = file.replace(mypath + '/22522-(Las405)-Vol-', '')
        split = split.split('_')
        while True:
            try:
                split.remove('')
            except ValueError:
                break
        wl = split[0]
        wl = wl.replace('nm)', '')
        mes.append(single_mes(wl, split[7], file))
        range_of_depth_to_sort.add(float(split[7]))
        range_of_labels.add(wl)

    range_of_depth_sorted = sorted(list(range_of_depth_to_sort))
    range_of_depth = []
    for depth in range_of_depth_sorted:
        range_of_depth.append('%g'%(depth))

    range_of_wavelength = {}
    for leaf in mes:
        leaf.read()
        if leaf.wl in range_of_labels:
            f = open(leaf.path, 'r')
            x = []
            get_smooth = []
            local_count = 1
            for line in f:
                if smooth == 1:
                    x.append(float(line.split()[0]))
                else:
                    if (local_count % smooth) == 0:
                        av = sum(get_smooth) / len(get_smooth)
                        x.append(av)
                        get_smooth = [float(line.split()[0])]
                    else:
                        get_smooth.append(float(line.split()[0]))
                    local_count = local_count + 1
            f.close()
            x.reverse()
            wave = single_mes(leaf.wl, '0', leaf.path, mes=x)
            range_of_wavelength[leaf.wl] = wave
            range_of_labels.remove(leaf.wl)
    return mes, range_of_wavelength, range_of_depth


def into_excel(name, mes, range_of_wavelength):
    exit_file = name + '.xlsx'
    writer = pd.ExcelWriter(exit_file, engine='xlsxwriter')
    lists = []  # names for lists
    for spectr in range_of_wavelength.values():
        name_of_list = spectr.wl
        df1 = {}
        for leaf in mes:
            if (leaf.wl == name_of_list):
                df1[leaf.depth] = leaf.mes

        whynot = []
        for i in df1.keys():
            whynot.append(float(i))
        whynot1 = sorted(whynot, reverse=True)
        depth_range = []
        for t in whynot1:
            depth_range.append(str(t))

        table = pd.DataFrame({'wavelength': spectr.mes})
        for depth in depth_range:
            table[depth] = df1[depth]
        table.to_excel(writer, name_of_list, index=False)
    writer.save()
    return writer


def into_excel_merged(name, mes, range_of_wavelength, range_of_depth):
    exit_file = name + '.xlsx'
    writer = pd.ExcelWriter(exit_file, engine='xlsxwriter')

    # sorting labels
    unsorted_labels = set()
    for leaf in range_of_wavelength.values():
        unsorted_labels.add(leaf.wl)
    whynot = []
    for i in unsorted_labels:
        whynot.append(int(i))
    whynot = sorted(whynot)
    labels_ranged = []
    for t in whynot:
        labels_ranged.append(str(t))
    # now labels are ranged and stored in labels_ranged

    once = True
    table = pd.DataFrame()
    for depth in range_of_depth:
        df1 = {}
        unmerged_mes = {}
        for label in labels_ranged:
            for leaf in mes:
                if (leaf.wl == label) and (leaf.depth == depth):
                    print("was here")
                    unmerged_mes[label] = leaf
        if (once):
            once = False
            _, table['wavelength'] = merging_spectra(labels_ranged, range_of_wavelength, unmerged_mes)
        df1[depth], _ = merging_spectra(labels_ranged, range_of_wavelength, unmerged_mes)
        table[depth] = df1[depth]

    table.to_excel(writer, 'merged', index=False)
    writer.save()
    return (writer)


def merging_spectra(labels_ranged, range_of_wavelength, mes):
    # it works now
    merged_measurement = []
    merged_wavelength = []
    average_coef = [1.0]

    first = labels_ranged[0]
    for i in range(len(range_of_wavelength[first].mes)):
        merged_wavelength.append(range_of_wavelength[first].mes[i])
        merged_measurement.append(mes[first].mes[i])

    for i in range(len(labels_ranged)):
        try:
            print(labels_ranged[i])
            first = labels_ranged[i]
            second = labels_ranged[i + 1]
            semaphor = True
            critical_ind = 0
            length = len(merged_wavelength) - 1
            get_average_coef = []
            while (merged_wavelength[length - critical_ind] - range_of_wavelength[second].mes[0] <= 10) and (
                    merged_wavelength[length - critical_ind] - range_of_wavelength[second].mes[0] > 0):
                critical_ind += 1
            for j in range(0, critical_ind):
                try:
                    coef = merged_measurement[-j - 1] / mes[second].mes[j]
                except ArithmeticError:
                    coef = 1
                get_average_coef.append(coef)
            average_coef.append(sum(get_average_coef) / len(get_average_coef))
            for f in range(critical_ind, len(range_of_wavelength[second].mes) - 1):
                merged_wavelength.append(range_of_wavelength[second].mes[f])
                merged_measurement.append(mes[second].mes[f] * average_coef[i])
        except KeyError:
            for f in range(critical_ind, len(range_of_wavelength[second].mes) - 1):
                merged_wavelength.append(range_of_wavelength[second].mes[f])
                merged_measurement.append(0)
        except IndexError:
            break
    return merged_measurement, merged_wavelength


mypath = "{}".format(sys.argv[1])
dirs = reading_meta_dir(mypath)
for dr in dirs:
    name = mypath + '/' + dr
    measur, rol, rod = reading_dir(name)
    into_excel_merged(dr, measur, rol, rod)
