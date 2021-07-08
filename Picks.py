import math
from PyQt5 import QtGui
import pyqtgraph as pg
from datetime import datetime
import MainWindow
import os

MAX_PICKS = 26


class Picks:
    def __init__(self):
        self.picks1 = [None for x in range(MAX_PICKS)]
        self.picks2 = [None for x in range(MAX_PICKS)]
        self.pick_num = [-1 for x in range(MAX_PICKS)]
        self.count = 0

    def add_pick(self, pick):
        label = ord(pick.label.format[0]) - 65
        if 0 <= label <= 25:
            if self.picks1[label] is None:
                self.picks1[label] = pick
                self.pick_num[label] = self.count
                self.count += 1
                return 2, None
            elif self.picks2[label] is None:
                p = pg.InfiniteLine(angle=90, movable=False,
                                    pen=MainWindow.COLORS[self.pick_num[label] % MainWindow.COLORS_NUM],
                                    label=pick.label.format[:-1] + "2",
                                    labelOpts={'position': 0.1,
                                               'color': MainWindow.COLORS[self.pick_num[label] % MainWindow.COLORS_NUM],
                                               'fill': (200, 200, 200, 50), 'movable': True})
                self.picks2[label] = p
                return 1, p
            else:
                print("Can not accept more than 2 picks with same label")
                return 0, None
        else:
            print("Only accept label between A-Z")
            return 0, None

    def get_y_values(self, pick, dataset):
        y_values = []
        count = len(dataset)
        x = pick.p[0]
        for i in range(count):
            dt = dataset[i].get_x()
            if dt[0] <= x <= dt[-1]:
                for j in range(len(dt)):
                    if dt[j] > x:
                        y_values.append(dataset[i].get_y()[j])
                        break
            else:
                y_values.append(None)
        return y_values

    def get_analysis_data(self, dt1, dt2, dataset):
        count = len(dataset)
        sum = [0.0 for x in range(count)]
        c = [0.0 for x in range(count)]
        mean = [0.0 for x in range(count)]
        std = [0.0 for x in range(count)]

        for i in range(count):
            dt = dataset[i].get_x()
            if dt[-1] < dt1 or dt2 < dt[0]:
                mean[i] = None
                std[i] = None
                continue

            for j in range(len(dt)):
                if dt1 <= dt[j] <= dt2:
                    y = dataset[i].get_y()[j]
                    sum[i] += y
                    c[i] += 1
            mean[i] = round(sum[i] / c[i], 3)

            dsum = 0.0
            for j in range(len(dt)):
                if dt1 <= dt[j] <= dt2:
                    y = dataset[i].get_y()[j]
                    dsum += math.pow((y - mean[i]), 2)
            std[i] = round(math.sqrt(dsum / c[i]), 3)

        return mean, std

    def save_picks(self, dataset):
        if self.count:
            desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
            f = open(desktop + "/PICKS.txt", 'w')
            f.write("       Date      Time      ")
            for i in range(len(dataset)):
                f.write("   {0}".format(i).ljust(15))
            f.write("\n")

            for i in range(MAX_PICKS):
                if self.picks1[i] is not None:
                    y_values = self.get_y_values(self.picks1[i], dataset)
                    f.write(self.picks1[i].label.format + datetime.fromtimestamp(self.picks1[i].p[0]).
                            strftime(': %Y/%m/%d %H:%M:%S    '))
                    for j in range(len(y_values)):
                        f.write(str(y_values[j]).ljust(15))
                    f.write("\n")

                if self.picks2[i] is not None:
                    y_values = self.get_y_values(self.picks2[i], dataset)
                    f.write(self.picks2[i].label.format + datetime.fromtimestamp(self.picks2[i].p[0]).
                            strftime(': %Y/%m/%d %H:%M:%S    '))
                    for j in range(len(y_values)):
                        f.write(str(y_values[j]).ljust(15))
                    f.write("\n")

            mean = [[] for x in range(MAX_PICKS)]
            std = [[] for x in range(MAX_PICKS)]

            for i in range(MAX_PICKS):
                if self.picks1[i] is not None and self.picks2[i] is not None and \
                        self.picks2[i].p[0] > self.picks1[i].p[0]:
                    mean[i], std[i] = self.get_analysis_data(self.picks1[i].p[0], self.picks2[i].p[0],
                                                                      dataset)

            f.write("\nMean                       ")
            for i in range(len(dataset)):
                f.write("   {0}".format(i).ljust(15))
            f.write("\n")

            for i in range(MAX_PICKS):
                if self.picks1[i] is not None and self.picks2[i] is not None and \
                        self.picks2[i].p[0] > self.picks1[i].p[0]:
                    f.write(self.picks1[i].label.format[:-1] + ":                         ")
                    for j in range(len(mean[i])):
                        f.write(str(mean[i][j]).ljust(15))
                    f.write("\n")

            f.write("\nStandard Deviation         ")
            for i in range(len(dataset)):
                f.write("   {0}".format(i).ljust(15))
            f.write("\n")

            for i in range(MAX_PICKS):
                if self.picks1[i] is not None and self.picks2[i] is not None and \
                        self.picks2[i].p[0] > self.picks1[i].p[0]:
                    f.write(self.picks1[i].label.format[:-1] + ":                         ")
                    for j in range(len(std[i])):
                        f.write(str(std[i][j]).ljust(15))
                    f.write("\n")

    def load_pick(self, main_widget, plot_widget):
        desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        fname = QtGui.QFileDialog.getOpenFileName(main_widget, 'Open file',
                                            desktop, "Text files (*.txt)")

        f = open(fname[0], 'r')
        f.readline()
        line = f.readline()
        while line != '' and line != '\n':
            label = line[0:2]
            dt = datetime.strptime(line[4:23], '%Y/%m/%d %H:%M:%S')
            pick = pg.InfiniteLine(angle=90, movable=False, pen=MainWindow.COLORS[self.count % MainWindow.COLORS_NUM],
                                   label=label, labelOpts={
                    'position': 0.1, 'color': MainWindow.COLORS[self.count % MainWindow.COLORS_NUM],
                    'fill': (200, 200, 200, 50), 'movable': True})
            plot_widget.addItem(pick, ignoreBounds=True)
            pick.setPos(dt.timestamp())
            self.add_pick(pick)
            line = f.readline()
