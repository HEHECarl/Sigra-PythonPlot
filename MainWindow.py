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
        self.function_buttons_layout = None
        self.zoom_button = None
        self.auto_button = None
        self.vLine = None
        self.hLine = None
        self.plot_gourp = []
        self.btn_group = []

    def init_window(self):
        self.app = QtGui.QApplication([])
        self.main_widget = QtGui.QWidget()
        self.main_widget.setGeometry(0, 0, 1000, 700)
        self.main_layout = QtGui.QGridLayout()
        self.main_widget.setLayout(self.main_layout)

        self.plot_widget = pg.PlotWidget(axisItems={'bottom': pg.DateAxisItem()})
        self.plot_widget.plotItem.setAcceptDrops(True)
        self.plot_widget.setBackground('w')
        self.plot_widget.dragEnterEvent = self.dragEnterEvent
        self.plot_widget.plotItem.dropEvent = self.dropEvent
        self.vLine = pg.InfiniteLine(angle=90, movable=False, pen="#696969")
        self.hLine = pg.InfiniteLine(angle=0, movable=False, pen="#696969")
        self.plot_widget.addItem(self.vLine, ignoreBounds=True)
        self.plot_widget.addItem(self.hLine, ignoreBounds=True)
        self.plot_widget.scene().sigMouseMoved.connect(self.mouse_moved)

        self.function_buttons_layout = QtGui.QGridLayout(self.main_widget)
        self.zoom_button = QtGui.QPushButton("Zoom", checkable=True)
        self.zoom_button.clicked.connect(self.zoom_button_click)
        self.auto_button = QtGui.QPushButton("Auto")
        self.auto_button.clicked.connect(self.auto_button_click)
        self.function_buttons_layout.addWidget(self.zoom_button, 0, 0)
        self.function_buttons_layout.addWidget(self.auto_button, 0, 1)

        self.channel_buttons_layout = QtGui.QGridLayout(self.main_widget)

        self.main_layout.addWidget(self.plot_widget, 0, 0, 3, 3)
        self.main_layout.addLayout(self.function_buttons_layout, 4, 0)
        self.main_layout.addLayout(self.channel_buttons_layout, 4, 1)

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
            self.btn_group[i].setMaximumWidth(30)
            self.btn_group[i].setMaximumHeight(30)
            self.btn_group[i].clicked.connect(partial(self.channel_button_click, i))

    def zoom_button_click(self):
        if self.zoom_button.isChecked():
            self.zoom_button.setChecked(True)
            self.plot_widget.getViewBox().setMouseMode(self.plot_widget.getViewBox().RectMode)
        else:
            self.zoom_button.setChecked(False)
            self.plot_widget.getViewBox().setMouseMode(self.plot_widget.getViewBox().PanMode)

    def auto_button_click(self):
        self.plot_widget.getViewBox().autoRange()

    def channel_button_click(self, channel):
        if self.btn_group[channel].isChecked():
            self.btn_group[channel].setChecked(True)
            self.plot_widget.addItem(self.plot_gourp[channel])
        else:
            self.btn_group[channel].setChecked(False)
            self.plot_widget.removeItem(self.plot_gourp[channel])

    def mouse_moved(self, evt):
        pos = evt
        if self.plot_widget.sceneBoundingRect().contains(pos):
            mouse_point = self.plot_widget.getViewBox().mapSceneToView(pos)
            index = int(mouse_point.x())
            self.vLine.setPos(mouse_point.x())
            self.hLine.setPos(mouse_point.y())