import sys
from gui.mainwin import MainWindow
from core.datacontainer import DataContainer
from core.controller import Controller
from PyQt5 import QtCore, QtWidgets

if __name__ == "__main__":
  app = QtWidgets.QApplication(sys.argv)
  data_container = DataContainer()
  controller = Controller(data_container)
  window = MainWindow(app, data_container, controller)
  sys.exit(app.exec_())
