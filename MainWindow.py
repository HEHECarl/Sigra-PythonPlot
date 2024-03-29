import pyqtgraph as pg
import pyqtgraph.exporters
import time
from pyqtgraph.Qt import QtGui, QtCore
from DataProcess import DataProcessor
from functools import partial
from datetime import datetime
from Picks import Picks
from SettingWindow import SettingWindow
from ImportWindow import ImportWindow


COLORS = ['#e6194B', '#42d4f4', '#000075', '#ffe119', '#f58231', '#911eb4', '#3cb44b',
          '#f032e6', '#bfef45', '#fabed4', '#469990', '#dcbeff', '#9A6324', '#fffac8',
          '#800000', '#aaffc3', '#808000', '#ffd8b1', '#4363d8', '#a9a9a9', '#000000']

COLORS_NUM = 21


class MainWindow:
    def __init__(self):

        self.app = QtGui.QApplication([])
        self.main_widget = QtGui.QWidget()
        self.main_layout = QtGui.QGridLayout()
        self.main_widget.setLayout(self.main_layout)

        self.plot_widget = pg.PlotWidget(axisItems={'bottom': pg.DateAxisItem()})
        self.channel_group_box = QtGui.QGroupBox(self.main_widget)
        self.channel_buttons_layout = QtGui.QGridLayout(self.main_widget)
        self.function_buttons_layout = QtGui.QGridLayout(self.main_widget)
        self.legend = MyLegend((80, 60), offset=(-60, 40))
        self.legend.setLabelTextSize('10pt')
        self.legend.setParentItem(self.plot_widget.graphicsItem())

        self.zoom_button = QtGui.QPushButton("Zoom", checkable=True)
        self.auto_button = QtGui.QPushButton("Auto")
        self.save_pick_button = QtGui.QPushButton("Save Picks")
        self.load_pick_button = QtGui.QPushButton("Load Picks")
        self.graph_setting_button = QtGui.QPushButton("Graph Settings")
        self.clear_graph_button = QtGui.QPushButton("Clear")

        self.vLine = pg.InfiniteLine(angle=90, movable=False, pen="#696969")
        self.hLine = pg.InfiniteLine(angle=0, movable=False, pen="#696969")
        self.mouse_label = QtGui.QLabel("[0000/00/00 00:00:00, 0000.000]", self.main_widget)

        self.x_type = None
        self.datasets = []
        self.data_count = 0
        self.legend_count = 0
        self.width = 2

        self.plot_group = []
        self.btn_group = []

        self.file_path = ""
        self.picks = Picks()

        self.moues_X = 0
        self.moues_Y = 0

        self.setting_window = None
        self.import_window = None

    def init_window(self):
        self.main_widget.setGeometry(0, 0, 1000, 700)
        self.main_widget.setWindowTitle("Sigra Plot")
        self.mouse_label.setFixedWidth(190)

        self.plot_widget.plotItem.setAcceptDrops(True)
        self.plot_widget.setBackground('w')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.5)
        self.plot_widget.addItem(self.vLine, ignoreBounds=True)
        self.plot_widget.addItem(self.hLine, ignoreBounds=True)
        self.plot_widget.getViewBox().suggestPadding = lambda *_: 0.0
        self.plot_widget.dragEnterEvent = self.dragEnterEvent
        self.plot_widget.plotItem.dropEvent = self.dropEvent
        self.plot_widget.scene().sigMouseMoved.connect(self.mouse_moved)
        self.plot_widget.keyPressEvent = self.key_pressed
        self.plot_widget.getAxis('left').setTextPen("#000000")
        self.plot_widget.getAxis('bottom').setTextPen("#000000")
        font = QtGui.QFont()
        font.setPixelSize(20)
        self.plot_widget.getAxis("left").setTickFont(font)
        self.plot_widget.getAxis("bottom").setTickFont(font)

        self.set_x_axis("x axis")
        self.set_y_axis("y axis")
        self.plot_widget.setTitle('<font size="9"><font color="black">Title</font></font>')

        self.zoom_button.clicked.connect(self.zoom_button_click)
        self.auto_button.clicked.connect(self.auto_button_click)
        self.save_pick_button.clicked.connect(self.save_pick_button_click)
        self.load_pick_button.clicked.connect(self.load_pick_button_click)
        self.graph_setting_button.clicked.connect(self.graph_setting_button_click)
        self.clear_graph_button.clicked.connect(self.clear_graph_button_click)

        self.function_buttons_layout.addWidget(self.zoom_button, 0, 0)
        self.function_buttons_layout.addWidget(self.auto_button, 0, 1)
        self.function_buttons_layout.addWidget(self.save_pick_button, 1, 0)
        self.function_buttons_layout.addWidget(self.load_pick_button, 1, 1)
        self.function_buttons_layout.addWidget(self.graph_setting_button, 0, 2)
        self.function_buttons_layout.addWidget(self.clear_graph_button, 1, 2)
        self.channel_buttons_layout.setAlignment(QtCore.Qt.AlignLeft)

        self.main_layout.addWidget(self.plot_widget, 0, 0, 4, 4)
        self.main_layout.addWidget(self.mouse_label, 4, 0)
        self.main_layout.addLayout(self.function_buttons_layout, 4, 1)
        self.main_layout.addWidget(self.channel_group_box, 4, 2, 1, 2)

    def exec(self):
        self.main_widget.show()
        self.app.exec_()

    def generate_channel_buttons(self):
        self.btn_group.append(QtGui.QPushButton(str(self.data_count + 1), checkable=True))
        style = 'QPushButton {background-color: ' + COLORS[self.data_count % COLORS_NUM] + ';}'
        self.btn_group[self.data_count].setStyleSheet(style)
        self.channel_buttons_layout.addWidget(self.btn_group[self.data_count], self.data_count / 14,
                                              self.data_count % 14)
        self.btn_group[self.data_count].setChecked(True)
        self.btn_group[self.data_count].setMaximumWidth(30)
        self.btn_group[self.data_count].setMaximumHeight(30)
        self.btn_group[self.data_count].clicked.connect(partial(self.channel_button_click, self.data_count))
        self.channel_group_box.setLayout(self.channel_buttons_layout)

    def import_setting_file(self, path):
        file = open(path, "r")
        line = file.readline()
        title = line.split(':')[1]
        line = file.readline()
        xaxis = line.split(':')[1]
        line = file.readline()
        yaxis = line.split(':')[1]
        line = file.readline()
        channel = line.split(':')[1].strip().split()
        channel = [int(i) for i in channel]
        line = file.readline()
        legend = line.split(':')[1]
        line = file.readline()
        xrange = line.split(':')[1]
        line = file.readline()
        yrange = line.split(':')[1]

        self.set_channel_vis(channel)
        self.set_y_range(yrange.strip().split()[0], yrange.strip().split()[1])
        self.set_x_range(xrange.strip().split()[0], xrange.strip().split()[1])
        self.set_title(title)
        self.set_x_axis(xaxis.strip())
        self.set_y_axis(yaxis.strip())
        self.set_legends(legend.strip().split(','))

    def import_new_data(self, path):
        self.file_path = path
        processor = DataProcessor()
        datasets = processor.read_datetime_file(path)
        self.datasets.extend(datasets)
        count = len(datasets)
        for i in range(count):
            self.plot_group.append(self.plot_widget.plot(x=datasets[i].get_x(),
                                                         y=datasets[i].get_y(),
                                                         pen=pg.mkPen(COLORS[self.data_count % COLORS_NUM], width=self.width,
                                                                      name="Data")))
            self.legend.addItemColor(self.plot_group[self.data_count], "Data" + str(self.data_count + 1),
                                     COLORS[self.data_count % COLORS_NUM])
            self.legend_count += 1
            self.upadte_legend()
            self.generate_channel_buttons()
            self.data_count += 1

        self.plot_widget.enableAutoRange('y', False)
        self.plot_widget.enableAutoRange('x', False)

        self.app.processEvents()

    def set_title(self, title):
        state = self.plot_widget.getViewBox().state
        title = title.replace("{x_start}", datetime.fromtimestamp(state['targetRange'][0][0]).strftime('%Y/%m/%d'))
        title = title.replace("{x_end}", datetime.fromtimestamp(state['targetRange'][0][1]).strftime('%Y/%m/%d'))
        self.plot_widget.setTitle('<font size="8"><font color="black">' + title + '</font></font>')

    def set_x_axis(self, label):
        self.plot_widget.setLabel('bottom', '<font size="6">' + label + '</font>')

    def set_y_axis(self, label):
        self.plot_widget.setLabel('left', '<font size="6">' + label + '</font>')

    def set_width(self, width):
        self.width = width

    def set_legends(self, legends):
        if len(legends) > len(self.legend.items):
            print("Entered too many legends!")

        for i in range(len(legends)):
            self.legend.items[i][1].setText(legends[i])

    def show_hide_legend(self, state):
        if state:
            self.legend.setOffset((-60, 40))
        else:
            self.legend.setOffset((10000, 10000))

    def upadte_legend(self):
        self.legend.setColumnCount(int(self.legend_count / 10 + 1))
        self.legend.setGeometry(0, 0, 0, 0)

    def set_channel_vis(self, channels):
        for i in range(len(self.plot_group)):
            if i+1 not in channels:
                self.btn_group[i].setChecked(False)
                self.plot_widget.removeItem(self.plot_group[i])
                self.legend.removeItem(self.plot_group[i])
                self.legend_count -= 1
                self.upadte_legend()

    def set_y_range(self, min, max):
        self.app.processEvents()
        if min == "{y_start}" and max == "{y_end}":
            self.plot_widget.getViewBox().autoRange(padding=0)
        else:
            self.plot_widget.setYRange(int(min), int(max), padding=0)

    def set_x_range(self, min, max):
        self.app.processEvents()
        state = self.plot_widget.getViewBox().state
        if min == "{x_start}":
            min = state['targetRange'][0][0]
        else:
            min = datetime.strptime(min, '%Y/%m/%d').timestamp()

        if max == "{x_end}":
            max = state['targetRange'][0][1]
        else:
            max = datetime.strptime(max, '%Y/%m/%d').timestamp()
        self.plot_widget.setXRange(min, max, padding=0)

    def export_image(self, name):
        self.main_widget.showMaximized()
        self.app.processEvents()
        exporter = pg.exporters.ImageExporter(self.plot_widget.plotItem)
        exporter.parameters()['width'] = 1600
        exporter.parameters()['height'] = 900
        exporter.export(name)

    def dragEnterEvent(self, ev):
        ev.accept()

    def dropEvent(self, event):
        if self.x_type is None:
            self.import_window = ImportWindow(self, event.mimeData().urls()[0].toLocalFile())
            self.import_window.show()
        else:
            self.import_new_data(event.mimeData().urls()[0].toLocalFile())

    def zoom_button_click(self):
        if self.zoom_button.isChecked():
            self.zoom_button.setChecked(True)
            self.plot_widget.getViewBox().setMouseMode(self.plot_widget.getViewBox().RectMode)
        else:
            self.zoom_button.setChecked(False)
            self.plot_widget.getViewBox().setMouseMode(self.plot_widget.getViewBox().PanMode)

    def auto_button_click(self):
        self.plot_widget.getViewBox().autoRange(padding=0)

    def save_pick_button_click(self):
        self.picks.save_picks(self.datasets, self.file_path.rsplit('/', 1)[0])
        msg = QtGui.QMessageBox()
        msg.setText("Picks file has been saved to " + self.file_path.rsplit('/', 1)[0])
        msg.setWindowTitle("Save Picks File")
        msg.exec_()

    def load_pick_button_click(self):
        self.picks.load_pick(self.main_widget, self.plot_widget)

    def graph_setting_button_click(self):
        self.setting_window = SettingWindow(self.legend, self.plot_group, self.plot_widget)
        self.setting_window.show()

    def clear_graph_button_click(self):
        self.plot_widget.clear()
        for btn in self.btn_group:
            self.channel_buttons_layout.removeWidget(btn)
        self.legend.clear()

        self.datasets = []
        self.data_count = 0

        self.plot_group = []
        self.btn_group = []

        self.picks = Picks()

        self.plot_widget.enableAutoRange('y', True)
        self.plot_widget.enableAutoRange('x', True)

    def channel_button_click(self, channel):
        if self.btn_group[channel].isChecked():
            self.btn_group[channel].setChecked(True)
            self.plot_widget.addItem(self.plot_group[channel])
            self.legend.addItemColor(self.plot_group[channel], "Data" + str(channel+1), COLORS[channel % COLORS_NUM])
            self.legend_count += 1
            self.upadte_legend()
        else:
            self.btn_group[channel].setChecked(False)
            self.plot_widget.removeItem(self.plot_group[channel])
            self.legend.removeItem(self.plot_group[channel])
            self.legend_count -= 1
            self.upadte_legend()

    def mouse_moved(self, evt):
        pos = evt
        if self.plot_widget.sceneBoundingRect().contains(pos):
            mouse_point = self.plot_widget.getViewBox().mapSceneToView(pos)
            self.moues_X = mouse_point.x()
            self.moues_Y = mouse_point.y()
            try:
                self.mouse_label.setText("[{0}, {1}]".format(
                    datetime.fromtimestamp(self.moues_X).strftime('%Y/%m/%d %H:%M:%S'), round(self.moues_Y, 3)))
            except:
                self.mouse_label.setText("[0000/00/00 00:00:00, 0000.000]")

            self.vLine.setPos(self.moues_X)
            self.hLine.setPos(self.moues_Y)

    def key_pressed(self, evt):
        pick = pg.InfiniteLine(angle=90, movable=False, pen=COLORS[self.picks.count % COLORS_NUM],
                               label=chr(evt.key()) + "1",
                               labelOpts={'position': 0.1, 'color': COLORS[self.picks.count % COLORS_NUM],
                                          'fill': (200, 200, 200, 50), 'movable': True})
        result, p = self.picks.add_pick(pick)
        if result == 2:
            self.plot_widget.addItem(pick, ignoreBounds=True)
            pick.setPos(self.moues_X)
        elif result == 1:
            self.plot_widget.addItem(p, ignoreBounds=True)
            p.setPos(self.moues_X)


class MyLegend(pg.LegendItem):
    def __init__(self, size=None, offset=None, horSpacing=20, verSpacing=-5):
        pg.LegendItem.__init__(self, size, offset, horSpacing, verSpacing)

    def paint(self, p, *args):
        p.setPen(pg.mkPen(0, 0, 0))  # outline
        p.setBrush(pg.mkBrush(255, 255, 255))  # background
        p.drawRect(self.boundingRect())

    def addItemColor(self, item, name, color):
        label = pg.LabelItem(name, color=color,
                          justify='left', size=self.opts['labelTextSize'])
        if isinstance(item, self.sampleType):
            sample = item
        else:
            sample = self.sampleType(item)
        self.items.append((sample, label))
        self._addItemToLayout(sample, label)
        self.updateSize()
