# -*- coding: utf-8 -*-
"""Definition of PNM-based metrics."""

import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
from .basic_metric import BasicMetric
from revanalyzer.vectorizers import HistVectorizer


class BasicPNMMetric(BasicMetric):
    """
    Base class of PNM-based metrics. (Don't use it directly but derive from it).
    """  
    def __init__(self, vectorizer, n_threads, resolution, show_time):
        """
        **Input:**
        
        	vectorizer (PNMVectorizer object): vectorizer to be used for a vector metric.
                        
            n_threads (int): number threads used for data generation;
                    
            resolution (float): resolution of studied sample;
            
            show_time (bool): Added to monitor time cost for large images.
        """
        if not (isinstance(vectorizer, HistVectorizer) or (vectorizer is None)):
            raise TypeError("Vectorizer should be None or an object of HistVectorizer class.")
        super().__init__(vectorizer, n_threads = n_threads)
        self.resolution = resolution
        self.show_time = show_time

    def generate(self, cut_name, gendatadir):
        """
        Generates PNM metric for a specific subsample.
        
        **Input:**
        
            cut_name (str): name of subsample;
        	
        	gendatadir (str): folder with generated PNM data.
            
            **Output:**
        
        	df (pandas.DataFrame): data frame with pnm statistics.
        """
        cut_name = os.path.join(gendatadir, cut_name + '.csv')
        df =  pd.read_csv(cut_name)
        return df
        
        
    def show(self, inputdir, step, cut_id, nbins, metric_name):
        """
        Vizualize the vector metric for a specific subsample.
        
        **Input:**
        
        	inputdir (str): path to the folder containing generated metric data for subcubes;
        	
        	step (int): subsamples selection step;
        	
        	cut_id (int: 0,..8): cut index;
        	
        	nbins (int): number of bins in histogram;
            
            metric_name(str): name of metric.
        """
        data = self.read(inputdir, step, cut_id)
        data = data/self.resolution 
        max_value = max(data)
        range_data = [0, max_value]
        hist, bin_edges = np.histogram(
            data, bins=nbins, range=range_data, density=True)
        step1 = max_value/nbins
        x = [i*step1 for i in range(nbins)]
        plt.rcParams.update({'font.size': 16})
        plt.rcParams['figure.dpi'] = 300
        fig, ax = plt.subplots(figsize=(10, 8))
        title = metric_name + ", "  + "cut size = " + str(step) + ", id = " + str(cut_id)
        ax.set_title(title)
        ax.bar(x, hist, width=0.5, color='r')
        ax.set_xlabel(metric_name)
        ax.set_ylabel('density')
        plt.show()

    def vectorize(self, v1, v2):
        """
        Vectorize the vector metric values for a given pair of subsample. Makes normalization to voxels and calls the
        vectorizer function.
        
        **Input:**
        
        	v1 (list(dtype = float)): data for the first subsample;
        	
        	v2 (list(dtype = float)): data for the second subsample.
        
        **Output:**
        
        	(list(dtype = float), list(dtype = float), float) - a tuple, in which the first two elements are vectorized metric values for a given pair of subsamples, the third one is the normalized distance between these vectors and the last one is the cosine similarity for them. 
        """
        if not self.metric_type == 'v':
            raise TypeError("Metric type should be vector")
        v1 = v1/self.resolution
        v2 = v2/self.resolution
        res = self.vectorizer.vectorize(v1, v2)
        return res

class PoreNumber(BasicPNMMetric):
    """
    Class describing pore number metric.
    """ 
    def __init__(self, n_threads = 1, resolution = 1., show_time = False):
        """
        **Input:**
        
            n_threads (int): number of threads used for data generation, default: 1;
        
            resolution (float): resolution of studied sample, default: 1;
            
            show_time (bool): Added to monitor time cost for large images,  default: False.             
        """
        super().__init__(vectorizer=None, n_threads = n_threads, resolution = resolution, show_time = show_time)
        self.metric_type = 's'

    def generate(self, cut, cut_name, outputdir, gendatadir):
        """
        Generates pore number for a specific subsample.
        
        **Input:**
        
            cut (numpy.ndarray): 3D array representing a subsample;
        
            cut_name (str): name of subsample;
            
            outputdir (str): output folder;
        	
        	gendatadir (str): folder with generated PNM data.  
        """    
        df = super().generate(cut_name, gendatadir)
        dimx = cut.shape[0]
        dimy = cut.shape[1]
        dimz = cut.shape[2]
        volume = dimx*dimy*dimz
        pore_number = (df.shape[0] - df['pore.phase'].isna().sum())/volume
        cut_name_out = cut_name + ".txt"
        fileout = os.path.join(outputdir, cut_name_out)
        with open(fileout, "w") as f:
            f.write(str(pore_number))

class ThroatNumber(BasicPNMMetric):
    """
    Class describing throat number metric.
    """ 
    def __init__(self, n_threads = 1, resolution = 1., show_time = False):
        """
        **Input:**
        
            n_threads (int): number of threads used for data generation, default: 1;
        
            resolution (float): resolution of studied sample, default: 1;
            
            show_time (bool): Added to monitor time cost for large images,  default: False.             
        """
        super().__init__(vectorizer=None, n_threads = n_threads, resolution = resolution, show_time = show_time)
        self.metric_type = 's'

    def generate(self, cut, cut_name, outputdir, gendatadir):
        """
        Generates throat number for a specific subsample.
        
        **Input:**
        
            cut (numpy.ndarray): 3D array representing a subsample;
        
            cut_name (str): name of subsample;
            
            outputdir (str): output folder;
        	
        	gendatadir (str): folder with generated PNM data.  
        """
        dimx = cut.shape[0]
        dimy = cut.shape[1]
        dimz = cut.shape[2]
        volume = dimx*dimy*dimz
        df = super().generate(cut_name, gendatadir)
        throat_number = (df.shape[0] - df['throat.phases[0]'].isna().sum())/volume
        cut_name_out = cut_name + ".txt"
        fileout = os.path.join(outputdir, cut_name_out)
        with open(fileout, "w") as f:
            f.write(str(throat_number))

class EulerDensityII(BasicPNMMetric):
    """
    Class describing Euler density II metric.
    """     
    def __init__(self, n_threads = 1, resolution = 1., show_time = False):
        """
        **Input:**
        
            n_threads (int): number of threads used for data generation, default: 1;
        
            resolution (float): resolution of studied sample, default: 1;
            
            show_time (bool): Added to monitor time cost for large images,  default: False.             
        """
        super().__init__(vectorizer=None, n_threads = n_threads, resolution = resolution, show_time = show_time)
        self.metric_type = 's'

    def generate(self, cut, cut_name, outputdir, gendatadir):
        """
        Generates Euler density for a specific subsample.
        
        **Input:**
        
            cut (numpy.ndarray): 3D array representing a subsample;
        
            cut_name (str): name of subsample;
            
            outputdir (str): output folder;
        	
        	gendatadir (str): folder with generated PNM data.  
        """
        dimx = cut.shape[0]
        dimy = cut.shape[1]
        dimz = cut.shape[2]
        volume = dimx*dimy*dimz
        df = super().generate(cut_name, gendatadir)
        euler_number = (df['throat.phases[0]'].isna().sum()-df['pore.phase'].isna().sum())/volume
        cut_name_out = cut_name + ".txt"
        fileout = os.path.join(outputdir, cut_name_out)
        with open(fileout, "w") as f:
            f.write(str(euler_number))

class MeanPoreRadius(BasicPNMMetric):
    """
    Class describing mean pore radius metric.
    """ 
    def __init__(self, n_threads = 1, resolution = 1., show_time = False):
        """
        **Input:**
        
            n_threads (int): number of threads used for data generation, default: 1;
        
            resolution (float): resolution of studied sample, default: 1;
            
            show_time (bool): Added to monitor time cost for large images,  default: False.             
        """
        super().__init__(vectorizer=None, n_threads = n_threads, resolution = resolution, show_time = show_time)
        self.metric_type = 's'

    def generate(self, cut, cut_name, outputdir, gendatadir):
        """
        Generates pore radius for a specific subsample.
        
        **Input:**
        
            cut (numpy.ndarray): 3D array representing a subsample;
        
            cut_name (str): name of subsample;
            
            outputdir (str): output folder;
        	
        	gendatadir (str): folder with generated PNM data.   
        """
        df = super().generate(cut_name, gendatadir)
        mean_pore_radius = np.mean(df['pore.inscribed_diameter'].dropna().tolist())/2
        cut_name_out = cut_name + ".txt"
        fileout = os.path.join(outputdir, cut_name_out)
        with open(fileout, "w") as f:
            f.write(str(mean_pore_radius))

class MeanThroatRadius(BasicPNMMetric):
    """
    Class describing mean throat radius metric.
    """     
    def __init__(self, n_threads = 1, resolution = 1., show_time = False):
        """
        **Input:**
        
            n_threads (int): number of threads used for data generation, default: 1;
        
            resolution (float): resolution of studied sample, default: 1;
            
            show_time (bool): Added to monitor time cost for large images,  default: False.             
        """
        super().__init__(vectorizer=None, n_threads = n_threads, resolution = resolution, show_time = show_time)
        self.metric_type = 's'

    def generate(self, cut, cut_name, outputdir, gendatadir):
        """
        Generates throat radius for a specific subsample.
        
        **Input:**
        
            cut (numpy.ndarray): 3D array representing a subsample;
        
            cut_name (str): name of subsample;
            
            outputdir (str): output folder;
        	
        	gendatadir (str): folder with generated PNM data.    
        """
        df = super().generate(cut_name, gendatadir)
        mean_throat_radius = np.mean(df['throat.inscribed_diameter'].dropna().tolist())/2
        cut_name_out = cut_name + ".txt"
        fileout = os.path.join(outputdir, cut_name_out)
        with open(fileout, "w") as f:
            f.write(str(mean_throat_radius))
            
class MeanConnectivity(BasicPNMMetric):
    """
    Class describing mean connectivity metric.
    """     
    def __init__(self, n_threads = 1, resolution = 1., show_time = False):
        """
        **Input:**
        
            n_threads (int): number of threads used for data generation, default: 1;
        
            resolution (float): resolution of studied sample, default: 1;
            
            show_time (bool): Added to monitor time cost for large images,  default: False.             
        """
        super().__init__(vectorizer=None, n_threads = n_threads, resolution = resolution, show_time = show_time)
        self.metric_type = 's'

    def generate(self, cut, cut_name, outputdir, gendatadir):
        """
        Generates mean connectivity for a specific subsample.
        
        **Input:**
        
            cut (numpy.ndarray): 3D array representing a subsample;
        
            cut_name (str): name of subsample;
            
            outputdir (str): output folder;
        	
        	gendatadir (str): folder with generated PNM data.    
        """
        df = super().generate(cut_name, gendatadir)
        pore_number = df.shape[0] - df['pore.phase'].isna().sum()
        con1 = df['throat.conns[0]'].dropna().tolist()
        con2 = df['throat.conns[1]'].dropna().tolist()
        con = con1 +con2
        (unique, counts) = np.unique(con, return_counts=True)
        counts0 = [0 for i in range(pore_number) if i not in unique]
        counts = counts.tolist() + counts0
        mean_con = np.mean(counts)

        cut_name_out = cut_name + ".txt"
        fileout = os.path.join(outputdir, cut_name_out)
        with open(fileout, "w") as f:
            f.write(str(mean_con))

class PoreRadius(BasicPNMMetric):
    """
    Class describing pore radius metric.
    """ 
    def __init__(self, vectorizer, n_threads = 1, resolution = 1., show_time = False):
        """
        **Input:**
        
            vectorizer (HistVectorizer object): vectorizer to be used for a vector metric;
        
            n_threads (int): number of threads used for data generation, default: 1;
        
            resolution (float): resolution of studied sample, default: 1;
            
            show_time (bool): Added to monitor time cost for large images,  default: False. 
        """
        super().__init__(vectorizer, n_threads = n_threads, resolution = resolution, show_time = show_time)
        self.metric_type = 'v'

    def generate(self, cut, cut_name, outputdir, gendatadir):
        """
        Generates pore radius distribution for a specific subsample.
        
        **Input:**
        
        	cut (numpy.ndarray): 3D array representing a subsample;
        	
        	cut_name (str): name of subsample;
        	
        	outputdir (str): output folder;
        	
        	gendatadir (str): folder with generated PNM data.  
        """
        df = super().generate(cut_name, gendatadir)
        pore_radius = np.array(df['pore.inscribed_diameter'].dropna().tolist())/2
        cut_name_out = cut_name + ".txt"
        fileout = os.path.join(outputdir, cut_name_out)
        np.savetxt(fileout, pore_radius, delimiter='\t')

    def show(self, inputdir, step, cut_id, nbins):
        """
        Vizualize pore radius distribution for a specific subsample.
        
        **Input:**
        
        	inputdir (str): path to the folder containing generated metric data for subsamples;
        	 
        	step (int): subsamples selection step;
        	
        	cut_id (int: 0,..8): cut index;
        	
        	nbins (int): number of bins in histogram.  
        """        
        super().show(inputdir, step, cut_id, nbins, 'pore radius')
        
class ThroatRadius(BasicPNMMetric):
    """
    Class describing throat radius metric.
    """ 
    def __init__(self, vectorizer, n_threads = 1, resolution = 1., show_time = False):
        """
        **Input:**
        
            vectorizer (HistVectorizer object): vectorizer to be used for a vector metric;
        
            n_threads (int): number of threads used for data generation, default: 1;
        
            resolution (float): resolution of studied sample, default: 1;
            
            show_time (bool): Added to monitor time cost for large images,  default: False. 
        """
        super().__init__(vectorizer, n_threads = n_threads, resolution = resolution, show_time = show_time)
        self.metric_type = 'v'

    def generate(self, cut, cut_name, outputdir, gendatadir):
        """
        Generates throat radius distribution for a specific subsample.
        
        **Input:**
        
        	cut (numpy.ndarray): 3D array representing a subsample;
        	
        	cut_name (str): name of subsample;
        	
        	outputdir (str): output folder;
        	
        	gendatadir (str): folder with generated PNM data.    
        """
        df = super().generate(cut_name, gendatadir)
        throat_radius = np.array(df['throat.inscribed_diameter'].dropna().tolist())/2
        cut_name_out = cut_name + ".txt"
        fileout = os.path.join(outputdir, cut_name_out)
        np.savetxt(fileout, throat_radius, delimiter='\t')

    def show(self, inputdir, step, cut_id, nbins):
        """
        Vizualize throat radius distribution for a specific subsample.
        
        **Input:**
        
        	inputdir (str): path to the folder containing generated metric data for subsamples;
        	 
        	step (int): subsamples selection step;
        	
        	cut_id (int: 0,..8): cut index;
        	
        	nbins (int): number of bins in histogram.
        """       
        super().show(inputdir, step, cut_id, nbins, 'throat radius')
        
class Connectivity(BasicPNMMetric):
    """
    Class describing connectivity metric.
    """     
    def __init__(self, vectorizer, n_threads = 1, resolution = 1., show_time = False):
        """
        **Input:**
        
            vectorizer (HistVectorizer object): vectorizer to be used for a vector metric;
        
            n_threads (int): number of threads used for data generation, default: 1;
        
            resolution (float): resolution of studied sample, default: 1;
            
            show_time (bool): Added to monitor time cost for large images,  default: False. 
        """
        super().__init__(vectorizer, n_threads = n_threads, resolution = resolution, show_time = show_time)
        self.metric_type = 'v'

    def generate(self, cut, cut_name, outputdir, gendatadir):
        """
        Generates connectivity distribution for a specific subsample.
        
        **Input:**
        
        	cut (numpy.ndarray): 3D array representing a subsample;
        	
        	cut_name (str): name of subsample;
        	
        	outputdir (str): output folder;
        	
        	gendatadir (str): folder with generated PNM data.    
        """
        df = super().generate(cut_name, gendatadir)
        pore_number = df.shape[0] - df['pore.phase'].isna().sum()
        con1 = df['throat.conns[0]'].dropna().tolist()
        con2 = df['throat.conns[1]'].dropna().tolist()
        con = con1 +con2
        (unique, counts) = np.unique(con, return_counts=True)
        counts0 = [0 for i in range(pore_number) if i not in unique]
        connectivity = counts.tolist() + counts0
        cut_name_out = cut_name + ".txt"
        fileout = os.path.join(outputdir, cut_name_out)
        np.savetxt(fileout, connectivity, delimiter='\t')

    def show(self, inputdir, step, cut_id, nbins):
        """
        Vizualize the connectivity distribution for a specific subsample.
        
        **Input:**
        
        	inputdir (str): path to the folder containing generated metric data for subsamples;
        	 
        	step (int): subsamples selection step;
        	
        	cut_id (int: 0,..8): cut index;
        	
        	nbins (int): number of bins in histogram. 
        """        
        super().show(inputdir, step, cut_id, nbins, 'connectivity')
