# -*- coding: utf-8 -*-
"""
Formulas for the calculation of dREV and sREV sizes for scalar and vector metrics.
"""

def _delta(a, b):
    if (a+b != 0):
        return 2*abs((a-b)/((a+b)))
    else:
        return 0


def get_sREV_size(sigmas_n, threshold):
    """
    sREV size calculation (can be applied both for scalar and vector metrics).
    
    **Input:**
         
    	sigmas_n (dict, int[float]): dictionary, in which a key is a subsamples selection step, and a value is a normailzed standard deviation for this step;
    
    	threshold (float, <1): threshold to estimate sREV size.
    
    **Output:**
    
    	sREV step (int): subsamples selection step, corresponding to sREV size.
    """
    sigmas_n = {key: val for key, val in sigmas_n.items() if val != 0.0}
    steps = list(sigmas_n.keys())
    steps.sort(reverse=True)
    for i, l in enumerate(steps):
        if sigmas_n[l] > threshold:
            if i == 0:
                return None
            else:
                return steps[i-1]
    return steps[-1]


def get_dREV_size_1_scalar(values, threshold):
    """
    dREV size calculation for scalar metric using formula (dREV_size_1). See the documentation.
    
    **Input:**
    
    	values (dict, int[float]): dictionary, in which a key is a subsamples selection step, and a value is a difference of metric mean values for a current and next steps;
      
    	threshold (float, <1): threshold to estimate dREV size.
    
    **Output:**
    
    	dREV step (int): subsamples selection step, corresponding to dREV size.
    """
    steps = list(values.keys())
    steps.sort(reverse=True)
    for i in range(len(steps)-1):
        if _delta(values[steps[i]], values[steps[i+1]]) > threshold:
            if i == 0:
                return None
            else:
                return steps[i]
    return steps[-1]


def get_dREV_size_1_scalar_dimensional(values, threshold):
    """
    dREV size calculation for scalar metric defined i 'x', 'y' an 'z' directions using formula (dREV_size_1).
    Returns subsamples selection step, corresponding to maximal dREV size over all the directions.
    
    **Input:**
    
    	values (dict, int[list(dtype=float)]): dictionary, in which a key is a a subsamples selection step, and a value is a list of the differences of metric mean values for a current and next steps computed in all directions;
    	  
    	threshold (float, <1): threshold to estimate dREV size.
    
    **Output:**
    
    	dREV step(int): subsamples selection step, corresponding to dREV size.
    """
    steps = list(values.keys())
    steps.sort(reverse=True)
    result = []
    for k in range(3):
        label = 0
        for i in range(len(steps)-1):
            if _delta(values[steps[i]][k], values[steps[i+1]][k]) > threshold:
                if i == 0:
                    return None
                else:
                    result.append(steps[i])
                    label = 1
        if (label == 0):
            result.append(sizes[-1])
    return max(result)


def get_dREV_size_2_scalar(values, threshold):
    """
    dREV size calculation for scalar metric using formula (dREV_size_2). See the documentation.
    
    **Input:**
    
    	values (dict, int[float]): dictionary, in which a key is a subsamples selection step, and a value is a difference of metric mean values for a current and next steps;
     
    	threshold (float, <1): threshold to estimate dREV size.
    
    **Output:**
    
    	dREV step (int): subsamples selection step, corresponding to dREV size.
    """
    steps = list(values.keys())
    steps.sort(reverse=True)
    value0 = values[steps[0]]
    for i in range(1, len(steps)):
        if _delta(values[steps[i]], value0) > threshold:
            if i == 1:
                return None
            else:
                return steps[i-1]
    return steps[-1]


def get_dREV_size_2_scalar_dimensional(values, threshold):
    """
    dREV size calculation for scalar metric defined i 'x', 'y' an 'z' directions using formula (dREV_size_2).
    Returns subsamples selection step, corresponding to maximal dREV size over all the directions.
    
    **Input:**
    
    	values (dict, int[list(dtype=float)]): dictionary, in which a key is a subsamples selection step, and a value is a list of the differences of metric mean values for a current and next steps computed in all directions;
    	  
    	threshold (float, <1): threshold to estimate dREV size.
    
    **Output:**
    
    	dREV step (int): subsamples selection step, corresponding to dREV size.
    """
    steps = list(values.keys())
    steps.sort(reverse=True)
    result = []
    for k in range(3):
        value0 = values[steps[0]][k]
        label = 0
        for i in range(len(steps)-1):
            if _delta(values[steps[i]][k], value0) > threshold:
                if i == 0:
                    return None
                else:
                    result.append(steps[i])
                    label = 1
        if label == 0:
            result.append(steps[-1])
    return max(result)


def get_dREV_size_1_vector(values, threshold):
    """
    dREV size calculation for vector metric. 
    
    **Input:**
    
    	values (dict, int[float]): dictionary, in which a key is a subsamples selection step, and a value is a mean distance between vectors at a current and next steps;
    	  
    	threshold (float, <1): threshold to estimate dREV size.
    
    **Output:**
    
    	dREV size (int): subsamples selection step, corresponding to dREV size.
    """
    steps = list(values.keys())
    steps.sort(reverse=True)
    for i in range(len(steps)):
        if values[steps[i]] > threshold:
            if i == 0:
                return None
            else:
                return steps[i-1]
    return steps[-1]
