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

Created on Feb 6, 2019

@author: bolme
'''
import faro
import os
import faro.proto.proto_types as pt 
import faro.proto.face_service_pb2 as fsd
import numpy as np
import pyvision as pv
#from keras_vggface.vggface import VGGFace
#import keras
#import tensorflow as tf
#import numpy as np
#from keras.preprocessing import image

 
# delayed keras load
keras = None
K = None
dlib = None
 

THRESH_100    = -0.31607726
THRESH_1000   = -0.42838144
THRESH_10000  = -0.5218667
THRESH_100000 = -0.6301167

class VggFaceWorker(faro.FaceWorker):
    '''
    classdocs
    '''

    def __init__(self, options):
        '''
        Constructor
        '''        
        global keras
        global K
        global dlib
        keras, K = faro.loadKeras()
        
        from keras_vggface.vggface import VGGFace

        global dlib
        import dlib as _local_dlib       
        dlib = _local_dlib

        self.detector = dlib.get_frontal_face_detector()


        self.shape_pred = dlib.shape_predictor(os.path.join(options.storage_dir,'models',"shape_predictor_5_face_landmarks.dat"))
        
        # This may run on the GPU.
        self.face_rec = dlib.face_recognition_model_v1(os.path.join(options.storage_dir,'models',"dlib_face_recognition_resnet_model_v1.dat"))

        #self.detector = dlib.get_frontal_face_detector()
        #self.shape_pred = dlib.shape_predictor(os.path.join(options.storage_dir,"shape_predictor_5_face_landmarks.dat"))
        #self.face_rec = dlib.face_recognition_model_v1(os.path.join(options.storage_dir,"dlib_face_recognition_resnet_model_v1.dat"))

        model = VGGFace(model='resnet50')
            
        # This line of code works with the VGGFace resnet50
        layer = model.layers[-2]
        
        out = layer.output
                
        self.recognizer = keras.Model(model.input,out)
        #self.recognizer = load_model(model_path)
        self.recognizer._make_predict_function()

        import tensorflow as tf
        self.graph = tf.get_default_graph()

        print("VGG Models Loaded.")

        
    def detect(self,img,face_records,options):
        '''Run a face detector and return rectangles.'''
        
        # TODO: Make this an option
        detection_threshold = options.threshold
        if options.best:
            detection_threshold = -1.5
        
        # Run the detector on the image
        dets, scores, idx = self.detector.run(img, 1, detection_threshold)


        # Now process each face we found and add a face to the records list.
        for k, d in enumerate(dets):
            face_record = face_records.face_records.add()
            face_record.detection.score = scores[k]
            face_record.detection.location.CopyFrom(pt.rect_val2proto(d.left(), d.top(), d.width(), d.height()))
            face_record.detection.detection_id = k
            face_record.detection.detection_class = "FACE_%d"%idx[k]

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
        
        im = pv.Image(img[:,:,::-1])
                
        for face_record in face_records.face_records:
            rect = pt.rect_proto2pv(face_record.detection.location)
            x,y,w,h = rect.asTuple()

            # Extract view
            rect = pv.Rect()
            cx,cy = x+0.5*w,y+0.5*h
            tmp = 1.5*max(w,h)
            cw,ch = tmp,tmp
            crop = pv.AffineFromRect(pv.CenteredRect(cx,cy,cw,ch),(256,256))

            pvim = pv.Image(img[:,:,::-1]) # convert rgb to bgr
            pvim = crop(pvim)
            view = pt.image_pv2proto(pvim)
            face_record.view.CopyFrom(view)
            
            # Extract landmarks
            l,t,r,b = [int(tmp) for tmp in [x,y,x+w,y+h]]
            d = dlib.rectangle(l,t,r,b)
            shape = self.shape_pred(img, d)

            
            for i in range(len(shape.parts())):
                loc = shape.parts()[i]
                landmark = face_record.landmarks.add()
                landmark.landmark_id = "point_%02d"%i
                landmark.location.x = loc.x
                landmark.location.y = loc.y
            
            
            # Get detection rectangle and crop the face
            #rect = pt.rect_proto2pv(face_record.detection.location).rescale(1.5)
            #tile = im.crop(rect)
            tile = pvim.resize((224,224))
        
            #tile.show(delay=1000)
        
            face_im = tile.asOpenCV2()
            face_im = face_im[:,:,::-1] # Convert BGR to RGB
            #mat_ = cv2.cvtColor(mat,cv2.COLOR_RGB2GRAY)
            #mat = cv2.cvtColor(mat_,cv2.COLOR_GRAY2RGB)

            #img = image.load_img('../image/ajb.jpg', target_size=(224, 224))
        
            from keras_vggface import utils
            from keras.preprocessing import image

            face_im = image.img_to_array(face_im)
            face_im = np.expand_dims(face_im, axis=0)
            face_im = utils.preprocess_input(face_im, version=2) # or version=2

            # Needed in multithreaded applications
            with self.graph.as_default():
                tmp = self.recognizer.predict(face_im)
                
            face_descriptor = pv.meanUnit(tmp.flatten())

            #print('shape:',face_records.face_records[0].landmarks)
            #face_descriptor = self.face_rec.compute_face_descriptor(img, shape, JITTER_COUNT)
            #face_descriptor = np.array(face_descriptor)
            
            #vec = face_descriptor.flatten()
            face_record.template.data.CopyFrom(pt.vector_np2proto(face_descriptor))

                
    def scoreType(self):
        '''Return the method used to create a score from the template.
        
        By default server computation is required.
        
        SCORE_L1, SCORE_L2, SCORE_DOT, SCORE_SERVER
        '''
        return fsd.NEG_DOT
    
    def status(self):
        '''Return a simple status message.'''
        print("Handeling status request.")
        status_message = fsd.FaceServiceInfo()
        status_message.status = fsd.READY
        status_message.detection_support = True
        status_message.extract_support = True
        status_message.score_support = True
        status_message.score_type = self.scoreType()
        status_message.detection_threshold = self.recommendedDetectionThreshold()
        status_message.match_threshold = self.recommendedScoreThreshold()
        status_message.algorithm = "VGG2_RESNET_1.0.0"

        
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
        
        return -0.42838144


