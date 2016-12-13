import sys
from gui.mainwin import MainWindow
from bio.brain import Brain
from core.datacontainer import DataContainer
from core.controller import Controller
from PyQt5 import QtCore, QtWidgets

if __name__ == "__main__":
  app = QtWidgets.QApplication(sys.argv)
  data_container = DataContainer()
  brain = Brain(data_container)
  controller = Controller(data_container, brain)
  window = MainWindow(app, controller)
  sys.exit(app.exec_())
