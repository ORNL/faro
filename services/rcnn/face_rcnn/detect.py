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
from __future__ import division

#import _init_paths
from fast_rcnn.config import cfg
from fast_rcnn.test import im_detect
from fast_rcnn.nms_wrapper import nms
from utils.timer import Timer
import matplotlib.pyplot as plt
import numpy as np
import scipy.io as sio
import caffe, os, sys, cv2
import argparse
import sys
import pyvision as pv
import csv

#print
#print cfg
#print
#exit(0)


NETS = {'vgg16': ('VGG16',
          os.path.join(os.path.dirname(__file__),'models','face_vgg16_faster_rcnn.caffemodel'))}


def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='Face Detection using Faster R-CNN')
    parser.add_argument('--gpu', dest='gpu_id', help='GPU device id to use [0]',
            default=0, type=int)
    parser.add_argument('--cpu', dest='cpu_mode',
            help='Use CPU mode (overrides --gpu)',
            action='store_true')
    parser.add_argument('--net', dest='demo_net', help='Network to use [vgg16]',
            choices=NETS.keys(), default='vgg16')

    parser.add_argument('--dir', dest='scan_dir', help='scan this directory for images.',
            action='store', default=None)
    parser.add_argument('--output', dest='output_dir', help='save results to this directory.',
            action='store', default=None)

    parser.add_argument('--csv', dest='output_csv', help='save results to a csv file.',
            action='store', default=None)

    parser.add_argument('--thresh', dest='detect_thresh', type=float,  help='set the detection threshold.',
            action='store', default=0.9)

    args = parser.parse_args()

    return args

if __name__ == '__main__':
    cfg.TEST.HAS_RPN = True  # Use RPN for proposals
    # cfg.TEST.BBOX_REG = False

    args = parse_args()

    #prototxt = os.path.join(cfg.MODELS_DIR, NETS[args.demo_net][0],
    #          'faster_rcnn_alt_opt', 'faster_rcnn_test.pt')
    #caffemodel = os.path.join(cfg.DATA_DIR, 'faster_rcnn_models',
    #            NETS[args.demo_net][1])

    prototxt = os.path.join(os.path.dirname(__file__),'models','test.prototxt')
    #'models/face/VGG16/faster_rcnn_end2end/test.prototxt'
    caffemodel = NETS[args.demo_net][1]

    if not os.path.isfile(caffemodel):
        raise IOError(('{:s} not found.\nDid you run ./data/script/'
             'fetch_faster_rcnn_models.sh?').format(caffemodel))

    if args.cpu_mode:
        caffe.set_mode_cpu()
    else:
        caffe.set_mode_gpu()
        caffe.set_device(args.gpu_id)
        cfg.GPU_ID = args.gpu_id
    net = caffe.Net(prototxt, caffemodel, caffe.TEST)

    print '\n\nLoaded network {:s}'.format(caffemodel)


    out_dir = args.output_dir
    
    if out_dir is None:
        print "Error: you must provide an output directory using the --output option."

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    CONF_THRESH = 0.65
    NMS_THRESH = 0.15

    # imdb = get_imdb_fddb(data_dir)

    # Warmup on a dummy image
    im = 128 * np.ones((300, 500, 3), dtype=np.uint8)
    for i in xrange(2):
        _, _= im_detect(net, im)
  
    result_id = 0
    
    if args.scan_dir is None:
        print "ERROR: you must provide an image directory using the --dir option."
        exit(0)
        
    
    csv_file = None
    if args.output_csv:
        csv_file = csv.DictWriter(open(args.output_csv,'w'),fieldnames=['path','detect_id','x','y','w','h','score'])
            
    
    for path,dirs,files in os.walk(args.scan_dir):
        for filename in files:
            
            pathname = os.path.join(path,filename)
            try:
                if not pv.isImage(filename):
                    continue
    
                im = cv2.imread(pathname)
                print "Running net on image: %s %s %d"%(filename,im.shape,result_id)
                timer = pv.Timer()
                scores, boxes = im_detect(net, im)
                #print scores.shape,boxes.shape
    
                cls_ind = 1
                cls_boxes = boxes[:, 4*cls_ind:4*(cls_ind + 1)]
                cls_scores = scores[:, cls_ind]
                dets = np.hstack((cls_boxes,
                        cls_scores[:, np.newaxis])).astype(np.float32)
                keep = nms(dets, NMS_THRESH)
                dets = dets[keep, :]
    
                keep = np.where(dets[:, 4] > args.detect_thresh)
                dets = dets[keep]
    
                # vis_detections(im, 'face', dets, CONF_THRESH)
    
                dets[:, 2] = dets[:, 2] - dets[:, 0] + 1
                dets[:, 3] = dets[:, 3] - dets[:, 1] + 1
                timer.mark("End Detection")
                #print dets.shape
                # print dets
                rects = []
                for each in dets:
                    rect = pv.Rect(each[0],each[1],each[2],each[3])
                    rect.score = each[4]
                    rects.append(rect)
                #print timer
                for rect in rects:
                    print rect.score,rect
                im = pv.Image(im)
                i = 0
                for rect in rects:
                    #if rect.score < DETECTION_THRESH:
                    #    continue
                    im.annotateRect(rect)
                    
                    out_data = {}
                    out_data['path'] = pathname
                    out_data['detect_id'] = i
                    out_data['x'] = rect.x
                    out_data['y'] = rect.y
                    out_data['w'] = rect.w
                    out_data['h'] = rect.h
                    out_data['score'] = rect.score
                    print out_data
                    if csv_file is not None:
                        csv_file.writerow(out_data)
                    i+= 1
                    
                tmp_name = os.path.splitext(filename)[0]
                pv.Image(im.asAnnotated()).save(os.path.join(out_dir,"%s.png"%tmp_name))
                result_id += 1
                #im.show()
            except:
                print ("Error processing file:",pathname)

  
      
