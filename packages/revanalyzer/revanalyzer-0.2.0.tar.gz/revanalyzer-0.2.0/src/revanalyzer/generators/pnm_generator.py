# -*- coding: utf-8 -*-
"""Module for the generation of PNM characteristics using PNM extractor."""
import numpy as np
import time
import os
import porespy as ps
import openpnm as op
import multiprocessing
from functools import partial
from .utils import _subcube_ids, make_cut


def generate_PNM(image, size, n_steps, sREV_max_step, outputdir, n_threads = 1, resolution=1., show_time=False):
    """
    Running PNM extractor for all the selected subsamples.
    
    **Input:**

     	image (numpy.ndarray): 3D array representing the image;
     	
        size (tuple (int, int, int)): linear image sizes in x, y and z directions;
        
     	n_steps (int): number of subsamples selection steps;
     	
     	sREV_max_step (int): maximal step for which sREV and stationarity analysis can be performed;
     	
     	outputdir (str): path to the output folder containing generated data;
     	
        n_threads (int): number of threads used for data generation, default: 1;
        
     	resolution (float): resolution of studied sample, default: 1; 
        
     	show_time (bool): Added to monitor time cost for large images,  default: False. 
    """
    start_time = time.time()
    cut_step = (np.array(size)/n_steps).astype(int)
    cut_sizes = [(cut_step*(i+1)).tolist() for i in range(n_steps-1)]
    cut_sizes.append(size)
    ids = _subcube_ids(n_steps, sREV_max_step)
    cuts = []
    for elem in ids:
        l = elem[0]
        idx = elem[1]
        if l  == n_steps:
            cuts.append(image)
        else:
            cut_size = cut_sizes[l-1]
            cuts.append(make_cut(image, size, cut_size, idx))
    data = zip(ids, cuts)
    pool = multiprocessing.Pool(processes=n_threads)
    results = pool.map(partial(_pnm_for_subsample, outputdir = outputdir, resolution = resolution, show_time = show_time), data)
    pool.close()
    pool.join()
    if show_time:
        print("---total PN data generation time is %s seconds ---" % (time.time() - start_time))

def get_pn_csv(cut, cut_name, outputdir, resolution, show_time):
    """
    Calculation of PNM statistics for a given subsample and writing the result to csv file.
    
    **Input:**
    
        n_threads (int): number of threads used for data generation;

     	cut (numpy.ndarray): 3D array representing a subsample;
     	
     	cut_name (str): name of output file;
     	
     	outputdir (str): path to the output folder containing generated data;
        
     	resolution (float): resolution of studied subsample;
        
        show_time (bool): Added to monitor time cost for large images.
    """
    start_time = time.time()
    cut = cut.astype(bool)
    cut = ~cut
    parallelization = {'cores':1}
    snow_output = ps.networks.snow2(cut, voxel_size = resolution, parallelization = parallelization)
    pn = op.io.network_from_porespy(snow_output.network)
    cut_name1 = os.path.join(outputdir, cut_name)
    op.io.network_to_csv(pn, filename = cut_name1)
    if show_time:
        print(cut_name)
        print("---PNM extractor run time is %s seconds ---" % (time.time() - start_time))

def _pnm_for_subsample(data, outputdir, resolution, show_time):
    l = data[0][0]
    idx = data[0][1]
    cut = data[1]
    cut_name = 'cut'+str(l)+'_'+str(idx)
    get_pn_csv(cut, cut_name, outputdir, resolution, show_time)