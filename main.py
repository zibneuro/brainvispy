import sys
from gui.mainwin import MainWindow
from PyQt5 import QtCore, QtWidgets

if __name__ == "__main__":
  app = QtWidgets.QApplication(sys.argv)
  window = MainWindow(app)
  sys.exit(app.exec_())
