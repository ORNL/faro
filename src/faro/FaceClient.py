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
import faro

class ClientOptions(object):
    pass

DEFAULT_MAX_ASYNC = 4

def getDefaultClientOptions():
    '''
    Create an object containing good default options for the client.
    '''
    
    options = ClientOptions()
    options.max_async = 4
    options.detect_port = 'localhost:50030'
    options.rec_port = 'localhost:50030'
    
    return options

class FaceClient(object):
    '''
    
    '''
    def __init__(self,options,max_message_length=-1):
        
        channel_options = [("grpc.max_send_message_length", max_message_length),
                           ("grpc.max_receive_message_length", max_message_length)]

        self.max_async_jobs = DEFAULT_MAX_ASYNC # TODO: This needs to come from options
        
        try:
            self.max_async_jobs = options.max_async
        except:
            pass
        
        self.max_async_jobs = max(self.max_async_jobs,1)
        self.async_sleep_time = 0.001
        self.running_async_jobs = []
        
        channel = grpc.insecure_channel(options.detect_port,
                                        options=channel_options)
        
        self.detect_stub = fs.FaceRecognitionStub(channel)
        
        channel = grpc.insecure_channel(options.rec_port,
                                        options=channel_options)
        self.rec_stub = fs.FaceRecognitionStub(channel)
        
        self.is_ready,self.info = self.status(False)
        print (self.status)
        
    def waitOnResults(self):
        #if len(self.running_async_jobs) >= self.max_async_jobs:
            #print("Waiting:",len(self.running_async_jobs))
        while len(self.running_async_jobs) >= self.max_async_jobs:
            self.running_async_jobs = list(filter(lambda x: x.running(),self.running_async_jobs))
            if len(self.running_async_jobs) >= self.max_async_jobs: 
                time.sleep(self.async_sleep_time)

    def detect(self,im,best=False,threshold=None,min_size=None, run_async=False,source=None,subject_id=None):
        request = fsd.DetectRequest()
        try:
            request.image.CopyFrom( pt.image_np2proto(im))
        except:
            request.image.CopyFrom( pt.image_np2proto(im.asOpenCV2()[:,:,::-1]))
            
        # Setup the source and subject information.
        request.source='UNKNOWN_SOURCE'
        request.subject_id='UNKNOWN_SUBJECT'
        if source is not None:
            request.source=source
        if subject_id is not None:
            request.subject_id=subject_id

        
        request.detect_options.best=best
        
        if threshold == None:
            request.detect_options.threshold = self.info.detection_threshold
        else: 
            request.detect_options.threshold = float(threshold)
            
        if run_async == False:
            face_records = self.detect_stub.detect(request,None)
        elif run_async == True:
            self.waitOnResults()
            face_records = self.detect_stub.detect.future(request,None)
            self.running_async_jobs.append(face_records)
        else:
            raise ValueError("Unexpected run_async value: %s"%(run_async,))
                                
        return face_records
    
    def extract(self, im, face_records, run_async=False):
        request = fsd.ExtractRequest()
        print("DR INFO",dir(request))
        try:
            request.image.CopyFrom( pt.image_np2proto(im))
        except:
            request.image.CopyFrom( pt.image_np2proto(im.asOpenCV2()[:,:,::-1]))
            
        request.records.CopyFrom(face_records)
        
        if run_async == False:
            face_records = self.rec_stub.extract(request,None)
        elif run_async == True:
            self.waitOnResults()
            face_records = self.rec_stub.extract.future(request,None)
            self.running_async_jobs.append(face_records)
        else:
            raise ValueError("Unexpected run_async value: %s"%(run_async,))
        
        return face_records

    def detectExtract(self,im,best=False,threshold=None,min_size=None, run_async=False,source=None,subject_id=None):
        request = fsd.DetectExtractRequest()

        try:
            request.image.CopyFrom( pt.image_np2proto(im))
        except:
            request.image.CopyFrom( pt.image_np2proto(im.asOpenCV2()[:,:,::-1]))

        # Setup the source and subject information.
        request.source='UNKNOWN_SOURCE'
        request.subject_id='UNKNOWN_SUBJECT'
        if source is not None:
            request.source=source
        if subject_id is not None:
            request.subject_id=subject_id
            
            
        request.detect_options.best=best
        
        if threshold == None:
            request.detect_options.threshold = self.info.detection_threshold
        else: 
            request.detect_options.threshold = float(threshold)
            
        if run_async == False:
            face_records = self.detect_stub.detectExtract(request,None)
        elif run_async == True:
            self.waitOnResults()
            face_records = self.detect_stub.detectExtract.future(request,None)
            self.running_async_jobs.append(face_records)
        else:
            raise ValueError("Unexpected run_async value: %s"%(run_async,))
                                
        return face_records
    
    def enroll(self,faces,gallery_name, subject_id=None, subject_name=None, run_async=False,**kwargs):
        request = fsd.EnrollRequest()
        
        #print( "enrolling:",gallery_name,subject_id,subject_name)
        
        request.gallery_name = gallery_name
        
        if subject_id is not None:
            for face in faces.face_records:
                face.subject_id = subject_id
        
        if subject_name is not None:
            for face in faces.face_records:
                face.name = subject_name
                
        request.records.CopyFrom(faces)
    
        if run_async == False:
            error = self.rec_stub.enroll(request,None)
        elif run_async == True:
            self.waitOnResults()
            error = self.rec_stub.enroll.future(request,None)
            self.running_async_jobs.append(error)
        else:
            raise ValueError("Unexpected run_async value: %s"%(run_async,))

        return error
        

    def search(self, faces, gallery_name, max_results=3, threshold=None, run_async=False,**kwargs):
        request = fsd.SearchRequest()
        
        #print( "enrolling:",gallery_name,subject_id,subject_name)
        request.probes.CopyFrom(faces)
        request.gallery_name = gallery_name
        request.max_results=max_results
        
        if threshold is not None:
            request.threshold=threshold
            
        if run_async == False:
            error = self.rec_stub.search(request,None)
        elif run_async == True:
            self.waitOnResults()
            error = self.rec_stub.search.future(request,None)
            self.running_async_jobs.append(error)
        else:
            raise ValueError("Unexpected run_async value: %s"%(run_async,))

        return error
        

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
            
        #self.detect_threshold = status_message.detect_threshold
        self.match_threshold = status_message.match_threshold
            
        return status_message.status == fsd.READY, status_message
        


