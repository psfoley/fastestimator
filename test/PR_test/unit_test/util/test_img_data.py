import unittest

import matplotlib.backends.backend_agg as plt_backend_agg
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
import torch
from matplotlib.backends.backend_agg import FigureCanvas
from PIL import Image

from fastestimator.util import ImgData


class TestImageData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch_size = 4
        cls.input_image_shape = (150, 150)
        cls.label_shape = (4, )
        cls.x_test = 0.5 * tf.ones((4, 150, 150, 3))
        cls.y_test = tf.ones(cls.label_shape)
        cls.img_data = ImgData(y=cls.y_test, x=cls.x_test)

    def test_n_cols(self):
        self.assertEqual(self.img_data._n_cols(), 2)

    def test_n_rows(self):
        self.assertEqual(self.img_data._n_rows(), 1)

    def test_shape_to_width_1d(self):
        self.assertEqual(self.img_data._shape_to_width(self.label_shape, min_width=300),
                         300,
                         'Output should be equal to minimum width')

    def test_shape_to_width_2d(self):
        self.assertEqual(self.img_data._shape_to_width(self.input_image_shape, min_width=100),
                         150,
                         'Output should be equal to input width')

    def test_shape_to_height_1d(self):
        self.assertEqual(self.img_data._shape_to_height(self.label_shape, min_height=300),
                         300,
                         'Output should be equal to minimum height')

    def test_shape_to_height_2d(self):
        self.assertEqual(self.img_data._shape_to_height(self.input_image_shape, min_height=150),
                         150,
                         'Output should be equal to input height')

    def test_img_data_widths(self):
        index = 0
        self.assertEqual(self.img_data._widths(index), [(0, 200), (250, 450)])

    def test_img_data_total_width(self):
        self.assertEqual(self.img_data._total_width(), 450)

    def test_img_data_heights(self):
        self.assertEqual(self.img_data._heights(), [(10, 810)])

    def test_img_data_total_height(self):
        self.assertEqual(self.img_data._total_height(), 840)

    def test_img_data_batch_size(self):
        self.assertEqual(self.img_data._batch_size(0), 4)

    def test_paint_figure(self):
        fig = self.img_data.paint_figure()
        canvas = FigureCanvas(fig)
        canvas.draw()
        output_test = np.array(canvas.renderer.buffer_rgba())
        img = Image.open('test_paint_fig.png')
        output = np.asarray(img)
        self.assertTrue(np.array_equal(output, output_test))

    def test_paint_numpy(self):
        output_test = self.img_data.paint_numpy()
        img = Image.open('test_paint_fig.png')
        output = np.asarray(img)
        output = np.stack([output[..., :3]])
        self.assertTrue(np.array_equal(output, output_test))


if __name__ == "__main__":
    unittest.main()
