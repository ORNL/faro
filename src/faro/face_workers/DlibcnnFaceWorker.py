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

Created on Feb 6, 2019

@author: bolme
'''
import faro
#import dlib
import os
import faro.proto.proto_types as pt 
import faro.proto.face_service_pb2 as fsd
import numpy as np
import faro.pyvision as pv
import time
#from _thread import _local

dlib = None


class DlibcnnFaceWorker(faro.FaceWorker):
    '''
    classdocs
    '''

    def __init__(self, options):
        '''
        Constructor
        '''
        global dlib
        import dlib as _local_dlib       
        dlib = _local_dlib

        
        self.detector = dlib.cnn_face_detection_model_v1(os.path.join(options.storage_dir, 'models', "mmod_human_face_detector.dat"))

        self.shape_pred = dlib.shape_predictor(os.path.join(options.storage_dir,'models',"shape_predictor_68_face_landmarks.dat"))
        
        # This may run on the GPU.
        self.face_rec = dlib.face_recognition_model_v1(os.path.join(options.storage_dir,'models',"dlib_face_recognition_resnet_model_v1.dat"))

        print("DLIB Models Loaded.")

        
    def detect(self,img,face_records,options):
        '''Run a face detector and return rectangles.'''
        
        detection_threshold = options.threshold 
        print('Detection Threshold', detection_threshold)       
        # TODO: Make this an option
        if options.best:
            detection_threshold = -1.5
        
        # Run the detector on the image
        dets = self.detector(img, 1)

        # Now process each face we found and add a face to the records list.
        for k, d in enumerate(dets):
            face_record = face_records.face_records.add()
            face_record.detection.score = d.confidence
            face_record.detection.location.CopyFrom(pt.rect_val2proto(d.rect.left(), d.rect.top(), d.rect.width(), d.rect.height()))
            face_record.detection.detection_id = k
            face_record.detection.detection_class = "FACE_%d"%k
            shape = self.shape_pred(img, d.rect)
            for i in range(len(shape.parts())):
                loc = shape.parts()[i]
                landmark = face_record.landmarks.add()
                landmark.landmark_id = "point_%02d"%i
                landmark.location.x = loc.x
                landmark.location.y = loc.y

        if options.best:
            face_records.face_records.sort(key = lambda x: -x.detection.score)
            while len(face_records.face_records) > 1:
                del face_records.face_records[-1]
            

            
    def locate(self,img,face_records,options):
        '''Locate facial features.'''
            # Get the landmarks/parts for the face in box d.
        print('locate')
        for face_record in face_records.face_records:
            rect = pt.rect_proto2pv(face_record.detection.location)
            x,y,w,h = rect.asTuple()
            l,t,r,b = [int(tmp) for tmp in [x,y,x+w,y+h]]
            d = dlib.rectangle(l,t,r,b)
            shape = self.shape_pred(img, d)
            print('s',shape)
        
        
    def align(self,image,face_records):
        '''Align the images to a standard size and orientation to allow 
        recognition.'''
        pass # Not needed for this algorithm.
            
    def extract(self,img,face_records):
        '''Extract a template that allows the face to be matched.'''
        # Compute the 128D vector that describes the face in img identified by
        # shape.  In general, if two face descriptor vectors have a Euclidean
        # distance between them less than 0.6 then they are from the same
        # person, otherwise they are from different people. Here we just print
        # the vector to the screen.
        
        # TODO: Make this an option
        JITTER_COUNT = 5
        
        for face_record in face_records.face_records:
            rect = pt.rect_proto2pv(face_record.detection.location)
            x,y,w,h = rect.asTuple()

            # Extract view
            rect = pv.Rect()
            cx,cy = x+0.5*w,y+0.5*h
            tmp = 1.5*max(w,h)
            cw,ch = tmp,tmp
            crop = pv.AffineFromRect(pv.CenteredRect(cx,cy,cw,ch),(256,256))
            #print (x,y,w,h,cx,cy,cw,ch,crop)
            pvim = pv.Image(img[:,:,::-1]) # convert rgb to bgr
            pvim = crop(pvim)
            view = pt.image_pv2proto(pvim)
            face_record.view.CopyFrom(view)
            
            # Extract landmarks
            l,t,r,b = [int(tmp) for tmp in [x,y,x+w,y+h]]
            d = dlib.rectangle(l,t,r,b)
            shape = self.shape_pred(img, d)
            #print('s',dir(shape))
            #print(shape.parts()[0])
            

            #print('shape:',face_records.face_records[0].landmarks)
            face_descriptor = self.face_rec.compute_face_descriptor(img, shape, JITTER_COUNT)
            face_descriptor = np.array(face_descriptor)
            
            vec = face_descriptor.flatten()
            face_record.template.data.CopyFrom(pt.vector_np2proto(vec))

        # It should also be noted that you can also call this function like this:
        #  face_descriptor = facerec.compute_face_descriptor(img, shape, 100)
        # The version of the call without the 100 gets 99.13% accuracy on LFW
        # while the version with 100 gets 99.38%.  However, the 100 makes the
        # call 100x slower to execute, so choose whatever version you like.  To
        # explain a little, the 3rd argument tells the code how many times to
        # jitter/resample the image.  When you set it to 100 it executes the
        # face descriptor extraction 100 times on slightly modified versions of
        # the face and returns the average result.  You could also pick a more
        # middle value, such as 10, which is only 10x slower but still gets an
        # LFW accuracy of 99.3%.
        
        
    def scoreType(self):
        '''Return the method used to create a score from the template.
        
        By default server computation is required.
        
        SCORE_L1, SCORE_L2, SCORE_DOT, SCORE_SERVER
        '''
        return fsd.L2
    
    def status(self):
        '''Return a simple status message.'''
        print("Handeling status request.")
        status_message = fsd.FaceServiceInfo()
        status_message.status = fsd.READY
        status_message.detection_support = True
        status_message.extract_support = True
        status_message.score_support = True
        status_message.score_type = self.scoreType()
        status_message.detection_threshold = self.recommendedDetectionThreshold();
        status_message.match_threshold = self.recommendedScoreThreshold();
        status_message.algorithm = "DLIB_%s"%(dlib.__version__);

        
        return status_message
        

    def recommendedDetectionThreshold(self):
        '''Return the method used to create a score from the template.
        
        By default server computation is required.
        
        Should return a recommended detection threshold.
        
        DLIB recommends a value of 0.0 for LFW dataset    
        '''
        
        return 0.0

    def recommendedScoreThreshold(self,far=-1):
        '''Return the method used to create a score from the template.
        
        By default server computation is required.
        
        Should return a recommended score threshold.
        
        DLIB recommends a value of 0.6 for LFW dataset    
        '''
        
        return 0.60


