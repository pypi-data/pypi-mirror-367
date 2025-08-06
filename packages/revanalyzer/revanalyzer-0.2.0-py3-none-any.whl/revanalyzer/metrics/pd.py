# -*- coding: utf-8 -*-
"""Definition of PD-based metrics. For the definition of persistence diagrams (PD) see the documentation."""

from .basic_metric import BasicMetric
import numpy as np
import matplotlib.pyplot as plt
import time
import os
import pyperspairdiamorse as pppdm
from ..vectorizers import SimpleBinningVectorizer, PersistenceImageVectorizer, LandscapeVectorizer, SilhouetteVectorizer


class BasicPDMetric(BasicMetric):
    """
    Base class of PD-based metrics. (Don't use it directly but derive from it).
    """ 
    def __init__(self, vectorizer, n_threads, show_time):
        """
        **Input:**
        
        	vectorizer (SimpleBinningVectorizer, PersistenceImageVectorizer, LandscapeVectorizer or SilhouetteVectorizer object): vectorizer to be used for PD metric.
            
            n_threads (int): number of threads used for data generation;
        	
        	show_time (bool): flag to monitor time cost for large images.
        """
        if not (isinstance(vectorizer, SimpleBinningVectorizer) or isinstance(vectorizer, PersistenceImageVectorizer) or isinstance(
            vectorizer, LandscapeVectorizer) or isinstance(vectorizer, SilhouetteVectorizer)):
            raise TypeError('Vectorizer should be an object of SimpleBinningVectorizer, PersistenceImageVectorizer, LandscapeVectorizer or SilhouetteVectorizer class')
        super().__init__(vectorizer, n_threads = n_threads)
        self.show_time = show_time
        
    def generate(self, cut, cut_name, outputdir, gendatadir = None):
        """
        Generates PD metric for a specific subsample.
        
        **Input:**
        
        	cut (numpy.ndarray): 3D array representing a subsample;
        	
        	cut_name (str): name of subsample;
        	
        	outputdir (str): output folder;
        """ 
        start_time = time.time()
        cut = cut.astype(bool)
        pds = pppdm.extract(cut)
        cut_name_out = cut_name + ".txt"
        for i, elem in enumerate(outputdir):
            fileout = os.path.join(elem, cut_name_out)
            np.savetxt(fileout, pds[i])
        if self.show_time:
            print("cut ", cut_name, ", run time: ")
            print("--- %s seconds ---" % (time.time() - start_time))        

    def show(self, inputdir, step, cut_id, title):
        """
        Transforms generated PD data to the convenient fomat for the following visualization in subclasses.
        
        **Input:**
        
        	inputdir (str): path to the folder containing generated metric data for subsamples;
                	
        	step (int): subsamples selection step;
        	
        	cut_id (int: 0,..8): cut index;
            
            title (str): image title.
        """          
        data = self.read(inputdir, step, cut_id)
        _show_pd(data, title)

    def vectorize(self, v1, v2):
        """
        Vectorize the vector metric values for a given pair of subsamples using the method of vectorizer. 
        
        **Input:**
        
        	v1 (list(dtype = float)): data for the first subsample;
        	
        	v2 (list(dtype = float)): data for the second subsample.
        
        **Output:**
        
        	(list(dtype = float), list(dtype = float), float) - a tuple, in which the first two elements are vectorized metric values for a given pair of subsamples, the third one is the normalized distance between these vectors and the last one is the cosine similarity for them. 
        """
        return self.vectorizer.vectorize(v1, v2)


class PD0(BasicPDMetric):
    """
    Class describing metric PD of rank 0.
    """    
    def __init__(self, vectorizer, n_threads = 1, show_time = False):
        """
        **Input:**
        
        	vectorizer (SimpleBinningVectorizer, PersistenceImageVectorizer, LandscapeVectorizer or SilhouetteVectorizer object): vectorizer to be used for PD metric;
            
            n_threads (int): number of threads used for data generation;
        	
        	show_time (bool): flag to monitor time cost for large images.        
        """
        super().__init__(vectorizer, n_threads, show_time)
        self.metric_type = 'v'
        
    def generate(self, cut, cut_name, outputdir, gendatadir = None):
        """
        Generates the PD of rank 0 for a specific subcube.
        
        **Input:**
        
        	cut (numpy.ndarray): subsample;
        	
        	cut_name (str): name of subcube;
        	
        	outputdir (str): output folder.
        """
        super().generate(cut, cut_name, outputdir)

    def show(self, inputdir, cut_step, cut_id):
        """
        Vizualize the PD of rank 0 for a specific subcube.
        
        **Input:**
        
        	inputdir (str): path to the folder containing generated metric data for subcubes;
        	 
        	cut_step (int): subsamples selection step;
        	
        	cut_id (int: 0,..8): cut index.
        """  
        title = 'PD0' + ",  step = " + str(cut_step) + ", id = " + str(cut_id)
        super().show(inputdir, cut_step, cut_id, title)

class PD1(BasicPDMetric):
    """
    Class describing metric PD of rank 1.
    """ 
    def __init__(self, vectorizer, n_threads = 1, show_time = False):
        """
        **Input:**
        
        	vectorizer (SimpleBinningVectorizer, PersistenceImageVectorizer, LandscapeVectorizer or SilhouetteVectorizer object): vectorizer to be used for PD metric;
            
            n_threads (int): number of threads used for data generation;
        	
        	show_time (bool): flag to monitor time cost for large images.        
        """
        super().__init__(vectorizer, n_threads, show_time)
        self.metric_type = 'v'

    def generate(self, cut, cut_name, outputdir, gendatadir = None):
        """
        Generates the PD of rank 1 for a specific subcube.
        
        **Input:**
        
        	cut (numpy.ndarray): subcube;
        	
        	cut_name (str): name of subcube;
        	
        	outputdir (str): output folder.
        """
        super().generate(cut, cut_name, outputdir)

    def show(self, inputdir, cut_step, cut_id):
        """
        Vizualize the PD of rank 0 for a specific subcube.
        
        **Input:**
        
        	inputdir (str): path to the folder containing generated metric data for subcubes;
        	 
        	cut_step (int): subsamples selection step;
        	
        	cut_id (int: 0,..8): cut index.
        """  
        title = 'PD1' + ",  step = " + str(cut_step) + ", id = " + str(cut_id)
        super().show(inputdir, cut_step, cut_id, title)


class PD2(BasicPDMetric):
    """
    Class describing metric PD of rank 2.
    """ 
    def __init__(self, vectorizer, n_threads = 1, show_time = False):
        """
        **Input:**
        
        	vectorizer (SimpleBinningVectorizer, PersistenceImageVectorizer, LandscapeVectorizer or SilhouetteVectorizer object): vectorizer to be used for PD metric;
            
            n_threads (int): number of threads used for data generation;
        	
        	show_time (bool): flag to monitor time cost for large images.        
        """
        super().__init__(vectorizer, n_threads, show_time)
        self.metric_type = 'v'

    def generate(self, cut, cut_name, outputdir, gendatadir = None):
        """
        Generates the PD of rank 2 for a specific subcube.
        
        **Input:**
        
        	cut (numpy.ndarray): subcube;
        	
        	cut_name (str): name of subcube;
        	
        	outputdir (str): output folder.
        """
        super().generate(cut, cut_name, outputdir)

    def show(self, inputdir, cut_step, cut_id):
        """
        Vizualize the PD of rank 0 for a specific subcube.
        
        **Input:**
        
        	inputdir (str): path to the folder containing generated metric data for subcubes;
        	 
        	cut_step (int): subsamples selection step;
        	
        	cut_id (int: 0,..8): cut index.
        """  
        title = 'PD2' + ",  step = " + str(cut_step) + ", id = " + str(cut_id)
        super().show(inputdir, cut_step, cut_id, title)


def _show_pd(data, title):
    b = [elem[0] for elem in data]
    d = [elem[1] for elem in data]
    plt.rcParams.update({'font.size': 16})
    plt.rcParams['figure.dpi'] = 300
    fig, ax = plt.subplots()
    plt.title(title)
    plt.plot(b, d, "ro")
    plt.axhline(y=0, color='black', linestyle='-')
    plt.axvline(x=0, color='black', linestyle='-')
    plt.xlabel("birth")
    plt.ylabel("death")
    plt.show()
