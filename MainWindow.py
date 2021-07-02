from PyQt5 import QtGui, QtCore
import pyqtgraph as pg
from DataProcess import DataProcessor
from functools import partial
from datetime import datetime
from Picks import Picks


COLORS = ["#A93226", "#884EA0", "#2471A3", "#17A589", "#229954", "#D4AC0D", "#CA6F1E", "#2E4053",
          "#CB4335", "#7D3C98", "#2E86C1", "#138D75", "#28B463", "#D68910", "#BA4A00", "#273746"]


class MainWindow:
    def __init__(self):
        self.app = QtGui.QApplication([])
        self.main_widget = QtGui.QWidget()
        self.main_layout = QtGui.QGridLayout()
        self.main_widget.setLayout(self.main_layout)

        self.plot_widget = pg.PlotWidget(axisItems={'bottom': pg.DateAxisItem()})
        self.channel_group_box = QtGui.QGroupBox(self.main_widget)
        self.channel_buttons_layout = QtGui.QHBoxLayout()
        self.function_buttons_layout = QtGui.QGridLayout(self.main_widget)

        self.zoom_button = QtGui.QPushButton("Zoom", checkable=True)
        self.auto_button = QtGui.QPushButton("Auto")
        self.save_pick_button = QtGui.QPushButton("Save Picks")
        self.load_pick_button = QtGui.QPushButton("Load Picks")

        self.vLine = pg.InfiniteLine(angle=90, movable=False, pen="#696969")
        self.hLine = pg.InfiniteLine(angle=0, movable=False, pen="#696969")
        self.mouse_label = QtGui.QLabel("[0000/00/00 00:00:00, 0000.000]", self.main_widget)

        self.legend = pg.LegendItem((80, 60), offset=(70, 20))
        self.legend.setParentItem(self.plot_widget.graphicsItem())

        self.datasets = []
        self.data_count = 0

        self.plot_group = []
        self.btn_group = []

        self.picks = Picks()

        self.moues_X = 0
        self.moues_Y = 0

    def init_window(self):
        self.main_widget.setGeometry(0, 0, 1000, 700)

        self.mouse_label.setFixedWidth(190)

        self.plot_widget.plotItem.setAcceptDrops(True)
        self.plot_widget.setBackground('w')
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.addItem(self.vLine, ignoreBounds=True)
        self.plot_widget.addItem(self.hLine, ignoreBounds=True)
        self.plot_widget.dragEnterEvent = self.dragEnterEvent
        self.plot_widget.plotItem.dropEvent = self.dropEvent
        self.plot_widget.scene().sigMouseMoved.connect(self.mouse_moved)
        self.plot_widget.keyPressEvent = self.key_pressed

        self.zoom_button.clicked.connect(self.zoom_button_click)
        self.auto_button.clicked.connect(self.auto_button_click)
        self.save_pick_button.clicked.connect(self.save_pick_button_click)
        self.load_pick_button.clicked.connect(self.load_pick_button_click)

        self.function_buttons_layout.addWidget(self.zoom_button, 0, 0)
        self.function_buttons_layout.addWidget(self.auto_button, 0, 1)
        self.function_buttons_layout.addWidget(self.save_pick_button, 1, 0)
        self.function_buttons_layout.addWidget(self.load_pick_button, 1, 1)

        self.channel_buttons_layout.setAlignment(QtCore.Qt.AlignLeft)

        self.main_layout.addWidget(self.plot_widget, 0, 0, 4, 4)
        self.main_layout.addWidget(self.mouse_label, 4, 0)
        self.main_layout.addLayout(self.function_buttons_layout, 4, 1)
        self.main_layout.addWidget(self.channel_group_box, 4, 2, 1, 2)

        self.main_widget.show()
        self.app.exec_()

    def dragEnterEvent(self, ev):
        ev.accept()

    def dropEvent(self, event):
        processor = DataProcessor()
        datasets = processor.read_datetime_file(event.mimeData().urls()[0].toLocalFile())
        self.datasets.extend(datasets)
        count = len(datasets)
        for i in range(count):
            self.plot_group.append(self.plot_widget.plot(x=datasets[i].get_x(),
                                                         y=datasets[i].get_y(),
                                                         pen=pg.mkPen(COLORS[self.data_count % 8], width=1)))
            self.generate_channel_buttons()
            self.data_count += 1

    def generate_channel_buttons(self):
        self.btn_group.append(QtGui.QPushButton(str(self.data_count + 1), checkable=True))
        style = 'QPushButton {background-color: ' + COLORS[self.data_count % 8] + ';}'
        self.btn_group[self.data_count].setStyleSheet(style)
        self.channel_buttons_layout.addWidget(self.btn_group[self.data_count])
        self.btn_group[self.data_count].setChecked(True)
        self.btn_group[self.data_count].setMaximumWidth(30)
        self.btn_group[self.data_count].setMaximumHeight(30)
        self.btn_group[self.data_count].clicked.connect(partial(self.channel_button_click, self.data_count))
        self.channel_group_box.setLayout(self.channel_buttons_layout)

    def zoom_button_click(self):
        if self.zoom_button.isChecked():
            self.zoom_button.setChecked(True)
            self.plot_widget.getViewBox().setMouseMode(self.plot_widget.getViewBox().RectMode)
        else:
            self.zoom_button.setChecked(False)
            self.plot_widget.getViewBox().setMouseMode(self.plot_widget.getViewBox().PanMode)

    def auto_button_click(self):
        self.plot_widget.getViewBox().autoRange()

    def save_pick_button_click(self):
        self.picks.save_picks(self.datasets)
        msg = QtGui.QMessageBox()
        msg.setText("Picks file has been saved to the desktop")
        msg.setWindowTitle("Save Picks File")
        msg.exec_()

    def load_pick_button_click(self):
        self.picks.load_pick(self.main_widget, self.plot_widget)

    def channel_button_click(self, channel):
        if self.btn_group[channel].isChecked():
            self.btn_group[channel].setChecked(True)
            self.plot_widget.addItem(self.plot_group[channel])
        else:
            self.btn_group[channel].setChecked(False)
            self.plot_widget.removeItem(self.plot_group[channel])

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
        pick = pg.InfiniteLine(angle=90, movable=False, pen=COLORS[self.picks.count % 8], label=chr(evt.key()) + "1",
                               labelOpts={'position': 0.1, 'color': COLORS[self.picks.count % 8],
                                          'fill': (200, 200, 200, 50), 'movable': True})
        result, p = self.picks.add_pick(pick)
        if result == 2:
            self.plot_widget.addItem(pick, ignoreBounds=True)
            pick.setPos(self.moues_X)
        elif result == 1:
            self.plot_widget.addItem(p, ignoreBounds=True)
            p.setPos(self.moues_X)
