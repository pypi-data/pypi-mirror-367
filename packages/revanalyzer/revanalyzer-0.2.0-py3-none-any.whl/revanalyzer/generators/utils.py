# -*- coding: utf-8 -*-
""" Utilities for metric generators."""

import numpy as np
import os

def _read_array(image, dimx, dimy, dimz, dtype):
    v = np.fromfile(image, dtype=dtype, sep="")
    return v.reshape([dimx, dimy, dimz])


def _write_array(A, fileout):
    A.astype('uint8').tofile(fileout)


def _subcube_ids(n_steps, sREV_max_step):
    ids = []
    for l in range(n_steps):
        if (l <= sREV_max_step-1):
            for idx in range(9):
                ids.append((l+1, idx))
        else:
            ids.append((l+1, 0))
    return ids


def make_cut(A, L, cut_size, idx):
    """
    Making subsample cut for a given 3D array. 
    
    **Input:**
     
     	A(np.array): initial 3D array;
     
     	L (tuple (int, int, int)): linear image sizes in x, y and z directions;
     	 
     	cut_size (list [int, int, int]): linear image sizes of subsample;
     	
     	idx (int): index of subcube (0,1,..8). idx = 0 corresponds to the center subsample, idx = 1,..8 corrspond to the corner subsamples.
    """
    if not len(A.shape) == 3:
        raise ValueError("Initial array should have 3 dimensions.")
    if idx < 0 or idx > 8:
        raise ValueError("Index value should be from the set (0,1,..8).")
    if idx == 0:
        return A[int((L[0]-cut_size[0])/2):int((L[0]+cut_size[0])/2), 
                 int((L[1]-cut_size[1])/2):int((L[1]+cut_size[1])/2), 
                 int((L[2]-cut_size[2])/2):int((L[2]+cut_size[2])/2)]
    if idx == 1:
        return A[:cut_size[0], :cut_size[1], :cut_size[2]]
    if idx == 2:
        return A[:cut_size[0], :cut_size[1], L[2]-cut_size[2]:]
    if idx == 3:
        return A[:cut_size[0], L[1]-cut_size[1]:, :cut_size[2]]
    if idx == 4:
        return A[L[0]-cut_size[0]:, :cut_size[1], :cut_size[2]]
    if idx == 5:
        return A[L[0]-cut_size[0]:, L[1]-cut_size[1]:, L[2]-cut_size[2]:]
    if idx == 6:
        return A[:cut_size[0], L[1]-cut_size[1]:, L[2]-cut_size[2]:]
    if idx == 7:
        return A[L[0]-cut_size[0]:, :cut_size[1], L[2]-cut_size[2]:]
    if idx == 8:
        return A[L[0]-cut_size[0]:, L[1]-cut_size[1]:, :cut_size[2]]
