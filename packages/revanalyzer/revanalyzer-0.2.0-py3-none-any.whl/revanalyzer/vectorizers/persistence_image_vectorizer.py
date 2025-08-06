# -*- coding: utf-8 -*-
"""
Definition of Persistence Image vectorizer, used in PD vectorization. A persistence image is a 2D function computed from a persistence diagram by convolving the diagram points with a weighted Gaussian kernel. The plane is then discretized into an image with pixels, which is flattened and returned as a vector. See Adams H. et al., (2017). Persistence images: A stable vector representation of persistent homology. Journal of Machine Learning Research, 18.
"""

import numpy as np
from gudhi.representations.vector_methods import PersistenceImage
from .basic_vectorizer import BasicVectorizer


class PersistenceImageVectorizer(BasicVectorizer):
    """
    Class describing persistence image vectorizer.
    """      
    def __init__(self, resolution, bandwidth=1., norm=2):
        """
        **Input:**
        
        	resolution ([int, int]): number of bins at each axe in XY plane in vectorized persistence image function;
        	
        	bandwidth (float): bandwidth of the Gaussian kernel, default: 1;
        	 
        	norm (int): Norm of vectors used in REV analysis. The same, as parameter 'ord' in numpy.linalg.norm function, default: 2.
        """  
        super().__init__(norm)
        self.resolution = resolution
        self.bandwidth = bandwidth

    def vectorize(self, v1, v2):
        """
        Vectorize the vector metric values for a given pair of subsamples. 
        
        **Input:**
        
        	v1 (list(dtype = float)): data for the first subsample;
        	
        	v2 (list(dtype = float)): data for the second subsample.
        
        **Output:**
        
        	(list(dtype = float), list(dtype = float), float): a tuple, in which the first two elements are vectorized metric values for a given pair of subsamples, the third one is the normalized distance between these vectors and the last one is the cosine similarity for them. 
        """    
        n1 = len(v1)
        n2 = len(v2)
        C1 = PersistenceImage(bandwidth=self.bandwidth, weight=lambda x: np.arctan(0.5*(x[1] - x[0])),
                              resolution=self.resolution)
        C1.fit([v1])
        range1 = C1.im_range
        v1 = C1.transform([v1])
        v1 = v1/n1
        C2 = PersistenceImage(bandwidth=self.bandwidth, weight=lambda x: np.arctan(0.5*(x[1] - x[0])),
                              resolution=self.resolution, im_range=range1)
        C2.fit([v2])
        v2 = C2.transform([v2])
        v2 = v2/n2
        delta, cos_sim = super()._compare_vectors(v1, v2)
        return v1.tolist(), v2.tolist(), delta, cos_sim
