# -*- coding: utf-8 -*-
"""Definition of basic metric"""

import numpy as np
import os


class BasicMetric:
    """
    Base class of all metrics. (Don't use it directly but derive from it).
    """    
    def __init__(self, vectorizer, n_threads):
        """
        **Input:**
        
        	vectorizer (subclass of BasicVectorizer): vectorizer to be used for a vector metric;
            
            n_threads (int): number of threads used for data generation.
        """
        self.vectorizer = vectorizer
        self.n_threads = n_threads
        self.directional = False
        self.metric_type = None
        
       
    def read(self, inputdir, step, cut_id):
        """
        Read the metric data generated for a specific subsample.
        
        **Input:**
        
        	inputdir (str): path to the folder containing image;
        	
        	step (int): subsamples selection step;
        	
        	cut_id (int: 0,..8): cut index.  
        
        **Output:**
        
        	metric value (float or np.array(dtype='float')).
        """
        if self.directional:
            directions = ('_x', '_y', '_z')
            cut_names = ["cut" + str(step) + "_" + str(cut_id) + direction + ".txt" for direction in directions]
            data = []
            for cut_name in cut_names:
                if inputdir is not None:
                    filein = os.path.join(inputdir, cut_name)
                else:
                    filein = cut_name
                d = np.loadtxt(filein, delimiter=" ", dtype=float)
                if self.metric_type == 'v':
                    data.append(d)
                if self.metric_type == 's':
                    if np.isnan(d) or np.isinf(d):
                        data.append(0)
                    else:
                        data.append(d.item())
            return data
        else:
            cut_name = "cut" + str(step) + "_" + str(cut_id) + ".txt"
            if inputdir is not None:
                filein = os.path.join(inputdir, cut_name)
            else:
                filein = cut_name
            data = np.loadtxt(filein, delimiter=" ", dtype=float)
            if self.metric_type == 's' and np.isnan(data):
                data = np.array(0)
            return data
