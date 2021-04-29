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

Created on April 7th, 2019

@author: srinivasn1
@ORNL
'''

import faro
import os
import faro.proto.proto_types as pt 
import faro.proto.face_service_pb2 as fsd
import numpy as np
import pyvision as pv
from PIL import Image

def getOptionsGroup(parser):

    yolov4_options = parser.add_option_group("Options for YOLOV4")
    yolov4_options.add_option("--iou-threshold", type=float, dest="iou_threshold", default=0.6)
    #height = 320 + 96 * n, n in {0, 1, 2, 3, ...}
    #width  = 320 + 96 * m, m in {0, 1, 2, 3, ...}
    yolov4_options.add_option("--height-factor", type=int, dest="height_scale", default=1)
    yolov4_options.add_option("--width-factor", type=int, dest="width_scale", default=1)

class YOLOV4FaceWorker(faro.FaceWorker):
    '''
    classdocs
    '''

    def __init__(self, options):
        '''
        Constructor
        '''
        global torch
        global cv2
        global np
        import torch as _local_torch
        torch = _local_torch
        from yolov4_net import Yolov4
        import cv2 as _local_cv2
        cv2 = _local_cv2 
        import numpy as _local_np
        np = _local_np
        #80 classes - COCO dataset
        self.width_scale = options.width_scale
        self.height_scale = options.height_scale
        self.iou_threshold = options.iou_threshold
        self.gpuid = options.gpuid
        self.n_classes = 80
        self.model = Yolov4(n_classes=self.n_classes, inference=True)
        weights_path = os.path.join(options.storage_dir, 'models', 'yolov4')
        weight_file = os.path.join(weights_path, 'yolov4.pth')

        if options.gpuid == -1:
            run_on_device = torch.device("cpu")
            pretrained_dict = torch.load(weight_file, map_location=run_on_device)
            self.model.load_state_dict(pretrained_dict)
        else:
            run_on_device = torch.device("cuda")
            pretrained_dict = torch.load(weight_file, map_location=run_on_device)
            self.model.load_state_dict(pretrained_dict)
            self.model.cuda(int(options.gpuid))
        
        print('Loaded YoloV4 model for cell phone detection')
    
    def _nms_cpu(self, boxes, confs, nms_thresh=0.5, min_mode=False):
        # print(boxes.shape)
        x1 = boxes[:, 0]
        y1 = boxes[:, 1]
        x2 = boxes[:, 2]
        y2 = boxes[:, 3]

        areas = (x2 - x1) * (y2 - y1)
        order = confs.argsort()[::-1]

        keep = []
        while order.size > 0:
            idx_self = order[0]
            idx_other = order[1:]

            keep.append(idx_self)

            xx1 = np.maximum(x1[idx_self], x1[idx_other])
            yy1 = np.maximum(y1[idx_self], y1[idx_other])
            xx2 = np.minimum(x2[idx_self], x2[idx_other])
            yy2 = np.minimum(y2[idx_self], y2[idx_other])

            w = np.maximum(0.0, xx2 - xx1)
            h = np.maximum(0.0, yy2 - yy1)
            inter = w * h

            if min_mode:
                over = inter / np.minimum(areas[order[0]], areas[order[1:]])
            else:
                over = inter / (areas[order[0]] + areas[order[1:]] - inter)

            inds = np.where(over <= nms_thresh)[0]
            order = order[inds + 1]
        
        return np.array(keep)

    def _post_processing(self, conf_thresh, nms_thresh, output):

        box_array = output[0]
        confs = output[1]

        
        if type(box_array).__name__ != 'ndarray':
            box_array = box_array.cpu().detach().numpy()
            confs = confs.cpu().detach().numpy()

        num_classes = confs.shape[2]
        box_array = box_array[:, :, 0]
        max_conf = np.max(confs, axis=2)
        max_id = np.argmax(confs, axis=2)
        bboxes_batch = []
        for i in range(box_array.shape[0]):
       
            argwhere = max_conf[i] > conf_thresh
            l_box_array = box_array[i, argwhere, :]
            l_max_conf = max_conf[i, argwhere]
            l_max_id = max_id[i, argwhere]

            bboxes = []
            j = 67
            cls_argwhere = l_max_id == j
            ll_box_array = l_box_array[cls_argwhere, :]
            ll_max_conf = l_max_conf[cls_argwhere]
            ll_max_id = l_max_id[cls_argwhere]

            keep = self._nms_cpu(ll_box_array, ll_max_conf, nms_thresh)
            
            if (keep.size > 0):
                ll_box_array = ll_box_array[keep, :]
                ll_max_conf = ll_max_conf[keep]
                ll_max_id = ll_max_id[keep]

                for k in range(ll_box_array.shape[0]):
                    bboxes.append([ll_box_array[k, 0], ll_box_array[k, 1], ll_box_array[k, 2], ll_box_array[k, 3], ll_max_conf[k], ll_max_conf[k], ll_max_id[k]])
        
            bboxes_batch.append(bboxes)
        return bboxes_batch

    def detect(self,img,face_records,options):
        new_width = 320 + 96 * self.width_scale
        new_height = 320 + 96 *  self.height_scale
        sized = cv2.resize(img, (new_width, new_height))
        old_width = img.shape[1]
        old_height = img.shape[0]
        self.model.eval()
        sized = torch.from_numpy(sized.transpose(2, 0, 1)).float().div(255.0).unsqueeze(0)
        if self.gpuid != -1:
            sized = sized.cuda(int(self.gpuid))
        sized = torch.autograd.Variable(sized)
        output = self.model(sized)
        confidence_thresh = options.threshold
        nms_thresh = self.iou_threshold
        boxes = self._post_processing(confidence_thresh, nms_thresh, output)
        boxes = boxes[0]
        if len(boxes) > 0:
            for idx in range(0,len(boxes)):
                face_record = face_records.face_records.add()
                box = boxes[idx]
                ulx = int(box[0] * old_width)
                uly = int(box[1] * old_height)
                lrx = int(box[2] * old_width)
                lry = int(box[3] * old_height)
                face_record.detection.location.CopyFrom(pt.rect_val2proto(ulx, uly, abs(lrx-ulx) , abs(lry-uly)))
                face_record.detection.detection_id = idx
                face_record.detection.detection_class = "CELLPHONE_%d"%box[4]
                face_record.detection.score = box[5]

        if options.best:
            face_records.face_records.sort(key = lambda x: -x.detection.score)
            
            while len(face_records.face_records) > 1:
                del face_records.face_records[-1]

    def locate(self,img,face_records,options):
        '''Locate facial features.'''
        pass 

    def align(self,image,face_records):
        '''Align the images to a standard size and orientation to allow 
        recognition.'''
        pass 
            
    def extract(self,img,face_records):
        '''Extract a template that allows the face to be matched.'''
        pass
                
    def scoreType(self):
        '''Return the method used to create a score from the template.
        
        By default server computation is required.
        
        SCORE_L1, SCORE_L2, SCORE_DOT, SCORE_SERVER
        '''
        pass
 
    def status(self):
        '''Return a simple status message.'''
        print("Handeling status request.")
        status_message = fsd.FaceServiceInfo()
        status_message.status = fsd.READY
        status_message.detection_support = True
        status_message.extract_support = False
        status_message.score_support = False
        status_message.detection_threshold = self.recommendedDetectionThreshold()
        status_message.algorithm = "Cell Phone Detector using YoloV4"

        return status_message
        

    def recommendedDetectionThreshold(self):
        #according to the github repo
        return 0.4

    def recommendedScoreThreshold(self,far=-1):
       
        '''
        Not required
        '''
         
        return None


