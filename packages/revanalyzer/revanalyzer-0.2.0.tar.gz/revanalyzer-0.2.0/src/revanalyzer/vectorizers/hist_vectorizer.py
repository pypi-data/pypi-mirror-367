# -*- coding: utf-8 -*-
"""Definition of histogram vectorizer"""

import numpy as np
from .basic_vectorizer import BasicVectorizer


class HistVectorizer(BasicVectorizer):
    """
    Class describing vectorizer for histogram-like data.
    """     
    def __init__(self, factor=1, norm=2):
        """
        **Input:**
        
        	factor (int): Defines how many bins are in linear size of one voxel, default: 1;
        	
        	norm (int): Norm of vectors used in REV analysis. The same, as parameter 'ord' in numpy.linalg.norm function, default: 2.
        """      
        super().__init__(norm)
        self.factor = factor

    def vectorize(self, v1, v2):
        """
        Vectorize the vector metric values for a given pair of subsamples. 
        
        **Input:**
        
        	v1 (list(dtype = float)): data for the first subsample;
        	
        	v2 (list(dtype = float)): data for the second subsample.
        
        **Output:**
        
        	(list(dtype = float), list(dtype = float), float) - a tuple, in which the first two elements are vectorized metric values for a given pair of subsamples, the third one is the normalized distance between these vectors and the last one is the cosine similarity for them. 
        """
        rmax1 = np.ceil(max(v1))
        r1 = [0, rmax1]
        bins = int(self.factor*rmax1)
        hist1, bin_edges1 = np.histogram(v1, bins=bins, range=r1, density=True)
        hist2, bin_edges2 = np.histogram(v2, bins=bins, range=r1, density=True)
        delta, cos_sim = super()._compare_vectors(hist1, hist2)
        return hist1.tolist(), hist2.tolist(), delta, cos_sim
