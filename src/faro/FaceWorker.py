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

Created on Feb 5, 2019

@author: bolme
'''

import faro.proto.face_service_pb2 as fsd
import faro.proto.geometry_pb2 as geo
import faro.proto.proto_types as pt
import numpy as np
import scipy as sp
import socket
import scipy.spatial as spat          
from faro.FaceGallery import GalleryWorker

# Standard scores can be computed by the client which may offer 
# performance benefits.  In some cases scores can only be computed 
# on the server.
SCORE_L1 = "SCORE_L1" # L1 Distance / Cityblock
SCORE_L2 = "SCORE_L2" # Euclidean
SCORE_DOT = "SCORE_DOT" # Simple dot product.
SCORE_SERVER = "SCORE_SERVER" # A non-standard, custom, or proprietary score / Requires computation on the server.

STATUS_READY = "STATUS_READY"

def getGalleryWorker(options):
    return GalleryWorker(options)


class FaceWorker(object):
    '''
    Workers handle requests for one process in a multiprocessing system.
    
    In general the methods will be called in the order: detect, locate, align, 
    extract, and score.  Not all of these methods need to do something.  Some
    deep learning algorithms do not require alignment for example.  Also, in 
    some cases detection, location, and alignment might all occur together.
    In that case it should be implemented in detect and the other methods will
    do nothing but may still be called to maintain a consistant interface.
    
    Scores are assumed to be distances where smaller indicates a better match.
    '''


    def __init__(self, options):
        '''
        Constructor
        '''
        

    def detect(self):
        '''Run a face detector and return rectangles.'''
        raise NotImplementedError("Abstract Method Called.")
        
    def locate(self):
        '''Locate facial features.'''
        raise NotImplementedError("Abstract Method Called.")
        
    def align(self):
        '''Align the images to a standard size and orientation to allow 
        recognition.'''
        raise NotImplementedError("Abstract Method Called.")
        
    def extract(self):
        '''Extract a template that allows the face to be matched.'''
        raise NotImplementedError("Abstract Method Called.")
        
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
            probe_mat = [pt.vector_proto2np(face_rec.template.data) for face_rec in score_request.face_probes.face_records]
        else:
            probe_mat = [pt.vector_proto2np(template.data) for template in score_request.template_probes.templates]
        probe_mat = np.array(probe_mat,dtype=np.float32)
                
        if len(score_request.face_gallery.face_records) > len(score_request.template_gallery.templates):
            gal_mat = [pt.vector_proto2np(face_rec.template.data) for face_rec in score_request.face_gallery.face_records]
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
        
    def version(self):
        '''Returns a three item tuple of algorithm name, version number, 
        configuration notes. '''
        raise NotImplementedError("Abstract Method Called.")
                
    def scoreType(self):
        '''Return the method used to create a score from the template.
        
        By default server computation is required.
        
        SCORE_L1, SCORE_L2, SCORE_DOT, SCORE_SERVER
        '''
        return fsd.L2
            
    
    def status(self):
        '''Return a simple status message.'''
        status_message = fsd.FaceServiceInfo()
        status_message.status = fsd.READY
        
        return status_message


    def recommendedThreshold(self,far=-1.0):
        '''Return the method used to create a score from the template.
        
        By default server computation is required.
        
        Should return a recommended score.  If a positive false accept rate is
        provided 
        '''
        
        raise NotImplementedError("Abstract Method Called.")
    
    
    def cleanexit(self):
        pass 
