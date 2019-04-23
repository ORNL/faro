'''
MIT License

Copyright (c) 2019 Oak Ridge National Laboratory

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Created on Feb 14, 2019

@author: bolme
'''

import numpy as np
import faro.proto.proto_types as pt

class Gallery:
    def __init__(self):
        self.faces = []
        self.vectors = []
        self.vector_cache = None
        
    def addTemplate(self,temp):
        self.faces.append(temp)
        self.vectors.append(pt.vector_proto2np(temp.template))
        self.vector_cache = None
        
    def search(self,temp,max_results=10):
        if self.vector_cache is None:
            #print "Creating fast template cache."
            self.vector_cache = np.array(self.vectors,dtype=np.float32)
        temp = temp.reshape(1,-1)
        
        scores = np.dot(temp, self.vector_cache.T)
        
        scores = scores.flatten()
        
        results = list(zip(self.faces,scores))
        results.sort(key=lambda x: -x[1])
        
        results = results[:max_results]
        
        return results

