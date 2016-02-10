import time
from collections import deque

from PIL import ImageQt, Image
from PyQt4 import QtGui, QtCore

from morphimate import Morpher


class MorphimateWidget(QtGui.QWidget):

    def __init__(self, generator, fps=30):
        super(MorphimateWidget, self).__init__()

        self.frameGenerator = generator
        self.frames_per_sec = fps
        self.timer = QtCore.QTimer()
        self.canvas = QtGui.QLabel(self)
        self.canvas.setAlignment(QtCore.Qt.AlignHCenter)
        self.label = QtGui.QLabel(self)
        self.label.setAlignment(QtCore.Qt.AlignLeft)

        vertical_layout = QtGui.QVBoxLayout()
        vertical_layout.addStretch()
        vertical_layout.addWidget(self.label)
        vertical_layout.addWidget(self.canvas)
        vertical_layout.addStretch()

        horizontal_layout = QtGui.QHBoxLayout()
        horizontal_layout.addStretch()
        horizontal_layout.addLayout(vertical_layout)
        horizontal_layout.addStretch()

        self.setLayout(horizontal_layout)

    def start(self):
        # Make sure that generated frames are the correct size
        self.frameGenerator.resize(self.size())

        # start generating image frames in the background
        self.frameGenerator.start()

        # Create timer to render the frames as they are produced
        self.timer.timeout.connect(self.__render_frame)
        self.timer.setInterval(1000 / self.frames_per_sec)
        self.timer.start()

    def __render_frame(self):
        if len(self.frameGenerator.frames) > 1:
            img, desc = self.frameGenerator.frames.popleft()
            pixmap = QtGui.QPixmap()
            pixmap.convertFromImage(ImageQt.ImageQt(Image.fromarray(img, "RGB")))
            self.canvas.setPixmap(pixmap)
            self.label.setText(QtCore.QString(desc))
            self.label.setStyleSheet('color: white; background: black')


class FrameGenerator(QtCore.QThread):

    def __init__(self, image_supplier, morph_steps=50, tweens_per_morph=50):
        QtCore.QThread.__init__(self)

        self.frames = deque([])
        self.size = None
        self.frame_buffer_size = 200
        self.tweens_per_morph = tweens_per_morph
        self.morph_steps = morph_steps
        self.image_supplier = image_supplier

    def resize(self, size):
        self.size = size
        self.image_supplier.resize(size)

    def run(self):

        # Initialise with the first two images
        image_a, points_a, label = self.image_supplier.next_image()
        image_b, points_b, next_label = self.image_supplier.next_image()

        morpher = Morpher((image_a, points_a), (image_b, points_b), self.size.width(), self.size.height())

        # Loop forever!
        while True:
            for morph in range(1, int(self.morph_steps)):

                # If the buffer is full, then sleep for a little while
                while len(self.frames) > self.frame_buffer_size:
                    time.sleep(0.1)

                # Generate all the morphed frames for these two images
                morph_pos = morph / float(self.morph_steps)
                for tween in range(0, int(self.tweens_per_morph)):
                    tween_pos = tween / float(self.tweens_per_morph)
                    fade_pos = ((morph-1)*self.tweens_per_morph + tween) / float(self.morph_steps*self.tweens_per_morph)
                    self.frames.append((morpher.morph(morph_pos, fade_pos, tween_pos), label))

            # Progress the label text
            label = next_label

            # Get the next image to morph
            image, points, next_label = self.image_supplier.next_image()
            morpher.new_target((image, points))
        return
