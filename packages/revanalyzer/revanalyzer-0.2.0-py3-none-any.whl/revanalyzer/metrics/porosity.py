# -*- coding: utf-8 -*-
"""Definition of Porosity metric."""

import numpy as np
import os
from .basic_metric import BasicMetric


class Porosity(BasicMetric):
    """
    Class describing porosity metric.
    """
    def __init__(self, n_threads = 1):
        super().__init__(vectorizer=None, n_threads = n_threads)
        self.metric_type = 's'

    def generate(self, cut, cut_name, outputdir, gendatadir = None):
        """
        Generates porosity for a specific subsample.
        
        **Input:**
        
        	cut (numpy.ndarray): 3D array representing a subsample;
        	
        	cut_name (str): name of subsample;
        	
        	outputdir (str): output folder.
        """
        porosity = 1 - np.count_nonzero(cut)/(cut.shape[0]*cut.shape[1]*cut.shape[2])
        cut_name_out = cut_name + ".txt"
        fileout = os.path.join(outputdir, cut_name_out)
        with open(fileout, "w") as f:
            f.write(str(porosity))
