import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore


class SettingWindow(QtGui.QWidget):
    def __init__(self, legend, plot_items, plot_widget):
        super(SettingWindow, self).__init__()
        self.setWindowTitle("Settings")

        self.main_layout = QtGui.QFormLayout()
        self.setLayout(self.main_layout)
        self.legend = legend
        self.plot_items = plot_items
        self.plot_widget = plot_widget

        self.le = []
        title_text = plot_widget.getPlotItem().titleLabel.text[35:].split('<')[0]
        self.title_le = QtGui.QLineEdit(title_text)
        self.title_le.setAlignment(QtCore.Qt.AlignCenter)
        x_text = plot_widget.getPlotItem().getAxis('bottom').labelText[15:].split('<')[0]
        self.x_le = QtGui.QLineEdit(x_text)
        self.x_le.setAlignment(QtCore.Qt.AlignCenter)
        y_text = plot_widget.getPlotItem().getAxis('left').labelText[15:].split('<')[0]
        self.y_le = QtGui.QLineEdit(y_text)
        self.y_le.setAlignment(QtCore.Qt.AlignCenter)

        self.confirm_button = QtGui.QPushButton("Confirm")
        self.confirm_button.setFixedWidth(130)
        self.cancel_button = QtGui.QPushButton("Cancel")
        self.confirm_button.clicked.connect(self.confirm_button_click)
        self.cancel_button.clicked.connect(self.cancel_button_click)

        self.generate_layout()

    def generate_layout(self):
        self.main_layout.addRow("Title", self.title_le)
        self.main_layout.addRow("X Axis", self.x_le)
        self.main_layout.addRow("Y Axis", self.y_le)
        for i in range(len(self.legend.items)):
            l = QtGui.QLabel("  Channel " + str(i+1) + "  ")
            l.setStyleSheet("background-color: " + self.legend.items[i][1].opts['color'] +";color:white;")
            le = QtGui.QLineEdit(self.legend.items[i][1].text)
            le.setAlignment(QtCore.Qt.AlignCenter)
            self.le.append(le)
            self.main_layout.addRow(l, le)
        self.main_layout.addRow(self.confirm_button, self.cancel_button)

    def confirm_button_click(self):
        self.plot_widget.setLabel('bottom', '<font size="5">' + self.x_le.text() + '</font>')
        self.plot_widget.setLabel('left', '<font size="5">' + self.y_le.text() + '</font>')
        self.plot_widget.setTitle('<font size="8"><font color="black">' + self.title_le.text() + '</font></font>')
        for i in range(len(self.legend.items)):
            text = self.le[i].text()
            self.legend.items[i][1].setText(text)
        self.close()

    def cancel_button_click(self):
        self.close()


