import numpy as np


class LocalMaximumDetector:
    def __init__(self,max_length=1000000):
        self.max_length = max_length
        self.maxes = np.zeros((max_length,2),dtype=np.int)
        self.vals = np.zeros((max_length,),dtype=np.float)
    
    def __call__(self, mat, threshold = None, sort_results = True):
        return None
        '''
        All any local maximum that are greater than threshhold up to a total of 
        max_length.
        
        To save time arrays that hold the maxes and vals that are created 
        once and reused for each call.  This means that local maximum detection
        is not thread safe. If using this class with threads create an instance
        for each thread.
        
        @param mat: 2d Real Matrix input.
        @param threshold: Mininum value of local maxima.
        @param sort_results: set to False to save time and return an unorderd list.
        
        @returns: maxes,vals
        '''

        
        

