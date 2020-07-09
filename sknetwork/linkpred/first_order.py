#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May, 2020
@author: Nathan de Lara <ndelara@enst.fr>
"""
from abc import ABC
from typing import Union, Iterable

import numpy as np
from scipy import sparse

from sknetwork.linkpred.base import BaseLinkPred
from sknetwork.linkpred.first_order_core import n_common_neigh
from sknetwork.utils.check import check_format


class FirstOrder(BaseLinkPred, ABC):
    """Base class for first order algorithms."""
    def __init__(self):
        super(FirstOrder, self).__init__()
        self.indptr_ = None
        self.indices_ = None

    def fit(self, adjacency: Union[sparse.csr_matrix, np.ndarray]):
        """Fit algorithm to the data.

        Parameters
        ----------
        adjacency :
            Adjacency matrix of the graph

        Returns
        -------
        self : :class:`FirstOrder`
        """
        adjacency = check_format(adjacency)
        adjacency.sort_indices()
        self.indptr_ = adjacency.indptr.astype(np.int32)
        self.indices_ = adjacency.indices.astype(np.int32)

        return self

    def _predict_node(self, source: int):
        """Prediction for a single edge."""
        n = self.indptr_.shape[0] - 1
        return self._predict_base(source, np.arange(n))


class CommonNeighbors(FirstOrder):
    """Link prediction by common neighbors:

    :math:`s(i, j) = |\\Gamma_i \\cap \\Gamma_j|`.

    Attributes
    ----------
    indptr_ : np.ndarray
        Pointer index for neighbors.
    indices_ : np.ndarray
        Concatenation of neighbors.

    Examples
    --------
    >>> from sknetwork.data import house
    >>> adjacency = house()
    >>> cn = CommonNeighbors()
    >>> similarities = cn.fit_predict(adjacency, 0)
    >>> similarities
    array([2, 1, 1, 1, 1])
    >>> similarities = cn.predict([0, 1])
    >>> similarities
    array([[2, 1, 1, 1, 1],
           [1, 3, 0, 2, 1]])
    >>> similarities = cn.predict((0, 1))
    >>> similarities
    1
    >>> similarities = cn.predict([(0, 1), (1, 2)])
    >>> similarities
    array([1, 0])
    """
    def __init__(self):
        super(CommonNeighbors, self).__init__()

    def _predict_base(self, source: int, targets: Iterable):
        """Prediction for a single node."""
        return np.asarray(n_common_neigh(self.indptr_, self.indices_, np.int32(source),
                                         np.array(targets, dtype=np.int32)))
