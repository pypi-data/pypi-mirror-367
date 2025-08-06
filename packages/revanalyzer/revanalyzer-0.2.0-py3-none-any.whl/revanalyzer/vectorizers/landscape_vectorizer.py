# -*- coding: utf-8 -*-
"""
Definition of Landscape vectorizer, used in PD vectorization. A persistence landscape is a collection of 1D piecewise-linear functions computed from the rank function associated to the persistence diagram. These piecewise-linear functions are then sampled evenly on a given range and the corresponding vectors of samples are concatenated and returned. See Bubenik, P. (2015). Statistical topological data analysis using persistence landscapes. J. Mach. Learn. Res., 16(1), 77-102.
"""

import numpy as np
from gudhi.representations.vector_methods import Landscape
from .basic_vectorizer import BasicVectorizer


class LandscapeVectorizer(BasicVectorizer):
    """
    Class describing persistence landscape vectorizer.
    """      
    def __init__(self, resolution, num_landcapes=1, norm=2):
        """
        **Input:**
        
        	resolution (int): number of sample for all piecewise-linear functions;
        	 
        	num_landcapes (int): number of piecewise-linear functions to output, default = 1;
        	 
        	norm (int): Norm of vectors used in REV analysis. The same, as parameter 'ord' in numpy.linalg.norm function, default: 2.
        """         
        super().__init__(norm)
        self.resolution = resolution
        self.num_landscapes = num_landcapes

    def vectorize(self, v1, v2):
        """
        Vectorize the vector metric values for a given pair of subsamples. 
        
        **Input:**
        
        	v1 (list(dtype = float)): data for the first subsample;
        	
        	v2 (list(dtype = float)): data for the second subsample.
        
        **Output:**
        
        	(list(dtype = float), list(dtype = float), float): a tuple, in which the first two elements are vectorized metric values for a given pair of subsamples, the third one is the normalized distance between these vectors and the last one is the cosine similarity for them. 
        """ 
        L1 = Landscape(self.num_landscapes, self.resolution)
        L1.fit([v1])
        range1 = L1.sample_range
        v1 = L1.transform([v1])
        L2 = Landscape(self.num_landscapes,
                       self.resolution, sample_range=range1)
        L2.fit([v2])
        v2 = L2.transform([v2])
        delta, cos_sim = super()._compare_vectors(v1, v2)
        return v1.tolist(), v2.tolist(), delta, cos_sim
