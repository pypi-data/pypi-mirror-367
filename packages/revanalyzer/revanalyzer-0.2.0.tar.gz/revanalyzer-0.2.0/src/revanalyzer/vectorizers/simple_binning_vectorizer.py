# -*- coding: utf-8 -*-
"""Definition of Simple Binning vectorizer, used in PD vectorization."""

import numpy as np
from .basic_vectorizer import BasicVectorizer


class SimpleBinningVectorizer(BasicVectorizer):
    """
    Class describing simple binning vectorizer.
    """  
    def __init__(self, bins, skip_zeros=True, norm=2):
        """
        **Input:**
        
        	bins (int): number of bins at each axe in XY plane;
        
        	skip_zeros (bool): If True, bins of 2D histogram empty for both compared PDs are not included into the final vectors, default: True;
        	
        	norm (int): Norm of vectors used in REV analysis. The same, as parameter 'ord' in numpy.linalg.norm function, default: 2.
        """         
        super().__init__(norm)
        self.bins = bins
        self.skip_zeros = skip_zeros

    def vectorize(self, v1, v2):
        """
        Vectorize the vector metric values for a given pair of subsamples. 
        
        **Input:**
        
        	v1 (list(dtype = float)): data for the first subsample;
        	
        	v2 (list(dtype = float)): data for the second subsample.
        
        **Output:**
        
        	(list(dtype = float), list(dtype = float), float): a tuple, in which the first two elements are vectorized metric values for a given pair of subsamples, the third one is the normalized distance between these vectors and the last one is the cosine similarity for them. 
        """        
        r1 = _range_pd(v1)
        v1 = _hist_pd(v1, self.bins, r1)
        v2 = _hist_pd(v2, self.bins, r1)
        if self.skip_zeros:
            v12 = _skip_zeros12(v1, v2)
            v1 = v12[0]
            v2 = v12[1]
        delta, cos_sim = super()._compare_vectors(v1, v2)
        return v1, v2, delta, cos_sim


def _hist_pd(v, bins, r):
    v = [i for i in zip(*v)]
    b = np.array(v[0])
    d = np.array(v[1])
    d = d - b
    hist = np.histogram2d(b, d, bins=bins, range=r)
    norm = len(b)
    return np.ravel(hist[0])/norm


def _range_pd(v):
    v = [i for i in zip(*v)]
    b = np.array(v[0])
    d = np.array(v[1])
    d = np.array(d) - np.array(b)
    xmin = min(b)
    xmax = max(b)
    ymin = min(d)
    ymax = max(d)
    r = [[xmin, xmax], [ymin, ymax]]
    return r


def _skip_zeros12(v1, v2):
    v1_new = []
    v2_new = []
    zeroes_ids = []
    for count, elem in enumerate(zip(v1, v2)):
        if (elem[0] > 0 or elem[1] > 0):
            v1_new.append(elem[0])
            v2_new.append(elem[1])
        else:
            zeroes_ids.append(count)
    return (v1_new, v2_new, zeroes_ids)
