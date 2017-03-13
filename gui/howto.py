from PyQt5 import QtWidgets, QtCore

class InfoWindow(QtWidgets.QDialog):
  def __init__(self, parent_window, title, info):
    super().__init__(parent_window, QtCore.Qt.WindowStaysOnTopHint)
    self.setWindowTitle(title)
    self.setModal(False)
    # The info
    label_info = QtWidgets.QLabel(info)
    label_info.setTextFormat(QtCore.Qt.RichText)
    # The OK button
    ok_btn = QtWidgets.QPushButton("OK")
    ok_btn.setFixedSize(QtCore.QSize(80, 30))
    ok_btn.clicked.connect(self.close)
    # The layout
    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(label_info)
    layout.addWidget(ok_btn)
    layout.setAlignment(ok_btn, QtCore.Qt.AlignHCenter)
    self.setLayout(layout)


class HowtoGetStarted(InfoWindow):
  def __init__(self, parent_window):
    text = "Load some meshes (brain regions)<br>"
    super().__init__(parent_window, "How to get started", text)


class HowtoCreateNeuralNetwork(InfoWindow):
  def __init__(self, parent_window):
    text = "1. Load some meshes (brain regions)<br>" + \
      "2. Import a connectivity matrix<br>"
    super().__init__(parent_window, "How to create a neural network", text)
