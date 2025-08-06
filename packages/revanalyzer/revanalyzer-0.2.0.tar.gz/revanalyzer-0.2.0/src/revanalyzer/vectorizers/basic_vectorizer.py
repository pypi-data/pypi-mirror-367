# -*- coding: utf-8 -*-
"""Definition of basic vectorizer"""

import numpy as np 

class BasicVectorizer:
    """
    Base class for vectorizers. (Don't use it directly but derive from it).
    """
    def __init__(self, norm):
        """
        **Input:**
        
        	norm (int): Norm of vectors used in REV analysis. The same, as parameter 'ord' in numpy.linalg.norm function.
        """
        self.norm = norm
    def _compare_vectors(self, v1, v2):
        if len(v1)!= len(v2):
            raise ValueError("Compared vectors should have equal sizes.")
        n1 = np.linalg.norm(np.array(v1), ord=self.norm)
        n2 = np.linalg.norm(np.array(v2), ord=self.norm)
        delta = 2*np.linalg.norm(np.array(v1) - np.array(v2), ord=self.norm)/(n1 + n2)
        if self.norm == 2:
            return delta, np.dot(v1,v2)/n1/n2
        else:
            return delta, np.nan
