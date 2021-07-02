from PyQt5 import QtGui
import pyqtgraph as pg
from DataProcess import DataProcessor, DataSet
from MainWindow import MainWindow


def init_window():
    app = QtGui.QApplication([])
    main_widget = QtGui.QWidget()
    plot_widget = pg.PlotWidget(axisItems={'bottom': pg.DateAxisItem()})
    main_layout = QtGui.QGridLayout()
    main_widget.setLayout(main_layout)

    def dragEnterEvent(ev):
        ev.accept()

    plot_widget.setBackground('w')
    plot_widget.dragEnterEvent = dragEnterEvent
    main_layout.addWidget(plot_widget, 0, 0, 3, 3)

    plot_widget.plotItem.setAcceptDrops(True)

    def dropEvent(event):
        processor = DataProcessor()
        datasets = processor.read_datetime_file(event.mimeData().urls()[0].toLocalFile())
        x = plot_widget.plot(x=[x.timestamp() for x in datasets[0].get_x()], y=datasets[0].get_y(), pen=pg.mkPen("r", width=1))
        y = plot_widget.plot(x=[x.timestamp() for x in datasets[2].get_x()], y=datasets[2].get_y(), pen=pg.mkPen("g", width=1))
        x = plot_widget.removeItem(x)
        print(x)
    plot_widget.plotItem.dropEvent = dropEvent

    main_widget.show()
    app.exec_()


if __name__ == '__main__':
    main_window = MainWindow()
    main_window.init_window()
    #pyqtgraph.examples.run()

