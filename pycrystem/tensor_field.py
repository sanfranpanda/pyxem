# -*- coding: utf-8 -*-
# Copyright 2017 The PyCrystEM developers
#
# This file is part of PyCrystEM.
#
# PyCrystEM is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyCrystEM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyCrystEM.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import division

from hyperspy.signals import Signal2D
import numpy as np
from scipy.linalg import polar
from hyperspy.utils import stack
import math

"""
Signal class for Tensor Fields
"""

def polar_decomposition(image, side):
    """Perform a polar decomposition of a second rank tensor and return the
    results as a numpy array.
    """
    return np.array(polar(image, side=side))

def get_rotation_angle(matrix):
    """Return the rotation angle corresponding to a

    Returns
    -------

    angle : float

    """
    return np.array(-math.asin(matrix[1,0]))

class DisplacementGradientMap(Signal2D):
    _signal_type = "tensor_field"

    def __init__(self, *args, **kwargs):
        Signal2D.__init__(self, *args, **kwargs)
        # Check that the signal dimensions are (3,3) for it to be a valid
        # TensorField

    def polar_decomposition(self):
        """Perform polar decomposition on the second rank tensors describing
        the TensorField. The polar decomposition is right handed and given by
            D = RU

        Returns
        -------

        R : TensorField
            The orthogonal matrix describing the rotation field.

        U : TensorField
            The strain tensor field.

        """
        RU = self.map(polar_decomposition,
                      side='right',
                      inplace=False)
        return RU.isig[:,:,0], RU.isig[:,:,1]

    def get_strain_maps(self):
        """Obtain strain maps from the displacement gradient tensor at each
        navigation position in the small strain approximation.

        Returns
        -------

        strain_results : BaseSignal
            Signal
        """
        R, U = self.polar_decomposition()

        e11 = -U.isig[0, 0].T + 1
        e12 = U.isig[0, 1].T
        e21 = U.isig[1, 0].T
        e22 = -U.isig[1, 1].T + 1
        theta = R.map(get_rotation_angle, inplace=False)

        strain_results = stack([e11, e22, e12, theta])

        return strain_results
