# -*- coding: utf-8 -*-
"""Main module of the library, ensures the complete pipeline for REV analysis.
"""
import numpy as np
import os
import json
import shutil
import matplotlib.pyplot as plt
import itertools
import multiprocessing
from functools import partial
from statistics import geometric_mean
from .generators import run_fdmss, _read_array, _write_array, _subcube_ids, make_cut, generate_PNM
from .metrics import BasicMetric, BasicPNMMetric, BasicPDMetric, Permeability
from .REV_formulas import _delta, get_sREV_size, get_dREV_size_1_scalar, get_dREV_size_2_scalar, get_dREV_size_1_vector, get_dREV_size_1_scalar_dimensional, get_dREV_size_2_scalar_dimensional


class REVAnalyzer:
    """
    analysis of representativity of a given image for a given scalar or vector metric.
    """
    def __init__(self, metric, image, size, n_steps, sREV_max_step, datadir=None, outputdir='output'):
        """
        **Input:**

        	metric (subclass of BasicMetric): metric to be analyzed;
        
        	image (str or numpy.ndarray): name of binary ('uint8') file or numpy.ndarray representing the image;
            
            size (tuple (int, int, int)): linear image sizes in x, y and z directions;
                
        	n_steps (int): number of subsamples selection steps;
        
        	sREV_max_step (int): maximal step for which sREV and stationarity analysis can be performed;
        
        	datadir (str): path to the folder containing image, default: None;
        
        	outputdir (str): path to the output folder containing generated data, default: 'output'.
        """
        if not issubclass(metric.__class__, BasicMetric):
            raise TypeError("Metric should be an object of a class derived from BasicMetric.")
        self.metric = metric
        self.size = size
        self._outputdirs_cut_values = []            
        if isinstance(image, str):
            self._outputdir_cut_values = os.path.join(outputdir, image, self.metric.__class__.__name__, 'cuts_values')
            if issubclass(self.metric.__class__, BasicPDMetric):
                for i in range(3):
                    outputdir_cut_values = os.path.join(outputdir, image, 'PD'+str(i), 'cuts_values')
                    self._outputdirs_cut_values.append(outputdir_cut_values)
                    os.makedirs(outputdir_cut_values, exist_ok=True)
        elif isinstance(image, np.ndarray):
            self._outputdir_cut_values = os.path.join(outputdir, self.metric.__class__.__name__, 'cuts_values')
            if issubclass(self.metric.__class__, BasicPDMetric):
                for i in range(3):
                    outputdir_cut_values = os.path.join(outputdir, 'PD'+str(i), 'cuts_values')
                    self._outputdirs_cut_values.append(outputdir_cut_values)
                    os.makedirs(outputdir_cut_values, exist_ok=True)
        else:
            raise TypeError("Image type should be str or numpy.ndarray")
        self.image = image
        self.n_steps = n_steps
        self.sREV_max_step = sREV_max_step
        self.cut_step = (np.array(size)/n_steps).astype(int)
        self.datadir = datadir
        self.outputdir = outputdir
        self.gendatadir = None
        if isinstance(self.image, str):
            self._outputdir_vectorized_cut_values = os.path.join(self.outputdir, self.image, self.metric.__class__.__name__, 'vectorized_cuts_values')
        else:
            self._outputdir_vectorized_cut_values = os.path.join(self.outputdir, self.metric.__class__.__name__, 'vectorized_cuts_values')
        os.makedirs(self.outputdir, exist_ok=True)
        os.makedirs(self._outputdir_cut_values, exist_ok=True)
        self.cut_sizes = [(self.cut_step*(i+1)).tolist() for i in range(self.n_steps-1)]
        if self.size[0] == self.size[1] and self.size[0] == self.size[2]:
            self.geom_mean_cut_sizes = [size[0] for size in self.cut_sizes]
            self.geom_mean_cut_sizes.append(self.size[0])
        else:
            self.geom_mean_cut_sizes = [int(geometric_mean(size)) for size in self.cut_sizes]
            self.geom_mean_cut_sizes.append(int(geometric_mean(self.size)))
        self._sizes_dict = dict(zip(np.arange(1, n_steps+1), self.geom_mean_cut_sizes))
        self._sizes_dict[None] = None
        self.cut_ids = _subcube_ids(self.n_steps, self.sREV_max_step)
        self._metric_cut_names = []
        self.metric_mean = {}
        self.metric_std = {}
        self.metric_normed_std = {}
        self.metric_normed_std_1 = {}
        self.metric_normed_std_2 = {}
        self.dREV_threshold = None
        self.sREV_threshold = None
        self.stationarity_threshold = None
        self.sREV_size_1 = None
        self.sREV_size_2 = None
        self.dREV_size_1 = None
        self.dREV_size_2 = None
        self.is_fdmss_data = False
        self.is_pnm_data = False
        if isinstance(self.metric, Permeability):
            if not (self.size[0] == self.size[1] and self.size[0] == self.size[2]):
                raise ValueError("Only cubical images can be input for FDMSS solver.")
            if isinstance(self.image, str):
                self.gendatadir = os.path.join(self.outputdir, self.image, 'fdmss_data')
            else:
                self.gendatadir = os.path.join(self.outputdir, 'fdmss_data')
            fdmss_input=os.path.join(self.gendatadir, 'fdmss_input.txt')
            if os.path.isfile(fdmss_input):
                with open(fdmss_input) as f:
                    lines = [line.rstrip('\n') for line in f]
                    if lines[0] == self.metric.direction and lines[1] == str(self.metric.resolution):                        
                        self.is_fdmss_data = True
        if issubclass(self.metric.__class__, BasicPNMMetric):
            if isinstance(self.image, str):
                self.gendatadir = os.path.join(self.outputdir, self.image, 'pn_data')
            else:
                self.gendatadir = os.path.join(self.outputdir, 'pn_data')
            pn_input=os.path.join(self.gendatadir, 'pn_input.txt')
            if os.path.isfile(pn_input):
                with open(pn_input) as f:
                    lines = [line.rstrip('\n') for line in f]
                if lines[0] == str(self.n_steps) and lines[1] == str(self.sREV_max_step) and lines[2] == str(self.metric.resolution): 
                    self.is_pnm_data = True
                    

    def generate(self):
        """
        Generator of metric values for all selected subsamples.
        """
        if isinstance(self.metric, Permeability) and not self.is_fdmss_data:
            os.makedirs(self.gendatadir, exist_ok=True)
            if isinstance(self.image, str):
                run_fdmss(self.image, self.metric.direction, self.datadir, self.gendatadir, self.metric.n_threads, self.metric.resolution, self.metric.show_time)
            else:
                fileout = os.path.join(self.gendatadir, 'image.raw') 
                _write_array(self.image, fileout)
                run_fdmss('image.raw', self.metric.direction, self.gendatadir, self.gendatadir, self.metric.n_threads, self.metric.resolution, self.metric.show_time)
                os.remove(fileout)
            fdmss_input = os.path.join(self.gendatadir, 'fdmss_input.txt')            
            with open(fdmss_input, 'w') as f:
                lines = [self.metric.direction, str(self.metric.resolution), str(self.size[0])]
                f.write('\n'.join(lines))
        if isinstance(self.image, str):
            if self.datadir is not None:
                filein = os.path.join(self.datadir, self.image)
            else:
                filein = self.image
            image = _read_array(filein, self.size[0], self.size[1], self.size[2], 'uint8')
        else:
            image = self.image
        if issubclass(self.metric.__class__, BasicPNMMetric) and not self.is_pnm_data:
            os.makedirs(self.gendatadir, exist_ok=True)
            generate_PNM(image, self.size, self.n_steps, self.sREV_max_step, self.gendatadir, self.metric.n_threads, self.metric.resolution, self.metric.show_time)     
            pn_input = os.path.join(self.gendatadir, 'pn_input.txt')            
            with open(pn_input, 'w') as f:
                lines = [str(self.n_steps), str(self.sREV_max_step), str(self.metric.resolution)]
                f.write('\n'.join(lines))
        ids = _subcube_ids(self.n_steps, self.sREV_max_step)
        cuts = []
        for elem in ids:
            l = elem[0]
            idx = elem[1]
            if l  == self.n_steps:
                cuts.append(image)
            else:
                cut_size = self.cut_sizes[l-1]
                cuts.append(make_cut(image, self.size, cut_size, idx))
        data = zip(ids, cuts)
        pool = multiprocessing.Pool(processes=self.metric.n_threads) 
        results = pool.map(self._metric_for_subsample, data)
        pool.close()
        pool.join()           

    def read(self, step, cut_id=0): 
        """
        Read the generated metric value for a given subsample.
        
        **Input:**
        
        	step (int): subsamples selection step;
        	
        	cut_id (int: 0,..8): cut index .   
        
        **Output**
        
        	metric value (float or np.array(dtype='float')).       
        """
        return self.metric.read(
            self._outputdir_cut_values, step, cut_id)
    
    def show(self, step, cut_id = 0, nbins = None):
        """
        Vizualize the vector metric for a specific subsample.
        
        **Input:**
         
        	step (int): subsamples selection step;
        
        	cut_id (int: 0,..8): cut index;
        	
        	nbins (int): number of bins in histogram. For PNM-based metric only.
        """
        if not self.metric.metric_type == 'v':
            raise TypeError("Metric type should be vector")
        if issubclass(self.metric.__class__, BasicPNMMetric):
            if nbins is None:
                raise ValueError("Number of bins in histogram should be defined for the visualization of this metric")
            self.metric.show(self._outputdir_cut_values, step, cut_id, nbins)
        else:
            self.metric.show(self._outputdir_cut_values, step, cut_id)
        

    def vectorize(self):
        """
        Vectorization of generated metric data using vetorizer. For vector metric only.
        """
        if not self.metric.metric_type == 'v':
            raise TypeError("Metric type should be vector")
        os.makedirs(self._outputdir_vectorized_cut_values, exist_ok=True)
        x = np.arange(9)
        y = [0]
        steps = [i for i in range(1, self.n_steps)]
        data1 = []
        data2 = []
        data3 = []
        for step in steps:
            if step > self.sREV_max_step:
                data1 = data1 + [tup for tup in itertools.product([step], y, y)]
            elif step == self.sREV_max_step:
                data2 = data2 + [tup for tup in itertools.product([step], x, y)]
            else:
                data3 = data3 + [tup for tup in itertools.product([step], x, x)]
        data = data1 + data2 + data3
        pool = multiprocessing.Pool(processes=self.metric.n_threads) 
        results = pool.map(self._vectorize_subsample, data)
        pool.close()
        pool.join() 
        ds = [{} for i in range(1, self.n_steps)]
        for elem in results:
            ds[elem[0]-1][elem[1]] = elem[2]      
        for step in steps:     
            jsonname = 'cut_' + str(step)
            with open(os.path.join(self._outputdir_vectorized_cut_values, jsonname), 'w') as f:
                json.dump(ds[step-1], f, indent=4)     
            

    def analyze(self, dREV_threshold, sREV_threshold):
        """
        Perform the analysis of representativity.
        
        **Input:**
        
        	dREV_threshold (float, <1): threshold to estimate dREV size;
        	
        	sREV_threshold (float, <1): threshold to estimate sREV size.
        """
        self.dREV_threshold = dREV_threshold
        self.sREV_threshold = sREV_threshold
        if self.metric.metric_type == 's':
            for l in range(1, self.n_steps+1):
                if (l <= self.sREV_max_step):
                    data = [self.read(l, i) for i in range(9)]
                    if self.metric.directional:
                        self.metric_mean[l] = [
                            np.mean(list(i)) for i in zip(*data)]
                        self.metric_std[l] = [
                            np.std(list(i)) for i in zip(*data)]
                        self.metric_normed_std[l] = max(
                            [np.std(list(i))/abs(np.mean(list(i))) for i in zip(*data)])
                    else:
                        self.metric_mean[l] = np.mean(data)
                        self.metric_std[l] = np.std(data)
                        self.metric_normed_std[l] = self.metric_std[l] / \
                            abs(self.metric_mean[l])
                else:
                    if self.metric.directional:
                        self.metric_mean[l] = self.read(l, 0)
                    else:
                        self.metric_mean[l] = self.read(l, 0).item()
            self.sREV_size_1 = self._sizes_dict[get_sREV_size(
                self.metric_normed_std, self.sREV_threshold)]
            if self.metric.directional:
                self.dREV_size_1 = self._sizes_dict[get_dREV_size_1_scalar_dimensional(
                    self.metric_mean, self.dREV_threshold)]
                self.dREV_size_2 = self._sizes_dict[get_dREV_size_2_scalar_dimensional(
                    self.metric_mean, self.dREV_threshold)]
            else:
                self.dREV_size_1 = self._sizes_dict[get_dREV_size_1_scalar(
                    self.metric_mean, self.dREV_threshold)]
                self.dREV_size_2 = self._sizes_dict[get_dREV_size_2_scalar(
                    self.metric_mean, self.dREV_threshold)]
        if self.metric.metric_type == 'v':
            for l in range(1, self.n_steps):
                jsonname = 'cut_' + str(l)
                with open(os.path.join(self._outputdir_vectorized_cut_values, jsonname), 'r') as f:
                    d = json.load(f)
                deltas = [elem for elem in d.values()]
                n = deltas[0]
                if (type(n) is list):
                    self.metric_mean[l] = max(
                        [np.mean(list(i)) for i in zip(*deltas)])
                else:
                    self.metric_mean[l] = np.mean(deltas)
                if (l <= self.sREV_max_step):
                    if (type(n) is list):
                        self.metric_std[l] = max(
                            [np.std(list(i)) for i in zip(*deltas)])
                        self.metric_normed_std[l] = max(
                            [np.std(list(i))/np.mean(list(i)) for i in zip(*deltas)])
                    else:
                        self.metric_std[l] = np.std(deltas)
                        self.metric_normed_std[l] = self.metric_std[l] / \
                            self.metric_mean[l]
                    self.metric_normed_std_1[l] = self.metric_std[l] / \
                        self.dREV_threshold
                    if (self.dREV_threshold is None or self.metric_mean[l] > self.dREV_threshold):
                        self.metric_normed_std_2[l] = self.metric_normed_std[l]
                    else:
                        self.metric_normed_std_2[l] = self.metric_normed_std_1[l]
            self.dREV_size_1 = self._sizes_dict[get_dREV_size_1_vector(
                self.metric_mean, self.dREV_threshold)]
            self.sREV_size_1 = self._sizes_dict[get_sREV_size(
                self.metric_normed_std_1, self.sREV_threshold)]
            self.sREV_size_2 = self._sizes_dict[get_sREV_size(
                self.metric_normed_std_2, self.sREV_threshold)]

    def analyze_stationarity(self, stationarity_threshold):
        """
        Perform the analysis of stationarity.
        
        **Input:**
        
        	stationarity_threshold (float, <1): threshold to analyze stationarity.
        	
        **Output**
        
        	 True or False: is image stationary.
        """
        if not self.metric.metric_type == 'v':
            raise TypeError("Metric type should be vector")
        self.stationarity_threshold = stationarity_threshold
        x = np.arange(9)
        for step in range(1, self.sREV_max_step):
            ids = itertools.combinations_with_replacement(x, 2)
            pool = multiprocessing.Pool(processes=self.metric.n_threads) 
            results = pool.map(partial(self._distance_for_subsamples, step=step), ids)
            pool.close()
            pool.join()
            dmax = max(results)
            print("at step ", step, " maximal distance between subsamples is ", dmax)
            if dmax > self.stationarity_threshold:
                print("Image is nonstationary.")
                return False
        print("Image is stationary.")
        return True
            
    
    def show_results(self):
        """
        Visualization of REV analysis results.
        """
        plt.rcParams.update({'font.size': 16})
        plt.rcParams['figure.dpi'] = 300
        x = list(self.metric_mean.keys())
        x.sort()
        xerr = list(self.metric_std.keys())
        xerr.sort()
        nzeros = len(x) - len(xerr)
        fig, ax = plt.subplots()
        title = self.metric.__class__.__name__ 
        plt.title(title)
        if self.metric.metric_type == 's' and self.metric.directional:
            y = [self.metric_mean[l] for l in x]
            y1 = [i for i in zip(*y)]
            yerr = [self.metric_std[l] for l in xerr]
            for i in range(nzeros):
                yerr.append([0, 0, 0])
            yerr1 = [i for i in zip(*yerr)]
            x0 = [self._sizes_dict[i] for i in x]
            x1 = np.array(x0)-2
            x2 = np.array(x0)+2
            plt.errorbar(x1, y1[0], yerr=yerr1[0], label='x')
            plt.errorbar(x0, y1[1], yerr=yerr1[1], label='y')
            plt.errorbar(x2, y1[2], yerr=yerr1[2], label='z')
            plt.legend()
        else:
            y = [self.metric_mean[l] for l in x]
            yerr = [self.metric_std[l] for l in xerr]
            for i in range(nzeros):
                yerr.append(0)
            x1 = [self._sizes_dict[i] for i in x]
            plt.errorbar(x1, y, yerr=yerr)
        plt.xlabel("Mean size of subsample")
        if self.metric.metric_type == 's':
            plt.ylabel(self.metric.__class__.__name__)
        if self.metric.metric_type == 'v':
            plt.ylabel("difference in distance")
            ax.axhline(y=self.dREV_threshold, color='k',
                       linestyle='-', label="dREV threshold")
        plt.show()

        fig, ax = plt.subplots()
        plt.title(title)
        xdrev = x[:-1]
        xsrev = list(self.metric_normed_std.keys())
        if self.metric.metric_type == 's':
            if self.metric.directional:
                y1 = np.array(y1)
                ydrev1 = [max([_delta(y1[k][i], y1[k][i+1])
                              for k in range(3)]) for i in range(len(xdrev))]
                ydrev2 = [max([_delta(y1[k][i], y1[k][-1])
                              for k in range(3)]) for i in range(len(xdrev))]
            else:
                ydrev1 = [_delta(self.metric_mean[x[i]], self.metric_mean[x[i+1]])
                          for i in range(len(xdrev))]
                y0 = self.metric_mean[x[-1]]
                ydrev2 = [_delta(self.metric_mean[x[i]], y0)
                          for i in range(len(xdrev))]
            ysrev = [self.metric_normed_std[l] for l in xsrev]
            xsrev = [self._sizes_dict[i] for i in xsrev]
            xdrev = [self._sizes_dict[i] for i in xdrev]
            ax.plot(xsrev, ysrev, "r--", label='sREV, $\sigma_{norm}$')
            ax.plot(xdrev, ydrev1, "b-", label='dREV, $\delta_1$')
            ax.plot(xdrev, ydrev2, "g-", label='dREV, $\delta_2$')
            ax.axhline(y=self.dREV_threshold, color='k',
                       linestyle='-', label="dREV threshold")
            plt.ylabel('$\sigma_{norm}$, $\delta_1$, $\delta_2$')
        if self.metric.metric_type == 'v':
            ysrev1 = [self.metric_normed_std_1[l] for l in xsrev]
            ysrev2 = [self.metric_normed_std_2[l] for l in xsrev]
            xsrev = [self._sizes_dict[i] for i in xsrev]
            ax.plot(xsrev, ysrev1, "r-", label='sREV, $\sigma_{norm1}$')
            ax.plot(xsrev, ysrev2, "r--", label='sREV, $\sigma_{norm2}$')
            plt.ylabel("$\sigma_{norm1}$, $\sigma_{norm2}$")
        ax.axhline(y=self.sREV_threshold, color='k',
                   linestyle='--', label="sREV threshold")
        plt.xlabel("Mean size of subsample")

        plt.legend()
        plt.show()
    
    def _metric_for_subsample(self, data):
        if issubclass(self.metric.__class__, BasicPDMetric):
            outputdir = self._outputdirs_cut_values
        else:
            outputdir = self._outputdir_cut_values
        l = data[0][0]
        idx = data[0][1]
        cut = data[1]
        cut_name = 'cut'+str(l)+'_'+str(idx)
        result = self.metric.generate(cut, cut_name, outputdir, self.gendatadir)
    
    def _vectorize_subsample(self, data):
        step = data[0]
        v1 = self.read(step, data[1])
        if self.metric.directional:
            v0 = v1[0]
        else:
            v0 = v1
        if len(v0) == 0:
            return np.nan
        v2 = self.read(step + 1, data[2])
        str_elem = str(data[1]) + ', ' + str(data[2])
        result = self.metric.vectorize(v1, v2)
        if (type(result[2]) is list and (np.nan in result[2])) or (type(result[2]) is not list and np.isnan(result[2])):
            return np.nan
        return (step, str_elem, result[2])
     
    def _distance_for_subsamples(self, ids, step):
        v1 = self.read(step, ids[0])
        if ids[0] == ids[1]:
            v2 = self.read(step + 1, ids[0])
        else:
            v2 = self.read(step, ids[1])
        result = self.metric.vectorize(v1, v2)
        delta = result[2]
        if (type(delta) is list):
            return max(delta)
        else:
            return delta

