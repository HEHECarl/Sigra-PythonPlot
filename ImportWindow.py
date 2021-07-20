from copy import deepcopy
from pyqtgraph.Qt import QtGui, QtCore


class ImportWindow(QtGui.QWidget):
    def __init__(self, main, path):
        super(ImportWindow, self).__init__()
        layout = QtGui.QGridLayout()
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setWindowTitle("Import X Type")
        self.setLayout(layout)
        self.list_widget = QtGui.QListWidget()

        self.main = main
        self.file_path = path

        self.list_widget.insertItem(0, "Datetime")
        self.continue_button = QtGui.QPushButton("Continue")
        self.continue_button.clicked.connect(self.continue_clicked)

        layout.addWidget(self.list_widget)
        layout.addWidget(self.continue_button)

    def continue_clicked(self):
        self.main.x_type = self.list_widget.currentItem().text()
        self.main.import_new_data(self.file_path)
        self.close()
