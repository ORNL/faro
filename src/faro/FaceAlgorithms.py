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

Created on Jul 23, 2018

@author: bolme
'''

#from keras_vggface.vggface import VGGFace
import dlib
import faro.pyvision as pv
import faro.proto.face_service_pb2 as fsd
#import geometry_pb2 as geo
#from face_service_pb2 import DetectionList
#def createRect():
#import keras
import numpy as np
import time
import faro.proto.proto_types as pt
from symbol import tfpdef
#import cv2

#import tensorflow as tf
# A placeholder for tensorflow
tf = None
keras = None

# Initial results and thresholds
# EER 0.0194114416885
# 1/100: ROCPoint 0.065492 FRR at 0.001000 FAR 0.42838144
# 1/1000: ROCPoint 0.024156 FRR at 0.010000 FAR 0.31607726
# 1/10000: ROCPoint 0.181287 FRR at 0.000100 FAR 0.5218667
# 1/100000: ROCPoint 0.474067 FRR at 0.000010 FAR 0.6301167

# 2019/09/28 Changed normalization and detection rect
# EER 0.014641541138080012
# 1/100: ROCPoint 0.016276 FRR at 0.010000 FAR 0.26578113
# 1/1000: ROCPoint 0.031739 FRR at 0.001000 FAR 0.38091332
# 1/10000: ROCPoint 0.082611 FRR at 0.000100 FAR 0.4815168
# 1/100000: ROCPoint 0.342000 FRR at 0.000010 FAR 0.61786556


THRESH_100    = 0.31607726
THRESH_1000   = 0.42838144
THRESH_10000  = 0.5218667
THRESH_100000 = 0.6301167

class FaceAlgorithms(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        
        self.detector = dlib.get_frontal_face_detector()
        
        model = VGGFace(model='resnet50')
            
        # This line of code works with the VGGFace resnet50
        layer = model.layers[-2]
        
        out = layer.output
                
        self.recognizer = keras.Model(model.input,out)
        #self.recognizer = load_model(model_path)
        self.recognizer._make_predict_function()
        self.graph = tf.get_default_graph()
    
    def detect(self,im,options=None):
        
        #print options 
        mat = im
        
        threshold = 0.0
        upsample = 1
        
        if options != None and options.best == True:
            #print "Running in best mode."
            threshold = -2.0
            
        if isinstance(im, pv.Image):
            mat = im.asOpenCV2()
            mat = mat[:,:,::-1]
        elif mat.shape[2] == 1:
            mat = mat[:,:,0]

        start_time = time.time()

        detections, scores, indexes = self.detector.run(mat, upsample, threshold)
        
        if options != None and options.best == True and len(scores) < 1:
            result = fsd.DetectionList()
            det = result.detections.add().CopyFrom(pt.detection_val2proto(-1000000, 0, 0, im.width,im.height))
            return result
        
        stop_time = time.time()
        
        #print "Scores:", scores
        
        detect_list = list(zip(scores,detections))
        detect_list.sort(key=lambda x: x[0],reverse=True)
        
        #print "Detections:",len(detect_list)
        #print "Detect Time:",stop_time-start_time
        

        result = fsd.DetectionList()
        
        if options != None and options.best == True:
            s,r = detect_list[0]
            det = result.detections.add().CopyFrom(pt.detection_val2proto(s, r.left(), r.top(), r.width(),r.height()))
        else:
            for s,r in detect_list:
                det = result.detections.add().CopyFrom(pt.detection_val2proto(s, r.left(), r.top(), r.width(),r.height()))
        
        return result
    
    def extract(self,im,detection):
        #import numpy as np
        from keras.preprocessing import image
        #from keras_vggface.vggface import VGGFace
        from keras_vggface import utils

        rect = pt.rect_proto2pv(detection.location).rescale(1.5)
        tile = im.crop(rect)
        tile = tile.resize((224,224))
        
        #tile.show(delay=1000)
        
        img = tile.asOpenCV2()
        img = img[:,:,::-1] # Convert BGR to RGB
        #mat_ = cv2.cvtColor(mat,cv2.COLOR_RGB2GRAY)
        #mat = cv2.cvtColor(mat_,cv2.COLOR_GRAY2RGB)

        #img = image.load_img('../image/ajb.jpg', target_size=(224, 224))
        img = image.img_to_array(img)
        img = np.expand_dims(img, axis=0)
        img = utils.preprocess_input(img, version=1) # or version=2
        #preds = model.predict(x)
        #print('Predicted:', utils.decode_predictions(preds))

        #mat = mat[:,:,::-1]
 
        
        #mat.shape = (1,224,224,3)
        
        # Needed in multithreaded applications
        with self.graph.as_default():
            tmp = self.recognizer.predict(img)
        
                
        return pv.meanUnit(tmp.flatten())
    
    def extractTile(self,im):
        import sys
        #import numpy as np
        from keras.preprocessing import image
        #from keras_vggface.vggface import VGGFace
        from keras_vggface import utils

        assert im.shape == (224,224,3)
        #tile = tile.resize((224,224))
        
        #tile.show(delay=1000)
        
        img = im
        #img = img[:,:,::-1] # Convert BGR to RGB
        #mat_ = cv2.cvtColor(mat,cv2.COLOR_RGB2GRAY)
        #mat = cv2.cvtColor(mat_,cv2.COLOR_GRAY2RGB)

        #img = image.load_img('../image/ajb.jpg', target_size=(224, 224))
        img = image.img_to_array(img)
        img = np.expand_dims(img, axis=0)
        img = utils.preprocess_input(img, version=1) # or version=2
        #preds = model.predict(x)
        #print('Predicted:', utils.decode_predictions(preds))

        #mat = mat[:,:,::-1]
 
        
        #mat.shape = (1,224,224,3)
        
        # Needed in multithreaded applications
        with self.graph.as_default():
            tmp = self.recognizer.predict(img)
        
                
        temp = pv.meanUnit(tmp.flatten())
    
        
        return temp
    
    def verify(self, temp1, temp2):
        score = (temp1*temp2).sum()
        
        return score
    
    def matrix(self, gallery1, gallery2):
        return np.dot(gallery1,gallery2.T)
    
    
    
