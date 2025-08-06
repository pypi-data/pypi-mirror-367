# -*- coding: utf-8 -*-
"""Definition of Permeability metric."""

import numpy as np
import os
from .basic_metric import BasicMetric
from ..generators import _read_array, make_cut


class Permeability(BasicMetric):
    """
    Class describing permeability metric.
    """
    def __init__(self, direction='all', n_threads=1, resolution=1., show_time = False):
        """
        **Input:**
        
         	direction (str): 'x', 'y', 'z' or 'all'. If label of this parameter is 'all', permeability values are generated for all 3 possible flow directions;
            
            n_threads (int): number of threads used by FDMSS, default: 1;
            
            resolution (float): resolution of studied sample (micrometers), default: 1;
            
            show_time (bool): Added to monitor time cost for large images,  default: False. 
        """
        super().__init__(vectorizer=None, n_threads = n_threads)
        self.metric_type = 's'
        self.direction = direction
        self.resolution = resolution
        self.show_time = show_time
        if direction == 'all':
            self.directional = True
            
    def generate(self, cut, cut_name, outputdir, gendatadir):
        """
        Generates permeability for a specific subsample.
        
        **Input:**
        
        	cut (numpy.ndarray): 3D array representing a subsample;
        	
        	cut_name (str): name of subsample;
        	
        	outputdir (str): output folder;
        	
        	gendatadir (str): folder with generated fdmss data output.    
        """
        fdmss_input = os.path.join(gendatadir, 'fdmss_input.txt')
        with open(fdmss_input) as f:
            lines = [line.rstrip('\n') for line in f]
            L = int(lines[2])
        if self.directional:
            directions_list = ['x', 'y', 'z']
        else:
            directions_list = [self.direction]
        for direction in directions_list:
            pressure_name = os.path.join(gendatadir, direction + '_pressure')
            vel_name  = os.path.join(gendatadir, direction + '_vel' + direction)
            pressure = _read_array(pressure_name, L, L, L, 'float32')
            vel = _read_array(vel_name, L, L, L, 'float32')
            if self.directional:
                cut_name_out = cut_name + "_" + direction + ".txt"
            else:
                cut_name_out = cut_name + ".txt"
            fileout = os.path.join(outputdir, cut_name_out)
            cut_size = (cut.shape[0], cut.shape[1], cut.shape[2])
            idx = int(cut_name[-1])
            size0 = (L, L, L)
            pressure_cut = make_cut(pressure, size0, cut_size, idx)
            vel_cut = make_cut(vel, size0, cut_size, idx)
            permeability = _get_permeability(cut, pressure_cut, vel_cut, direction)
            with open(fileout, "w") as f:
                if permeability > 0:
                    f.write(str(permeability))
                else:
                    f.write(str(0))


def _pressure_diff(image, pressure, axis):
    inv = ~image
    pressure = np.where(inv, pressure, 0)
    if axis == 'x':
        p_start = np.sum(pressure[:, :, 1])/np.sum(inv[:, :, 1])
        p_end = np.sum(pressure[:, :, -1])/np.sum(inv[:, :, -1])
    if axis == 'y':
        p_start = np.sum(pressure[:, 1, :])/np.sum(inv[:, 1, :])
        p_end = np.sum(pressure[:, -1, :])/np.sum(inv[:, -1, :])
    if axis == 'z':
        p_start = np.sum(pressure[1, :, :])/np.sum(inv[1, :, :])
        p_end = np.sum(pressure[-1, :, :])/np.sum(inv[-1, :, :])
    return (p_start - p_end)/image.shape[0]


def _get_permeability(image, pressure, vel, direction):
    dim = image.shape[0]
    pores = dim**3 - np.count_nonzero(image)
    p = _pressure_diff(image, pressure, direction)
    v = np.sum(vel)/pores
    porosity = pores/(dim**3)
    return v/p*porosity


