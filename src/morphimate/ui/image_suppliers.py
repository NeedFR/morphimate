from __future__ import division
from copy import copy
from os import walk, path

import numpy as np
import scipy.ndimage
from scipy.misc import imresize


class ImageSupplier:
    """
    This is an abstract class. Use one of the specialisations below for an actual image supplier
    """
    def __init__(self):
        self.size = None

    def resize(self, size):
        self.size = size

    def next_image(self):
        return None


class RandomSupplier(ImageSupplier):
    """
    Provide random colourful stripey images.
    Provides "pretty" images for testing, but not useful for much else.
    """
    def next_image(self):

        # Random control points
        points = np.vstack((np.random.randint(0, self.size.width()-1, 50), np.random.randint(0, self.size.height()-1, 50))).T

        # Random image
        img = np.empty(0)
        for i in range(0, 10):
            rgb = np.random.randint(0, 256, 3)
            tmp = np.tile(rgb, self.size.width() * self.size.height() / 10)
            img = np.hstack([img, tmp])

        img = np.reshape(img, [self.size.height(), self.size.width(), 3])

        description = 'Random image examples'
        return img, points, description


class LabelledImageSupplier(ImageSupplier):
    """
    Supplies images that have been labelled with control points and a descriptive text.
    The images are loaded from the supplied file-system path. Sub-directories are searched,
    and the following files are looked for:

    image.jpg = the image
    points.txt = the control points, provided as x, y coordinates, one per line
    description.txt = a short descriptive label for the image

    Note: all images are expected to have the same number of control points, and they should
    be listed in the same order. Control points for face images (for example) could be generated using
    Stasm (http://www.milbo.users.sonic.net/stasm/index.html) or similar software.
    """
    def __init__(self, image_path):
        ImageSupplier.__init__(self)

        self.counter = 0
        self.images = []

        # Search for images
        for subdir, dirs, _ in walk(image_path):
            for dir in dirs:
                # Get the image (if one exists)
                if path.exists(path.join(subdir, dir, 'image.jpg')):
                    image = path.join(subdir, dir, 'image.jpg')
                else:
                    continue

                # Get the control points for the image
                if path.exists(path.join(subdir, dir, 'points.txt')):
                    f = open(path.join(subdir, dir, 'points.txt'), 'r')
                    points = [control_point.split(' ') for control_point in f.read().strip().split('\n')]
                    points = np.array(points).astype('int')
                    f.close()
                else:
                    continue

                # Get the description text
                if path.exists(path.join(subdir, dir, 'description.txt')):
                    f = open(path.join(subdir, dir, 'description.txt'), 'r')
                    description = f.read()
                    f.close()
                else:
                    description = ''

                self.images.append((image, points, description))

    def next_image(self):
        image, points, description = self.images[self.counter]
        image = scipy.ndimage.imread(image)[..., :3]

        self.counter += 1
        self.counter %= len(self.images)

        scaled_image, scaled_points = self.__scale_image(image, points, self.size)

        return scaled_image, scaled_points, description

    @staticmethod
    def __scale_image(image, points, size):
        """
        Scales the image (and control points) to match the required display size.
        """
        # Bounding box
        x_min, y_min = np.min(points, axis=0)
        x_max, y_max = np.max(points, axis=0)
        w = x_max - x_min
        h = y_max - y_min

        # Pad bounding box by 20% on all sides
        x_padding = 0.4*w
        x_min -= x_padding / 2
        x_max += x_padding / 2
        w = x_max - x_min

        y_padding = 0.4*h
        y_min -= y_padding / 2
        y_max += y_padding / 2
        h = y_max - y_min

        # Add extra padding to the bounding box to maintain required aspect-ratio
        aspect_ratio = size.width() / size.height()
        bounding_ratio = w / h
        if bounding_ratio < aspect_ratio:
            padding = aspect_ratio * h - w
            x_min -= padding / 2
            x_max += padding / 2
        elif bounding_ratio > aspect_ratio:
            padding = w / aspect_ratio - h
            y_min -= padding / 2
            y_max += padding / 2
            h = y_max - y_min

        # Scale
        scale = size.height() / h
        scaled = imresize(image, scale)

        # Crop
        cropped = scaled[y_min * scale:y_max * scale, x_min * scale:x_max * scale]

        # Apply the same transformation to the control points
        transformed_points = copy(points)
        transformed_points[:, 0] = (points[:, 0] - x_min) * scale
        transformed_points[:, 1] = (points[:, 1] - y_min) * scale

        # Add corner co-ordinates so that the entire rectangle is morphed
        transformed_points = np.vstack([transformed_points, [[0, 0], [0, size.height()-1], [size.width()-1, 0], [size.width()-1, size.height()-1]]])

        return cropped, transformed_points