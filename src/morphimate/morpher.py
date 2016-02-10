from copy import copy
import numpy as np
from scipy.spatial import Delaunay
from scipy.interpolate import RectBivariateSpline


class Morpher:
    """
    Morphs between two images.
    This is generally intended to produce animations, and the "tween" functionality may not work
    entirely as expected if morph images are not generated in sequence. Using the default
    tween value of 1.0 should avoid any weirdness (I hope).
    """

    def __init__(self, source=None, target=None, width=500, height=600):
        # Output image size
        self.size = (height, width)

        # The image and control-points
        self.source = dict()
        self.target = dict()
        self.source['image'], self.source['points'] = source
        self.target['image'], self.target['points'] = target

        # Interpolation functions
        self.source['interp_red'] = RectBivariateSpline(range(0, self.source['image'].shape[0]), range(0, self.source['image'].shape[1]), self.source['image'][:, :, 0])
        self.source['interp_green'] = RectBivariateSpline(range(0, self.source['image'].shape[0]), range(0, self.source['image'].shape[1]), self.source['image'][:, :, 1])
        self.source['interp_blue'] = RectBivariateSpline(range(0, self.source['image'].shape[0]), range(0, self.source['image'].shape[1]), self.source['image'][:, :, 2])
        self.target['interp_red'] = RectBivariateSpline(range(0, self.target['image'].shape[0]), range(0, self.target['image'].shape[1]), self.target['image'][:, :, 0])
        self.target['interp_green'] = RectBivariateSpline(range(0, self.target['image'].shape[0]), range(0, self.target['image'].shape[1]), self.target['image'][:, :, 1])
        self.target['interp_blue'] = RectBivariateSpline(range(0, self.target['image'].shape[0]), range(0, self.target['image'].shape[1]), self.target['image'][:, :, 2])

        # Warp both images to be aligned with the source in preparation for the first morph
        self.source['warped'] = self.__warp(self.source, self.source['points'], self.size)
        self.target['warped'] = self.__warp(self.target, self.source['points'], self.size)

        self.source['last_warped'] = self.source['warped']
        self.target['last_warped'] = self.target['warped']

        self.source['tweened'] = self.source['warped']
        self.target['tweened'] = self.target['warped']

        self.morph_percent = None
        self.tween_percent = None

    def new_target(self, target):
        """
        Change the target image for the morph, and make the old target the source
        """
        self.source = copy(self.target)
        self.target['image'], self.target['points'] = target
        self.target['interp_red'] = RectBivariateSpline(range(0, self.target['image'].shape[0]), range(0, self.target['image'].shape[1]), self.target['image'][:, :, 0])
        self.target['interp_green'] = RectBivariateSpline(range(0, self.target['image'].shape[0]), range(0, self.target['image'].shape[1]), self.target['image'][:, :, 1])
        self.target['interp_blue'] = RectBivariateSpline(range(0, self.target['image'].shape[0]), range(0, self.target['image'].shape[1]), self.target['image'][:, :, 2])

    def morph(self, morph_percent, blend_percent, tween_percent=1):
        """
        Produce a morphed image
        :param morph_percent: the morph "distance" between the two images
        :param blend_percent: the amount to blend the source and target images
        :param tween_percent: the tween "distance" between the two most recent morphs
        :return:
        """
        if self.morph_percent != morph_percent:
            self.morph_percent = morph_percent
            self.tween_percent = None

            # Get the way-points for this frame
            way_points = self.__way_points(morph_percent)

            # Remember previous warped images
            self.source['last_warped'] = self.source['warped']
            self.target['last_warped'] = self.target['warped']

            # Warp both images to these way-points
            self.source['warped'] = self.__warp(self.source, way_points, self.size)
            self.target['warped'] = self.__warp(self.target, way_points, self.size)

        if self.tween_percent != tween_percent:

            self.tween_percent = tween_percent
            self.__tween()

        return self.__blend(blend_percent)

    def __way_points(self, percent):
        if percent <= 0:
            return self.source['points']
        elif percent >= 1:
            return self.target['points']
        else:
            return np.asarray(self.target['points'] * percent + self.source['points'] * (1 - percent), np.int32)

    def __tween(self):
        """
        Generate "tween" images (i.e. between two morph steps) by creating a weighted average between two morphs.
        """
        if self.tween_percent <= 0:
            self.source['tweened'] = self.source['last_warped']
            self.tween_target_warped = self.target['last_warped']
        elif self.tween_percent >= 1:
            self.source['tweened'] = self.source['warped']
            self.target['tweened'] = self.target['warped']
        else:
            self.source['tweened'] = np.clip(self.source['warped'] * self.tween_percent + self.source['last_warped'] * (1 - self.tween_percent), 0, 255).astype('uint8')
            self.target['tweened'] = np.clip(self.target['warped'] * self.tween_percent + self.target['last_warped'] * (1 - self.tween_percent), 0, 255).astype('uint8')

    def __blend(self, percent):
        """
        Blend the two tween images for the source and target to produce the final output image
        """
        if percent <= 0:
            return self.source['tweened']
        elif percent >= 1:
            return self.target['tweened']
        else:
            return np.clip(self.source['tweened'] * (1-percent) + self.target['tweened'] * percent, 0, 255).astype('uint8')

    @staticmethod
    def __warp(image, points, size):
        """
        Warp an image using the provided point locations.
        """
        rows, cols = size[:2]

        # perform triangulation on the control points
        delaunay = Delaunay(points)
        triangles = delaunay.simplices

        output = np.zeros((rows, cols, 3), np.uint8)
        grid = np.vstack(np.unravel_index(xrange(0, rows*cols), size)).T
        membership = delaunay.find_simplex(grid)

        for triangle_id in range(len(triangles)):

            triangle = triangles[triangle_id]

            # Transformation matrix from output triangle to source triangle
            src = np.vstack((image['points'][triangle, :].T, [1, 1, 1]))
            dst = np.vstack((points[triangle, :].T, [1, 1, 1]))
            mat = np.dot(src, np.linalg.inv(dst))[:2, :]

            # Co-ordinates into output image
            x, y = grid[membership == triangle_id].T

            # Co-ordinates into source image
            a, b = np.dot(mat, np.vstack((x, y, np.ones(len(x)))))

            # Interpolate from source image to fill in the output image values
            output[y, x, 0] = np.clip(image['interp_red'](b, a, grid=False), 0, 255)
            output[y, x, 1] = np.clip(image['interp_green'](b, a, grid=False), 0, 255)
            output[y, x, 2] = np.clip(image['interp_blue'](b, a, grid=False), 0, 255)

        delaunay.close()

        return output
