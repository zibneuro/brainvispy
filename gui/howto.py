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


class HowtoCreateNeurons(InfoWindow):
  def __init__(self, parent_window):
    text = "1. Load some meshes (brain regions)<br>" + \
      "2. Select at least one brain region<br>" + \
      "3. Make sure you see inside the region<br>" + \
      "3. Click on the <b>create neuron(s)</b> button<br>"
    super().__init__(parent_window, "How to create neurons", text)


class HowtoAdjustNeuronParameters(InfoWindow):
  def __init__(self, parent_window):
    text = "1. &nbsp;&nbsp;Select a neuron (by clicking on it)<br>" + \
      "2a. Place the mouse pointer on top of a field and scroll up/down<br>" + \
      "<center>or</center><br>" + \
      "2b. Click on a field and enter a number"
    super().__init__(parent_window, "How to adjust neuron parameters", text)


class HowtoConnectNeurons(InfoWindow):
  def __init__(self, parent_window):
    text = "1. Click on a neuron (this is the source)<br>" + \
      "2. Hold the shift key and click on the target neuron<br>"
    super().__init__(parent_window, "How to connect neurons", text)


class HowtoAdjustConnectionParameters(InfoWindow):
  def __init__(self, parent_window):
    text = "1. &nbsp;&nbsp;Select a neural connection (by clicking on it)<br>" + \
      "2a. Place the mouse pointer on top of a field and scroll up/down<br>" + \
      "<center>or</center><br>" + \
      "2b. Click on a field and enter a number"
    super().__init__(parent_window, "How to adjust connection parameters", text)
