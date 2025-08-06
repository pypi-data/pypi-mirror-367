# -*- coding: utf-8 -*-
"""
Definition of Euler Density I metric. The Euler density here is calculated using the topological properties of considered voxel domain as in Vogel, H. J., Weller, U., & Schlüter, S. (2010). Quantification of soil structure based on Minkowski functions. Computers & Geosciences, 36(10), 1236-1245. See the details in documentation.
"""

from .basic_metric import BasicMetric
from ..generators import _write_array
import os
import time
import imp
import subprocess

class EulerDensityI(BasicMetric):
    """
    Class describing Euler density I metric.
    """     
    def __init__(self, n_threads = 1, show_time=False):
        """
        **Input:**
        
        n_threads (int): number of threads used for data generation, default: 1;
        
        	show_time (bool): flag to monitor time cost for large images, default: False.
        """
        super().__init__(vectorizer=None, n_threads = n_threads)
        self.metric_type = 's'
        self.show_time = show_time

    def generate(self, cut, cut_name, outputdir, gendatadir = None):
        """
        Generates Euler density for a specific subsample.
        
        **Input:**
        
        	cut (numpy.ndarray): 3D array representing a subsample;
        	
        	cut_name (str): name of subsample;
        	
        	outputdir (str): output folder.
        """        
        start_time = time.time()
        glob_path = os.getcwd()
        dimx = cut.shape[0]
        dimy = cut.shape[1]
        dimz = cut.shape[2]
        path0 = imp.find_module('revanalyzer')[1]
        jl_path = os.path.join(path0, 'jl', 'euler_density.jl')
        output_path = os.path.join(glob_path, outputdir)
        image_path = os.path.join(output_path, cut_name +'.raw')
        _write_array(cut, image_path)
        file_out = os.path.join(output_path, cut_name +'.txt')
        code = subprocess.call(['julia', jl_path, image_path, str(dimx), str(dimy), str(dimz), file_out])
        if (code != 0):
            raise RuntimeError("Error in julia run occured!")
        os.remove(image_path)
        if self.show_time:
            print("cut ", cut_name, ", run time: ")
            print("--- %s seconds ---" % (time.time() - start_time))
