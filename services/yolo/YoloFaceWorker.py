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

from __future__ import print_function, division


# This requires libdarknet.so to be in the same directory as the YoloFaceWorker directory.
# This should support multiple Yolo models for different detection types.

# Getting Weights
# wget https://pjreddie.com/media/files/yolov3.weights
# wget https://pjreddie.com/media/files/yolov3-tiny.weights

import faro
#import dlib
import os
import faro.proto.proto_types as pt 
import faro.proto.face_service_pb2 as fsd
import numpy as np
import pyvision as pv
import time
#from _thread import _local

dlib = None

# Upgrading to python3 - DSB
# unicode strings need to be encode to ascii strings before
# going to ctypes calls: .encode('ascii')
# Byte arrays can be encoded to ascii like this: .decode("utf-8")

from ctypes import *
import ctypes
#import math
import random
#import sys
#import time

def sample(probs):
    s = sum(probs)
    probs = [a/s for a in probs]
    r = random.uniform(0, 1)
    for i in range(len(probs)):
        r = r - probs[i]
        if r <= 0:
            return i
    return len(probs)-1

def c_array(ctype, values):
    arr = (ctype*len(values))()
    arr[:] = values
    return arr

class BOX(Structure):
    _fields_ = [("x", c_float),
                ("y", c_float),
                ("w", c_float),
                ("h", c_float)]

class DETECTION(Structure):
    _fields_ = [("bbox", BOX),
                ("classes", c_int),
                ("prob", POINTER(c_float)),
                ("mask", POINTER(c_float)),
                ("objectness", c_float),
                ("sort_class", c_int)]


class IMAGE(Structure):
    _fields_ = [("w", c_int),
                ("h", c_int),
                ("c", c_int),
                ("data", POINTER(c_float))]

class METADATA(Structure):
    _fields_ = [("classes", c_int),
                ("names", POINTER(c_char_p))]

    


    
MODELS = {
    'yolov3-coco':      ('yolov3.cfg',                'yolov3.weights',                      'coco.data',             0.2, 0.0, 0.4),
    'yolov3-spp-coco':      ('yolov3-spp.cfg',                'yolov3-spp.weights',          'coco.data',         0.2, 0.0, 0.4),
    'yolov3-tiny-coco': ('yolov3-tiny.cfg',           'yolov3-tiny.weights',                 'coco.data',             0.2, 0.0, 0.4),
    'azface':           ('tiny-yolo-azface-fddb.cfg', 'tiny-yolo-azface-fddb_82000.weights', 'azface.data',       0.2, 0.0, 0.4), # https://github.com/azmathmoosa/azFace
    'yolov3-wider':     ('yolov3-wider.cfg',          'yolov3-wider_16000.weights',          'yolov3-wider.data', 0.2, 0.0, 0.4), # https://github.com/sthanhng/yoloface
    # poor performance 'yolo-face':     ('yolo-face.cfg',             'yolo-face_final.weights',             'azface.data', 0.35, 0.35, 0.25), # https://github.com/dannyblueliu/YOLO-Face-detection
    }
    
# Here are some darknet or yolo face related options
# https://github.com/dannyblueliu/YOLO-Face-detection
# https://github.com/sthanhng/yoloface
# https://github.com/abars/YoloKerasFaceDetection
# https://github.com/iitzco/faced
# https://github.com/azmathmoosa/azFace
# https://github.com/lincolnhard/facenet-darknet-inference
# https://github.com/initialz/darknet-yolo-face-detection
# https://github.com/xhuvom/darknetFaceID



def getOptionsGroup(parser):
    model_options = parser.add_option_group("Options for YOLO (darknet).")
    model_options.add_option( "--yolo-model", type="choice", dest="yolo_model", default='yolov3-wider',
                              choices=list(MODELS.keys()),
                      help="Select Yolo model: %s"%(", ".join(MODELS.keys()),))


class YoloFaceWorker(faro.FaceWorker):
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

        self.lib = CDLL("libdarknet.so", RTLD_GLOBAL)
        self.lib.network_width.argtypes = [c_void_p]
        self.lib.network_width.restype = c_int
        self.lib.network_height.argtypes = [c_void_p]
        self.lib.network_height.restype = c_int
        
        predict = self.lib.network_predict
        predict.argtypes = [c_void_p, POINTER(c_float)]
        predict.restype = POINTER(c_float)
        
        set_gpu = self.lib.cuda_set_device
        set_gpu.argtypes = [c_int]
        
        make_image = self.lib.make_image
        make_image.argtypes = [c_int, c_int, c_int]
        make_image.restype = IMAGE
        
        self.get_network_boxes = self.lib.get_network_boxes
        self.get_network_boxes.argtypes = [c_void_p, c_int, c_int, c_float, c_float, POINTER(c_int), c_int, POINTER(c_int)]
        self.get_network_boxes.restype = POINTER(DETECTION)
        
        make_network_boxes = self.lib.make_network_boxes
        make_network_boxes.argtypes = [c_void_p]
        make_network_boxes.restype = POINTER(DETECTION)
        
        self.free_detections = self.lib.free_detections
        self.free_detections.argtypes = [POINTER(DETECTION), c_int]
        
        free_ptrs = self.lib.free_ptrs
        free_ptrs.argtypes = [POINTER(c_void_p), c_int]
        
        network_predict = self.lib.network_predict
        network_predict.argtypes = [c_void_p, POINTER(c_float)]
        
        reset_rnn = self.lib.reset_rnn
        reset_rnn.argtypes = [c_void_p]
        
        load_net = self.lib.load_network
        load_net.argtypes = [c_char_p, c_char_p, c_int]
        load_net.restype = c_void_p
        
        self.do_nms_obj = self.lib.do_nms_obj
        self.do_nms_obj.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]
        
        do_nms_sort = self.lib.do_nms_sort
        do_nms_sort.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]
        
        self.free_image = self.lib.free_image
        self.free_image.argtypes = [IMAGE]
        
        letterbox_image = self.lib.letterbox_image
        letterbox_image.argtypes = [IMAGE, c_int, c_int]
        letterbox_image.restype = IMAGE
        
        load_meta = self.lib.get_metadata
        self.lib.get_metadata.argtypes = [c_char_p]
        self.lib.get_metadata.restype = METADATA
        
        self.load_image = self.lib.load_image_color
        self.load_image.argtypes = [c_char_p, c_int, c_int]
        self.load_image.restype = IMAGE
        
        rgbgr_image = self.lib.rgbgr_image
        rgbgr_image.argtypes = [IMAGE]
        
        self.predict_image = self.lib.network_predict_image
        self.predict_image.argtypes = [c_void_p, IMAGE]
        self.predict_image.restype = POINTER(c_float)

        # Load the model and other data
        model_data = MODELS[options.yolo_model]
        yolo_cfg = os.path.join('models',model_data[0])
        yolo_weights = os.path.join('models',model_data[1])
        yolo_data = os.path.join('models',model_data[2])
        self.t1 = model_data[3]
        self.t2 = model_data[4]
        self.t_nms = model_data[5]
        self.net = load_net(yolo_cfg.encode('ascii'), yolo_weights.encode('ascii'), 0)
        self.meta = load_meta(yolo_data.encode('ascii'))

        print("YOLO Models Loaded.",self.t1,self.t2,self.t_nms)

        
    def detect(self,img,face_records,options):
        '''Run a face detector and return rectangles.'''
        
        # TODO: Make this an option
        detection_threshold = options.threshold
        if options.best:
            detection_threshold = 0.01
        
        
        #thresh=.5
        #hier_thresh=.5
        #nms=.45

        thresh=self.t1
        hier_thresh=self.t2
        #nms=self.t_nms
        
        start = time.time()
        
        # Reformat the image for darknet
        img = (img/255.0).astype(np.float32)
        img = np.transpose(img,(2,0,1)).copy()
        
        c,h,w = img.shape
        
        im = IMAGE(w,h,c,img.ctypes.data_as(ctypes.POINTER(ctypes.c_float)))
        
        num = c_int(0)
        pnum = pointer(num)
        self.predict_image(self.net, im)
        dets = self.get_network_boxes(self.net, im.w, im.h, thresh, hier_thresh, None, 0, pnum)
        num = pnum[0]
        if (detection_threshold > 0.0): self.do_nms_obj(dets, num, self.meta.classes, detection_threshold);

        # print('time checkBB:',time.time()-start)
    
        res = []
        for j in range(num):
            for i in range(self.meta.classes):
                if dets[j].prob[i] > 0:
                    b = dets[j].bbox
                    res.append((self.meta.names[i], dets[j].prob[i], (b.x, b.y, b.w, b.h)))
        res = sorted(res, key=lambda x: -x[1])
        
        #self.free_image(im)
        self.free_detections(dets, num)
                
        k = 0
        for each in res:
            name,prob,rect = each

            face_record = face_records.face_records.add()
            face_record.detection.score = prob
            face_record.detection.location.CopyFrom(pt.rect_val2proto(rect[0]-0.5*rect[2],rect[1]-0.5*rect[3],rect[2],rect[3]))
            face_record.detection.detection_id = k
            face_record.detection.detection_class = name
            k += 1

        
        return                

            
    def locate(self,img,face_records,options):
        '''Locate facial features.'''

        return
        
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
        
        return
        
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
        status_message.extract_support = False
        status_message.score_support = False
        status_message.score_type = self.scoreType()
        status_message.detection_threshold = self.recommendedDetectionThreshold();
        status_message.match_threshold = self.recommendedScoreThreshold();
        status_message.algorithm = "YOLO_%s"%("2018.09.14");

        
        return status_message
        

    def recommendedDetectionThreshold(self):
        '''Return the method used to create a score from the template.
        
        By default server computation is required.
        
        Should return a recommended detection threshold.
        
        DLIB recommends a value of 0.0 for LFW dataset    
        '''
        
        return 0.2

    def recommendedScoreThreshold(self,far=-1):
        '''Return the method used to create a score from the template.
        
        By default server computation is required.
        
        Should return a recommended score threshold.
        
        DLIB recommends a value of 0.6 for LFW dataset    
        '''
        
        return 0.0


