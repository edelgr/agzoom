"""Utilities for real-time data augmentation on image data.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from keras_preprocessing import get_keras_submodule
import tensorflow as tf
import numpy as np
import math

try:
    IteratorType = get_keras_submodule('utils').Sequence
except ImportError:
    IteratorType = object


class PatchesImageIterator(IteratorType):
    """Take and images and divide it in patches & generates batches.
           # Arguments
               image: nump array de la image
               target_size: Tuple of integers `(height, width)`,
                   default: `(7, 7)`.
                   The dimensions to which all images found will be resized.
               window_size: Size of patches
               batch_size: Size of the batches of data (default: 32).

           # Returns
               A `PatchesIterator` yielding 'x'
                   where `x` is a NumPy array containing a batch
                   of patches from image with shape `(batch_size, *target_size, channels)`

        batch_size: Integer, size of a batch.
        dtype: Dtype to use for generated arrays.
    """

    def __new__(cls, *args, **kwargs):
        try:
            from tensorflow.keras.utils import Sequence as TFSequence
            if TFSequence not in cls.__bases__:
                cls.__bases__ = cls.__bases__ + (TFSequence,)
        except ImportError:
            pass
        return super(PatchesImageIterator, cls).__new__(cls)

    def __init__(self, image, target_size=(7, 7, 14), window_size=7, batch_size=32, dtype='float32'):
        self.window_size = window_size
        self.target_size = target_size
        self.image = image
        self.dtype = dtype
        self.n = np.shape(self.image)[0] * np.shape(self.image)[1]
        self.batch_size = batch_size
        self.batch_index = 0
        self.total_batches_seen = 0
        self.index_array = None

        super(PatchesImageIterator, self).__init__()

    def reset(self):
        self.batch_index = 0

    def __len__(self):
        return math.ceil(self.n / self.batch_size)

    def _set_index_array(self):
        self.index_array = np.arange(self.n)

    def __getitem__(self, idx):
        if idx >= len(self):
            raise ValueError('Asked to retrieve element {idx}, '
                             'but the Sequence '
                             'has length {length}'.format(idx=idx, length=len(self)))
        self.total_batches_seen += 1
        if self.index_array is None:
            self._set_index_array()

        index_array = self.index_array[self.batch_size * idx: self.batch_size * (idx + 1)]
        return self._get_batches_of_transformed_samples(index_array)

    def _get_batches_of_transformed_samples(self, index_array):
        """Gets a batch of samples.

        # Arguments
            index_array: Array of sample indices to include in batch.

        # Returns
            A batch of  samples.
        """
        batch = np.zeros((len(index_array),) + self.target_size, dtype=self.dtype)
        offset = self.window_size // 2
        shape = np.shape(self.image)

        for i, index in enumerate(index_array):
            py = index // shape[1]
            px = index % shape[1]
            if offset <= px <= shape[1] - offset and offset <= py <= shape[0] - offset:
                patch_image = self.image[py - offset:py + offset + 1, px - offset:px + offset + 1]
                patch_image = tf.image.resize(patch_image, (self.target_size[0], self.target_size[1]))
                batch[i, :, :, :] = patch_image[:, :, :]
        return batch
