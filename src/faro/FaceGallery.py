'''
MIT License

Copyright 2019 Oak Ridge National Laboratory

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
import multiprocessing as mp
import numpy as np
import faro
import h5py

_GALLERY_MAP = {}


def _readerInit():
    pass

def _openGalleryReader(gallery_name):
    if gallery_name in _GALLERY_MAP:
        pass
    else:
        f = h5py.File("swmr.h5", 'r', libver='latest', swmr=True)
        _GALLERY_MAP[gallery_name] = f
    
    
    
#faro.DEFAULT_STORAGE_DIR

class Gallery:
    def __init__(self):
        self.writer_pool = mp.Pool(1)
        self.matching_pool = mp.Pool(4)
        self.faces = []
        self.vectors = []
        self.vector_cache = None
        
    def createGallery(self):
        self.worker_pool.apply()
        
    def size(self,gallery_name, ):
        pass 
    
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
    
    def score(self,score_request):
        '''Compare templates to produce scores.'''
        score_type = self.scoreType()
        result = geo.Matrix()
        
        # Check that this is a known score type
        if score_type not in [fsd.L1,fsd.L2,fsd.NEG_DOT]:
            raise NotImplementedError("Score type <%s> not implemented."%(score_type,))
        
        # Check to make sure the probe and gallery records are correct
        if min(len(score_request.face_probes.face_records),len(score_request.template_probes.templates)) != 0:
            raise ValueError("probes argument cannot have both face_probes and template_probes defined.")
        if max(len(score_request.face_probes.face_records),len(score_request.template_probes.templates)) == 0:
            raise ValueError("no probe templates were found in the arguments.")
        if min(len(score_request.face_gallery.face_records),len(score_request.template_gallery.templates)) != 0:
            raise ValueError("gallery argument cannot have both face_gallery and template_gallery defined.")
        if max(len(score_request.face_gallery.face_records),len(score_request.template_gallery.templates)) == 0:
            raise ValueError("no gallery templates were found in the arguments.")
        
        # Generate probe and gallery matrices
        if len(score_request.face_probes.face_records) > len(score_request.template_probes.templates):
            probe_mat = [pt.vector_proto2np(face_rec.template.data) for face_rec in score_request.face_records]
        else:
            probe_mat = [pt.vector_proto2np(template.data) for template in score_request.template_probes.templates]
        probe_mat = np.array(probe_mat,dtype=np.float32)
                
        if len(score_request.face_gallery.face_records) > len(score_request.template_gallery.templates):
            gal_mat = [pt.vector_proto2np(face_rec.template.data) for face_rec in score_request.face_records]
        else:
            gal_mat = [pt.vector_proto2np(template.data) for template in score_request.template_gallery.templates]
        gal_mat = np.array(gal_mat,dtype=np.float32)
                
        # Compute the distance
        if score_type == fsd.L1:
            dist_mat = spat.distance_matrix(probe_mat,gal_mat,1)
        elif score_type == fsd.L2:
            dist_mat = spat.distance_matrix(probe_mat,gal_mat,2)
        elif score_type == fsd.NEG_DOT:
            dist_mat = -np.dot(probe_mat,gal_mat.T)
        else:
            NotImplementedError("ScoreType %s is not implemented."%(score_type,))
        
        # Return the result
        return pt.matrix_np2proto(dist_mat)


