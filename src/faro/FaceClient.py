#! /usr/bin/env python

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

Created on Jul 18, 2018

@author: bolme
'''

import faro.proto.face_service_pb2_grpc as fs
import grpc
import faro.proto.proto_types as pt
import faro.proto.face_service_pb2 as fsd
import time

class FaceClient(object):
    '''
    
    '''
    def __init__(self,options,max_message_length=-1):
        
        channel_options = [("grpc.max_send_message_length", max_message_length),
                           ("grpc.max_receive_message_length", max_message_length)]

        
        try:
            self.max_async_jobs = 8 # TODO: This needs to come from options
            self.max_async_jobs = options.max_async_jobs
        except:
            pass
        
        self.max_async_jobs = max(self.max_async_jobs,1)
        self.running_async_jobs = []
        
        channel = grpc.insecure_channel(options.detect_port,
                                        options=channel_options)
        
        self.detect_stub = fs.FaceRecognitionStub(channel)
        
        channel = grpc.insecure_channel(options.rec_port,
                                        options=channel_options)
        self.rec_stub = fs.FaceRecognitionStub(channel)
        
        self.is_ready,self.info = self.status(False)
        print (self.status)
        

    def detect(self,im,best=False,threshold=None,min_size=None, run_async=False):
        request = fsd.DetectionRequest()
        try:
            request.image.CopyFrom( pt.image_np2proto(im))
        except:
            request.image.CopyFrom( pt.image_np2proto(im.asOpenCV2()[:,:,::-1]))
        request.options.best=best
        
        if threshold == None:
            request.options.threshold = self.info.detection_threshold
        else: 
            request.options.threshold = float(threshold)
            
        if run_async == False:
            face_records = self.detect_stub.detect(request,None)
        elif run_async == True:
            face_records = self.detect_stub.detect.future(request,None)
            face_records = face_records.result()
        
        if min_size is not None:
            # iterate through the list in reverse order because we are deleting as we go
            for i in range(len(face_records.face_records))[::-1]:
                if face_records.face_records[i].detection.location.width < min_size:
                    del face_records.face_records[i]
        
        # TODO: This is a temporary fix.
        if best and len(face_records.face_records) > 1:
            print( "WARNING: detector service does not seem to support best mode.  To many faces returned." )
            face_records.face_records.sort(key=lambda x: -x.detection.score)
            #print(detections.detections)
            while len(face_records.face_records) > 1:
                del face_records.face_records[-1]
                
            assert len(face_records.face_records) == 1
        
        if best and len(face_records.face_records) == 0:
            print( "WARNING: detector service does not seem to support best mode.  No faces returned." )
            
            # in this case select the center of the image
            det = face_records.face_records.add().detection
            h,w = im.shape[:2]
            s = 0.8*min(w,h)
            det.location.CopyFrom(pt.rect_val2proto(0.5*w-0.5*s,0.5*h-0.5*s, s, s))
            det.score = -1.0 
            
            det.detection_id = 1
            
            assert len(face_records.face_records) == 1            
                                
        return face_records
    
    def extract(self,im,face_records):
        request = fsd.ExtractRequest()
        try:
            request.image.CopyFrom( pt.image_np2proto(im))
        except:
            request.image.CopyFrom( pt.image_np2proto(im.asOpenCV2()[:,:,::-1]))
            
        request.records.CopyFrom(face_records)
        
        #request.options.threshold = 0.9
        
        face_records = self.rec_stub.extract(request,None)
        return face_records

    #def detectAndExtract(self,im,best=False,threshold=0.9):
    #    request = fsd.DetectionRequest()
    #    try:
    #        request.image.CopyFrom( pt.image_np2proto(im))
    #    except:
    #        request.image.CopyFrom( pt.image_np2proto(im.asOpenCV2()[:,:,::-1]))
    #    request.options.best=best


    #    request.options.threshold = threshold

    #    face_records = self.detect_rec_stub.detectAndExtract(request,None)


    #    assert len(face_records.face_records) == 1

    #    if best and len(face_records.face_records) == 0:
    #        print( "WARNING: detector service does not seem to support best mode.  No faces returned." )

    #        # in this case select the center of the image
    #        det = face_records.face_records.add().detection
    #        h,w = im.shape[:2]
    #        s = 0.8*min(w,h)
    #        det.location.CopyFrom(pt.rect_val2proto(0.5*w-0.5*s,0.5*h-0.5*s, s, s))
    #        det.score = -1.0

    #        det.detection_id = 1

    #        assert len(face_records.face_records) == 1

    #    return face_records

    def score(self,probe,gallery):
        '''
        '''
        request = fsd.ScoreRequest()
        
        # Copy the templates into the request
        for face_rec in probe:
            request.template_probes.templates.add().CopyFrom(face_rec.template)
        for face_rec in gallery:
            request.template_gallery.templates.add().CopyFrom(face_rec.template)
        
        # Run the computation on the server
        dist_mat = self.rec_stub.score(request,None)
        return pt.matrix_proto2np(dist_mat)

    def echo(self,mat):
        '''
        '''
        request = pt.matrix_np2proto(mat)
        
        
        # Run the computation on the server
        dist_mat = self.rec_stub.echo(request,None)
        
        return pt.matrix_proto2np(dist_mat)

    def status(self,verbose=False):
        request = fsd.FaceStatusRequest()
        
        status_message = self.rec_stub.status(request,None)
        if verbose:
            print(type(status_message),status_message)
            
        return status_message.status == fsd.READY, status_message
        


