# -*- coding: utf-8 -*-
"""Definition of direct vectorizer"""

import numpy as np
from .basic_vectorizer import BasicVectorizer


class DirectVectorizer(BasicVectorizer):
    """
    Class describing direct vectorizer.
    """   
    def __init__(self, norm=2):
        """
        **Input:**
        
        	norm (int): Norm of vectors used in REV analysis. The same, as parameter 'ord' in numpy.linalg.norm function, default: 2.
        """      
        super().__init__(norm)

    def vectorize(self, v1, v2):
        """
        Vectorize the vector metric values for a given pair of subsamples. 
        
        **Input:**
        
        	v1 (list(dtype = float)): data for the first subsample;
        	
        	v2 (list(dtype = float)): data for the second subsample.
        
        **Output:**
        
       		(list(dtype = float), list(dtype = float), float) - a tuple, in which the first two elements are vectorized metric values for a given pair of subsamples, the third one is the normalized distance between these vectors and the last one is the cosine similarity for them.        
        """
        n = min(len(v1), len(v2))
        v1 = v1[:n]
        v2 = v2[:n]
        delta, cos_sim = super()._compare_vectors(v1, v2)
        return v1.tolist(), v2.tolist(), delta, cos_sim
