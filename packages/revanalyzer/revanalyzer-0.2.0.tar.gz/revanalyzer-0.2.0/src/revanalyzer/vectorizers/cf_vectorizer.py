# -*- coding: utf-8 -*-
"""Definition of CF vectorizer"""

import numpy as np
from .basic_vectorizer import BasicVectorizer


class CFVectorizer(BasicVectorizer):
    """
    Class describing CF vectorizer.
    """   
    def __init__(self, norm=2, mode='max'):
        """
        **Input:**
        
        	mode (str): can be 'all' or 'max'. If mode = 'all', CF calculated for 'x', 'y' and 'z' directions are concatenated into one vector during vectorization. If mode = 'max', CF calculared for different directions are vectorizes  independently. 
        	Then at the analisys step, maximal differences and deviations over 3 directions are taking for REV sizes calculation. Default: 'max';
        	
        	norm (int): Norm of vectors used in REV analysis. The same, as parameter 'ord' in numpy.linalg.norm function, default: 2.
        """      
        super().__init__(norm)
        self.mode = mode

    def vectorize(self, v1, v2):
        """
        Vectorize the vector metric values for a given pair of subsamples. 
        
        **Input:**
        
        	v1 (list(dtype = float)): data for the first subsample;
        	
        	v2 (list(dtype = float)): data for the second subsample.
        
        **Output:**
        
        Depends on the chosen mode.
        
        	If mode = 'all':
        
        		(list(dtype = float), list(dtype = float), float) - a tuple, in which the first two elements are vectorized metric values for a given pair of subsamples, the third one is the normalized distance between these vectors and the last one is the cosine similarity for them. 
        
        	If mode = 'max:
        
        		(list(list(dtype = float)), list(list(dtype = float)), list(float)) - a tuple, in which the first two elements are vectorized metric values in 'x', 'y' and 'z' directions for a given pair of subsamples, the third one is the list of normalized distances between these vectors and the last one is the list of cosine similarity values for them..        
        """
        if not (self.mode == 'max' or self.mode == 'all'):
            raise ValueError("Mode should be 'max' or 'all'.")
        n = min(len(v1[0]), len(v2[0]))
        if self.mode == 'max':
            v_res1 = []
            v_res2 = []
            deltas = []
            cos_sims = []
            for i in range(3):
                v1i = v1[i][:n]
                v2i = v2[i][:n]
                delta, cos_sim = super()._compare_vectors(v1i, v2i)
                v_res1.append(v1i)
                v_res2.append(v2i)
                deltas.append(delta)
                cos_sims.append(cos_sims)
        if self.mode == 'all':
            v_res1 = np.concatenate([v1[0][:n], v1[1][:n], v1[2][:n]]).tolist()
            v_res2 = np.concatenate([v2[0][:n], v2[1][:n], v2[2][:n]]).tolist()
            deltas, cos_sims = super()._compare_vectors(v_res1, v_res2)
        return v_res1, v_res2, deltas, cos_sims
