from PyQt5 import QtGui
import pyqtgraph as pg
from DataProcess import DataProcessor
from functools import partial

COLORS = ["#DC143C", "#7CFC00", "#1E90FF", "#FF1493", "#FFD700", "#7B68EE", "#00CED1", "#808000"]

class MainWindow:
    def __init__(self):
        self.app = None
        self.main_widget = None
        self.main_layout = None
        self.plot_widget = None
        self.channel_buttons_layout = None
        self.plot_gourp = []
        self.btn_group = []

    def init_window(self):
        self.app = QtGui.QApplication([])
        self.main_widget = QtGui.QWidget()
        self.main_layout = QtGui.QGridLayout()
        self.main_widget.setLayout(self.main_layout)

        self.plot_widget = pg.PlotWidget(axisItems={'bottom': pg.DateAxisItem()})
        self.plot_widget.plotItem.setAcceptDrops(True)
        self.plot_widget.setBackground('w')
        self.plot_widget.dragEnterEvent = self.dragEnterEvent
        self.plot_widget.plotItem.dropEvent = self.dropEvent

        self.channel_buttons_layout = QtGui.QGridLayout(self.main_widget)
        self.main_layout.addWidget(self.plot_widget, 0, 0, 3, 3)
        self.main_layout.addLayout(self.channel_buttons_layout, 4, 0)

    def exec_app(self):
        self.main_widget.show()
        self.app.exec_()

    def dragEnterEvent(self, ev):
        ev.accept()

    def dropEvent(self, event):
        processor = DataProcessor()
        datasets = processor.read_datetime_file(event.mimeData().urls()[0].toLocalFile())
        count = len(datasets)
        for i in range(count):
            self.plot_gourp.append(self.plot_widget.plot(x=[x.timestamp() for x in datasets[i].get_x()],
                                                         y=datasets[i].get_y(), pen=pg.mkPen(COLORS[i % 8], width=1)))
        self.generate_channel_buttons(count)

    def generate_channel_buttons(self, count):
        for i in range(count):
            self.btn_group.append(QtGui.QPushButton(str(i), checkable=True))
            self.channel_buttons_layout.addWidget(self.btn_group[i], 0, i)
            self.btn_group[i].setChecked(True)
            self.btn_group[i].clicked.connect(partial(self.channel_button_click, i))

    def channel_button_click(self, channel):
        if self.btn_group[channel].isChecked():
            self.btn_group[channel].setChecked(True)
            self.plot_widget.addItem(self.plot_gourp[channel])
        else:
            self.btn_group[channel].setChecked(False)
            self.plot_widget.removeItem(self.plot_gourp[channel])