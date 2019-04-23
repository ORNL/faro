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

from __future__ import print_function
from __future__ import division

import faro
#import dlib
import os
import faro.proto.proto_types as pt 
import faro.proto.face_service_pb2 as fsd
import numpy as np
import pyvision as pv
import time
import multiprocessing
#from _thread import _local
import cv2

import sys

#dlib = None

MYNET=None
WORKER_INDEX=None
GPU_ID = None
NMS_THRESH = 0.15
OPTIONS = None

NETS = {'vgg16': ('VGG16',
          os.path.join(os.path.dirname(__file__),'..','models','face_vgg16_faster_rcnn.caffemodel'))}

DEFAULT_PROTO = os.path.dirname(__file__),'..','models','test.prototxt'
DEFAULT_NET   = 'vgg16'

def chopImage(im,scale=0,levels=0,overlap=0.2):
    # pyrdown = dlib.pyramid_down()
    tot_scale = 1.0
    pyrdown = cv2.pyrDown
    for each in range(scale):
        #im = skimage.transform.pyramid_reduce(im,multichannel=True)
        im = pyrdown(im)
        tot_scale *= 2
        
    h,w,c = im.shape

    # Compute the final scale for the images.
    s = (1.+overlap)/(2.**levels)
    
    # Compute the image with and height
    tw = int(s*w)
    th = int(s*h)
    
    batch = []
    trans = []
    div = 2**levels
    while True:
        if tw < im.shape[1]:
            h,w,_ = im.shape
            x_gate = (w-tw)/(div-1)
            y_gate = (h-th)/(div-1)
            # print("multi_extract",im.shape,div,x_gate,y_gate,tw,th)
            for i in range(div):                
                for j in range(div):
                    x = int(j*x_gate)
                    y = int(i*y_gate)
                    tile = im[y:y+th,x:x+tw,:]
                    batch.append(tile)
                    trans.append( [tot_scale,x,y] )
                    # print(x,y,tile.shape)
                    
        else:
            # print("single_extract",im.shape)
            break
        im = pyrdown(im)
        tot_scale *= 2
        div //= 2
    
    
    #a = cv2.resize(im,(tw,th))
    batch.append(im)
    trans.append( [tot_scale,0,0] )
    
    return batch,trans



# TODO: RCNN uses twice the memory it probably should.

class RcnnFaceWorker(faro.FaceWorker):
    '''
    classdocs
    '''

    def __init__(self, options):
        '''
        Constructor
        '''
        
        from fast_rcnn.config import cfg
        from fast_rcnn.test import im_detect
        from fast_rcnn.nms_wrapper import nms
        import caffe
    
        print("Starting worker process:",multiprocessing.current_process())
        
        global MYNET,cfg,WORKER_INDEX,OPTIONS
        cfg.TEST.HAS_RPN = True  # Use RPN for proposals
        proc = multiprocessing.current_process()
        WORKER_INDEX = (int(proc.name.split('-')[-1])-1)%options.worker_count
    
        OPTIONS = options
        
        assert WORKER_INDEX >= 0
    
        prototxt = os.path.join(options.storage_dir,'models','test.prototxt')
        #'models/face/VGG16/faster_rcnn_end2end/test.prototxt'
        
        net_path = os.path.join(options.storage_dir,'models','face_vgg16_faster_rcnn.caffemodel')
        #caffemodel = NETS[options.net][1]
    
        if not os.path.isfile(net_path):
            raise IOError(('{:s} not found. Was the network downloaded to the {:s} directory?').format(net_path,options.storage_dir))
    
        if options.cpu_mode:
            print ("Setting CPU Mode")
            caffe.set_mode_cpu()
            caffe.set_multiprocess(True)
        else:
        #    GPU_ID = options.gpu_ids[WORKER_INDEX%len(options.gpu_ids)]
        #    cfg.GPU_ID = GPU_ID
        #    print ("Setting GPU:",GPU_ID)        
            caffe.set_mode_gpu()
        #    caffe.set_device(GPU_ID)
        print("Loading Network:",net_path)
        MYNET = caffe.Net(prototxt, net_path, caffe.TEST)
        
        print( "Worker Process Ready:",WORKER_INDEX,multiprocessing.current_process())
        #print(proc.ident,proc.name,proc.pid)
        sys.stdout.flush()
        sys.stderr.flush()

    def runNetwork(self, im, options):
        from fast_rcnn.config import cfg
        from fast_rcnn.test import im_detect
        from fast_rcnn.nms_wrapper import nms
        import caffe
    
        best=options.best
        thresh=options.threshold
        
        if best:
            thresh = 0.2
        
        scale_lvls = options.scale_levels
        scan_lvls = options.scan_levels
        scan_over = options.scan_overlap
        
        if scan_over < 0.0 or scan_over > 1.0:
            print( "Warning: 'scan_overlap' is not properly set. It should be in range [0.0 to 1.0].")
            scan_over = 0.2
            
        assert scale_lvls >= 0
        assert scan_lvls >= 0
    
        global MYNET,NMS_THRESH

        assert MYNET is not None
        assert OPTIONS is not None
        #print('im_shape', im.shape )
        
        batch,trans = chopImage(im,scale_lvls,scan_lvls,scan_over)
        results = []
        
        #print(len(trans))
        assert len(trans) == len(batch)
        for tile,ttt in zip(batch,trans):
            scores, boxes = im_detect(MYNET, tile)
        
            #print('level',tile.shape)

            cls_ind = 1
            cls_boxes = boxes[:, 4*cls_ind:4*(cls_ind + 1)]
            cls_scores = scores[:, cls_ind]
            dets = np.hstack((cls_boxes,
                    cls_scores[:, np.newaxis])).astype(np.float32)
            keep = nms(dets, NMS_THRESH)
            dets = dets[keep, :]
            # print (dets[:,4])
            keep = np.where(dets[:, 4] >= thresh)
            dets = dets[keep]
            
            #print (dets)
            dets[:,0] = ttt[0]*(dets[:,0]+ttt[1])
            dets[:,1] = ttt[0]*(dets[:,1]+ttt[2])
            dets[:,2] = ttt[0]*(dets[:,2]+ttt[1])
            dets[:,3] = ttt[0]*(dets[:,3]+ttt[2])
            results = results+list(dets)
        
        dets = np.array(results,dtype=np.float32)
        dets = dets.reshape(-1,5) # Handle empty arrays properly
        
        keep = nms(dets, NMS_THRESH)
        dets = dets[keep, :]
        # print (dets[:,4])
        if best:
            thresh = dets[:,4].max()
            
        keep = np.where(dets[:, 4] >= thresh)
        dets = dets[keep]
        #print("run",dets,keep)
        #sys.stdout.flush()
        return dets

        
    def detect(self,img,face_records,options):
        '''Run a face detector and return rectangles.'''
        
        # Load the model
        mat = img
        #print('options<',options,'>')
        #thresh = options.threshold

        #result_id = 0

        #im = mat #cv2.imread(pathname)
        timer = pv.Timer()
        
        
        # Run the network in the worker processes...
        dets = self.runNetwork(mat,options)
        
        #dets = as_result.get()

        dets[:, 2] = dets[:, 2] - dets[:, 0] + 1
        dets[:, 3] = dets[:, 3] - dets[:, 1] + 1
        timer.mark("End Detection")

        #print('dets')
        # Now process each face we found and add a face to the records list.
        for k, d in enumerate(dets):
            face_record = face_records.face_records.add()
            face_record.detection.score = d[4]
            face_record.detection.location.CopyFrom(pt.rect_val2proto(d[0], d[1], d[2], d[3]))
            face_record.detection.detection_id = k
            face_record.detection.detection_class = "FACE"

        if options.best:
            face_records.face_records.sort(key = lambda x: -x.detection.score)
            while len(face_records.face_records) > 1:
                del face_records.face_records[-1]
                
            

            
    def locate(self,img,face_records,options):
        '''Locate facial features.'''
        
        raise NotImplementedError()
        
    def align(self,image,face_records):
        '''Align the images to a standard size and orientation to allow 
        recognition.'''
        raise NotImplementedError()
            
    def extract(self,img,face_records):
        '''Extract a template that allows the face to be matched.'''
        # Compute the 128D vector that describes the face in img identified by
        # shape.  In general, if two face descriptor vectors have a Euclidean
        # distance between them less than 0.6 then they are from the same
        # person, otherwise they are from different people. Here we just print
        # the vector to the screen.
        
        # TODO: Make this an option
        raise NotImplementedError()
        
        
    def scoreType(self):
        '''Return the method used to create a score from the template.
        
        By default server computation is required.
        
        SCORE_L1, SCORE_L2, SCORE_DOT, SCORE_SERVER
        '''
        return fsd.L2
    
    def status(self):
        '''Return a simple status message.'''
        #print("Handeling status request.")
        status_message = fsd.FaceServiceInfo()
        status_message.status = fsd.READY
        status_message.detection_support = True
        status_message.extract_support = True
        status_message.score_support = True
        status_message.score_type = self.scoreType()
        status_message.detection_threshold = self.recommendedDetectionThreshold();
        status_message.match_threshold = self.recommendedScoreThreshold();
        status_message.algorithm = "RCNN_%s"%('1.0.0',);

        
        return status_message
        

    def recommendedDetectionThreshold(self):
        '''Return the method used to create a score from the template.
        
        By default server computation is required.
        
        Should return a recommended detection threshold.
        
        DLIB recommends a value of 0.0 for LFW dataset    
        '''
        
        return 0.90

    def recommendedScoreThreshold(self,far=-1):
        '''Return the method used to create a score from the template.
        
        By default server computation is required.
        
        Should return a recommended score threshold.
        
        DLIB recommends a value of 0.6 for LFW dataset    
        '''
        
        return 0.60


