# -*- coding: utf-8 -*-
"""
Definition of Silhouette vectorizer, used in PD vectorization. A persistence silhouette is computed by taking a weighted average of the collection of 1D piecewise-linear functions given by the persistence landscapes, and then by evenly sampling this average on a given range. Finally, the corresponding vector of samples is returned. See Chazal, F., et al. (2014). Stochastic convergence of persistence landscapes and silhouettes. In Proceedings of the thirtieth annual symposium on Computational geometry (pp. 474-483).
"""

import numpy as np
from gudhi.representations.vector_methods import Silhouette
from .basic_vectorizer import BasicVectorizer


class SilhouetteVectorizer(BasicVectorizer):
    """
    Class describing persistence silhouette vectorizer.
    """   
    def __init__(self, resolution, n=1, norm=2):
        """
        **Input:**
        
        	resolution (int): number of samples for the weighted average;
        	
        	n (int): power parameter in weighted funtion (d-b)^n, default = 1;
        	 
        	norm (int): Norm of vectors used in REV analysis. The same, as parameter 'ord' in numpy.linalg.norm function, default: 2.
        """ 
        super().__init__(norm)
        self.resolution = resolution
        self.n = n

    def vectorize(self, v1, v2):
        """
        Vectorize the vector metric values for a given pair of subsamples. 
        
        **Input:**
        
        	v1 (list(dtype = float)): data for the first subsample;
        	
        	v2 (list(dtype = float)): data for the second subsample.
        
        **Output:**
        
        	(list(dtype = float), list(dtype = float), float): a tuple, in which the first two elements are vectorized metric values for a given pair of subsamples, the third one is the normalized distance between these vectors and the last one is the cosine similarity for them. 
        """ 
        S1 = Silhouette(weight=lambda x: (
            x[1] - x[0])**self.n, resolution=self.resolution)
        S1.fit([v1])
        range1 = S1.sample_range
        v1 = S1.transform([v1])
        S2 = Silhouette(weight=lambda x: (
            x[1] - x[0])**self.n, resolution=self.resolution,  sample_range=range1)
        S2.fit([v2])
        v2 = S2.transform([v2])
        delta, cos_sim = super()._compare_vectors(v1, v2)
        return v1.tolist(), v2.tolist(), delta, cos_sim
