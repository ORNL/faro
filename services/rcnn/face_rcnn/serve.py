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
'''
from __future__ import print_function, division

import os   
# Reduces all the crap that caffe dumps out 
os.environ['GLOG_minloglevel'] = '2' 

from utils.timer import Timer
import matplotlib.pyplot as plt
import numpy as np
import scipy.io as sio


import os, sys, cv2
import argparse
import sys
import pyvision as pv
import csv
import optparse
import faro.proto.proto_types as pt
from faro.proto.face_service_pb2 import DetectionRequest

import faro.proto.face_service_pb2_grpc as fs
import faro.proto.face_service_pb2 as fsd
import faro.proto.geometry_pb2 as geo
import grpc
from concurrent import futures
import time
import logging
import traceback
import multiprocessing
import socket
logging.basicConfig()
_ONE_DAY_IN_SECONDS = 60 * 60 * 24
_LOGGER = logging.getLogger(__name__)


import threading

mydata = threading.local()

NETS = {'vgg16': ('VGG16',
          os.path.join(os.path.dirname(__file__),'..','models','face_vgg16_faster_rcnn.caffemodel'))}

DEFAULT_PROTO = os.path.dirname(__file__),'..','models','test.prototxt'
DEFAULT_NET   = 'vgg16'
def parseOptions():
    '''
    Parse command line arguments.
    '''
    args = [] # Add the names of arguments here.
    n_args = len(args)
    args = " ".join(args)
    description = '''A service that runs the rcnn face detector.'''
    epilog = '''Created by David Bolme - bolmeds@ornl.gov'''
    
    version = "0.0.0"
    
    # Setup the parser
    parser = optparse.OptionParser(usage='%s [OPTIONS] %s'%(sys.argv[0],args),version=version,description=description,epilog=epilog)

    # Here are some templates for standard option formats.
    #parser.add_option("-q", "--quiet", action="store_false", dest="verbose", default=True,
    #                 help="Decrease the verbosity of the program")
    
    #parser.add_option("-b", "--bool", action="store_true", dest="my_bool", default=False,
    #                  help="don't print status messages to stdout")
    
    parser.add_option("--cpu", action="store_true", dest="cpu_mode", default=False,
                      help="Set the model to run on the cpu only.")
    
    #parser.add_option("-b", "--bool", action="store_true", dest="my_bool", default=False,
    #                  help="don't print status messages to stdout")
    
    #parser.add_option( "-c","--choice", type="choice", choices=['c1','c2','c3'], dest="my_choice", default="c1",
    #                  help="Choose an option.")

    #parser.add_option( "-f","--float", type="float", dest="my_float", default=0.0,
    #                  help="A floating point value.")

    #parser.add_option( "--gpu-memory", type="float", dest="gpu_memory", default=0.2,
    #                  help="GPU memory fraction. Default=0.2 ")

    #parser.add_option( "-i","--int", type="int", dest="my_int", default=0,
    #                  help="An integer value.")

    parser.add_option( "--gpus", type="string", dest="gpu_ids", default="0",
                      help="A comma seperated list of gpu ids.")

    parser.add_option( "--workers", type="int", dest="worker_count", default=1,
                      help="The number of worker processes to use.")

    #parser.add_option( "-s","--str", type="str", dest="my_str", default="default",
    #                  help="A string value.")

    parser.add_option( "--net", type="str", dest="net", default=DEFAULT_NET,
                      help="Select a network file. default=%s"%(DEFAULT_NET,))
    parser.add_option( "--proto", type="str", dest="proto", default=DEFAULT_PROTO,
                      help="Select a proto file. default=%s"%(DEFAULT_PROTO,))
    

    port = socket.gethostname() + ":50030"

    parser.add_option( "-p","--port", type="str", dest="port", default=port,
                      help="Service port.  Default=%s"%port)


    # Parse the arguments and return the results.
    (options, args) = parser.parse_args()
    
    if len(args) != n_args:
        parser.print_help()
        print
        print ("Please supply exactly %d arguments."%n_args)
        print
        exit(-1)
        
    options.gpu_ids = [int(x) for x in options.gpu_ids.split(',')]
    
    return options,args

# Global variables that are set and persisted in worker processes
MYNET=None
WORKER_INDEX=None
GPU_ID = None
NMS_THRESH = 0.15
OPTIONS = None

def processInit(options):
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

    prototxt = os.path.join(os.path.dirname(__file__),'..','models','test.prototxt')
    #'models/face/VGG16/faster_rcnn_end2end/test.prototxt'
    caffemodel = NETS[options.net][1]

    if not os.path.isfile(caffemodel):
        raise IOError(('{:s} not found.\nDid you run ./data/script/'
             'fetch_faster_rcnn_models.sh?').format(caffemodel))

    if options.cpu_mode:
        print ("Setting CPU Mode")
        caffe.set_mode_cpu()
        caffe.set_multiprocess(True)
    else:
        GPU_ID = options.gpu_ids[WORKER_INDEX%len(options.gpu_ids)]
        cfg.GPU_ID = GPU_ID
        print ("Setting GPU:",GPU_ID)        
        caffe.set_mode_gpu()
        caffe.set_device(GPU_ID)
    print("Loading Network:",caffemodel)
    MYNET = caffe.Net(prototxt, caffemodel, caffe.TEST)
    
    print( "Worker Process Ready:",WORKER_INDEX,multiprocessing.current_process(),"GPU_ID:",GPU_ID)
    #print(proc.ident,proc.name,proc.pid)
    sys.stdout.flush()
    sys.stderr.flush()
    
    
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
    #print(im.shape,tw,th)
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

    
def runNetwork(im,options):
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
    try:
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
        sys.stdout.flush()
        
        dets = np.array(results,dtype=np.float32)
        dets = dets.reshape(-1,5) # Handle empty arrays properly
        
        keep = nms(dets, NMS_THRESH)
        dets = dets[keep, :]
        # print (dets[:,4])
        if best:
            thresh = dets[:,4].max()
            
        keep = np.where(dets[:, 4] >= thresh)
        dets = dets[keep]

        return dets
    except:
        #print( "Error with detections.")
        traceback.print_exc()
        raise
    
        
class RCNNFaceDetector(fs.FaceRecognitionServicer):
    
    def __init__(self,options):
        self.options = options
        self.my_data = threading.local()
        print( "Creating a pool of processes." )
        assert options.worker_count > 0
        self.pool = multiprocessing.Pool(options.worker_count,processInit,[options])

    def detect(self,request,context):
        # TODO: we need to get rid of NMS
        #from fast_rcnn.nms_wrapper import nms

        try:

            # Load the model
            start = time.time()
            mat = pt.image_proto2np(request.image)
            thresh = request.options.threshold

            result_id = 0

            im = mat #cv2.imread(pathname)
            timer = pv.Timer()
            
            
            # Run the network in the worker processes...
            as_result = self.pool.apply_async(runNetwork,[im,request.options])
            
            dets = as_result.get()

            dets[:, 2] = dets[:, 2] - dets[:, 0] + 1
            dets[:, 3] = dets[:, 3] - dets[:, 1] + 1
            timer.mark("End Detection")

            result = fsd.DetectionList()

            for each in dets:
                det = result.detections.add()
                det.score = each[4]
                det.location.x = each[0]
                det.location.y = each[1]
                det.location.width = each[2]
                det.location.height = each[3]

            stop = time.time()
            print( "Processed image %16s -- %2d detections -- %0.4fs"%(im.shape,len(dets),stop-start,))
            sys.stdout.flush()
            sys.stderr.flush()
            return result
        except:
            traceback.print_exc()
            raise

    
    def detectAndExtract(self,request,context):
        raise NotImplementedError("'detectAndExtract' is currently not implemented.")


    def extract(self,request,context):
        raise NotImplementedError("'verify' is currently not implemented.")


    def enroll(self,request,context):
        raise NotImplementedError("'verify' is currently not implemented.")
    
    
    def search(self,request,context):
        raise NotImplementedError("'verify' is currently not implemented.")
    
    
    def batchLoad(self,filepath,gallery_name):
        raise NotImplementedError("'verify' is currently not implemented.")

    
    def verify(self,face_template,gallery_name):
        raise NotImplementedError("'verify' is currently not implemented.")
    

def serve():
    #global graph, model, cfg, NETS
    #cfg.TEST.HAS_RPN = True  # Use RPN for proposals

    options,args = parseOptions()
        
    print ('Configuring Server...')
    worker_thread_count = int(max(16,options.worker_count*2))
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=worker_thread_count),
                         options=[('grpc.max_send_message_length', 1024*1024*1024),
                                  ('grpc.max_receive_message_length', 1024*1024*1024)])
    #hdr_service = HDRService()

    face_service = RCNNFaceDetector(options)
    fs.add_FaceRecognitionServicer_to_server(face_service, server)

    #ir.add_HDRCNNServicer_to_server(hdr_service, server)
    

    port = server.add_insecure_port(options.port)

    print ('Starting Server on port:',port)
    server.start()
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        server.stop(0)
        print ('Sever Stopped.')


if __name__ == '__main__': 
    serve()


