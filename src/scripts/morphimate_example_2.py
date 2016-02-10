#!/usr/bin/python2.7
#
# Face Morphing Example
#
# Creates an animation showing morphs between different face images.
#

import sys
import pkg_resources

from PyQt4 import QtGui, QtCore

from morphimate import MorphimateWidget, FrameGenerator, LabelledImageSupplier

size = QtCore.QSize(400, 400)

app = QtGui.QApplication(sys.argv)

image_dir = pkg_resources.resource_filename('morphimate', 'resources/images')

morph_widget = MorphimateWidget(FrameGenerator(LabelledImageSupplier(image_dir), morph_steps=50, tweens_per_morph=30), fps=20)

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
