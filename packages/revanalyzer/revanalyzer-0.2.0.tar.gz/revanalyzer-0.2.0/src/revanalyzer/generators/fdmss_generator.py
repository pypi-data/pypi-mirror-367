# -*- coding: utf-8 -*-
"""Module for running FDMSS solver."""

import os
import numpy as np
import time
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ElementTree
from .utils import _read_array, make_cut
from pyfdmss import run

fdmss_data = "fdmss_data"


def run_fdmss(image, direction, datadir, outputdir, n_threads=1, resolution=1., show_time=False):
    """
    Running FDMSS solver for an initial image.
    
    **Input:**

     	image (str): name of binary ('uint8') file representing the image;     
     	
     	direction (str): 'x', 'y', 'z' or 'all'. If label of this parameter is 'all', all 3 possible flow directions are considered;
     	
        datadir (str): path to the folder containing image;
     	
     	outputdir (str): path to the output folder containing generated data;
        
     	n_threads (int): number of threads used by FDMSS, default: 1;
     	
     	resolution (float): resolution of studied sample (micrometers), default: 1;
     	
     	show_time (bool): Added to monitor time cost for large images,  default: False. 
    """
    if not (direction == 'x' or direction == 'y' or direction == 'z' or direction == 'all'):
        raise ValueError("Direction should be 'x', 'y', 'z' or 'all'")
    if direction == 'all':
        directions_list = ['x', 'y', 'z']
    else:
        directions_list = [direction]
    for d in directions_list:
        start_time = time.time()
        if datadir is not None:
            image_path = os.path.join(datadir, image)
        else:
            image_path = image
        config_path = os.path.join(outputdir, d + '_config.xml')
        _make_fdmss_config(config_path, d, resolution, n_threads)
        summary_path = os.path.join(outputdir, d + '_summary.xml')
        pressure_path = os.path.join(outputdir, d + '_pressure')
        velx_path = os.path.join(outputdir, d + '_velx')
        vely_path = os.path.join(outputdir, d + '_vely')
        velz_path = os.path.join(outputdir, d + '_velz')
        full_vel_path =  os.path.join(outputdir, d + '_full_vel')
        comp_vel_path =  os.path.join(outputdir, d + '_comp_vel')
        log_path = 'log.txt'
        run(config_path, image_path, summary_path, velx_path, vely_path, velz_path, pressure_path, full_vel_path, comp_vel_path, log_path)
        if show_time:
            print("---fdmss run time is %s seconds ---" % (time.time() - start_time))


def _make_fdmss_config(fileout, direction, resolution=1, n_threads=1):
    xml_data = """
<OverdozenPermsolverParams>
  <Parameter name="Resolution" datatype="float">
    <ParameterValue>1.0</ParameterValue>
  </Parameter>
  <Parameter name="TimeStep" datatype="float">
    <ParameterValue>0.0003</ParameterValue>
  </Parameter>
  <Parameter name="IterationsPerStep" datatype="unsigned int">
    <ParameterValue>100</ParameterValue>
  </Parameter>
  <Parameter name="MaximumStepsCount" datatype="unsigned int">
    <ParameterValue>140</ParameterValue>
  </Parameter>
  <Parameter name="InitialVelocityValue" datatype="float">
    <ParameterValue>0.001</ParameterValue>
  </Parameter>
  <Parameter name="Accuracy" datatype="float">
    <ParameterValue>0.01</ParameterValue>
  </Parameter>
  <Parameter name="BoundaryCondition" datatype="int">
    <ParameterValue>1</ParameterValue>
  </Parameter>
  <Parameter name="TerminationCondition" datatype="int">
    <ParameterValue>2</ParameterValue>
  </Parameter>
  <Parameter name="AccuracyOrder" datatype="int">
    <ParameterValue>0</ParameterValue>
  </Parameter>
  <Parameter name="ErrorSmoothingLength" datatype="unsigned int">
    <ParameterValue>10</ParameterValue>
  </Parameter>
  <Parameter name="ThreadsNumber" datatype="unsigned int">
    <ParameterValue>1</ParameterValue>
  </Parameter>
  <Parameter name="FlowDirectionAxis" datatype="char">
    <ParameterValue>AXIS</ParameterValue>
  </Parameter>
  <Parameter name="WaterLayerWidth" datatype="unsigned int">
    <ParameterValue>0</ParameterValue>
  </Parameter>
</OverdozenPermsolverParams>
"""
    root = ET.fromstring(xml_data)
    root[0][0].text = str(resolution)
    root[10][0].text = str(n_threads)
    root[11][0].text = direction
    tree = ElementTree(root)
    tree.write(fileout)


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


def _get_permeability(image, porosity, pressure, vel, direction):
    dim = image.shape[0]
    pores = dim**3 - np.count_nonzero(image)
    p = _pressure_diff(image, pressure, direction)
    v = np.sum(vel)/pores
    return 100*v/p*porosity/0.986*1000


def _get_porosity(image):
    dim = image.shape[0]
    pores = dim**3 - np.count_nonzero(image)
    return pores/(dim**3)
