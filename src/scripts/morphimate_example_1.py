#!/usr/bin/python2.7
#
# Random Image Example
#
# Creates an animation window showing randomly generated image morphs.
#

import sys
from PyQt4 import QtGui, QtCore

from morphimate import MorphimateWidget, FrameGenerator, RandomSupplier

size = QtCore.QSize(400, 400)

app = QtGui.QApplication(sys.argv)

morph_widget = MorphimateWidget(FrameGenerator(RandomSupplier(), morph_steps=30, tweens_per_morph=30), fps=10)

main_window = QtGui.QMainWindow()
main_window.setCentralWidget(morph_widget)
main_window.setMinimumSize(size)

palette = main_window.palette()
palette.setColor(main_window.backgroundRole(), QtCore.Qt.black)
main_window.setPalette(palette)

main_window.show()
main_window.raise_()

morph_widget.start()

sys.exit(app.exec_())
