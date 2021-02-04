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

Created on October 3, 2019

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

class ArcfaceFaceWorker(faro.FaceWorker):
    '''
    classdocs
    '''

    def __init__(self, options):
        '''
        Constructor
        '''
        import insightface
        import torch
        import torch.nn as nn
        from torch.utils.data import DataLoader
        from torchvision import transforms
        import torch.backends.cudnn as cudnn
        import torchvision
        import hopenet

        os.environ['MXNET_CUDNN_AUTOTUNE_DEFAULT'] = '0'
        kwargs = {'root':os.path.join(options.storage_dir,'models')}
        #load Retina face model
        self.detector = insightface.model_zoo.get_model('retinaface_r50_v1',**kwargs)
        if options.gpuid == -1:
            self.ctx_id = -1
        else:
            self.ctx_id = int(options.gpuid)
        #set ctx_id to a gpu a predefined gpu value
        self.detector.prepare(self.ctx_id, nms=0.4)
        # load arcface FR model
        self.fr_model = insightface.model_zoo.get_model('arcface_r100_v1',**kwargs)
        
        self.fr_model.prepare(self.ctx_id) 
        self.preprocess = insightface.utils.face_align
        print("ArcFace Models Loaded.")
        

        self.deep_pose_model = hopenet.Hopenet(torchvision.models.resnet.Bottleneck, [3, 4, 6, 3], 66)
        cudnn.enabled = True
        saved_state_dict = torch.load(os.path.join(options.storage_dir, 'models', 'deep_head_pose', 'hopenet_robust_alpha1.pkl'))
        self.deep_pose_model.load_state_dict(saved_state_dict)
        self.deep_pose_model.cuda(self.ctx_id)
        self.transformations = transforms.Compose([transforms.Scale(224), transforms.CenterCrop(224), transforms.ToTensor(), transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])
        self.deep_pose_model.eval() 
        self.idx_tensor = [idx for idx in range(66)]
        self.idx_tensor = torch.FloatTensor(self.idx_tensor).cuda(self.ctx_id)
        print('Deep pose head models Ready')

    def detect(self,img,face_records,options):
        from torch.autograd import Variable
        import torch.nn.functional as F
        import torch
        '''Run a face detector and return rectangles.'''
        print('Running Face Detector For ArchFace')
        img_bgr = img[:,:,::-1] #convert from rgb to bgr . There is a reordering from bgr to RGB internally in the detector code.
        dets, lpts = self.detector.detect(img_bgr, threshold=options.threshold, scale=1)
        #print('Number of detections ', dets.shape[0])
        # Now process each face we found and add a face to the records list.
        for idx in range(0,dets.shape[0]):
            face_record = face_records.face_records.add()
            face_record.detection.score = dets[idx,-1:]
            ulx, uly, lrx, lry = dets[idx,:-1]        
            #create_square_bbox = np.amax(abs(lrx-ulx) , abs(lry-uly))
            face_record.detection.location.CopyFrom(pt.rect_val2proto(ulx, uly, abs(lrx-ulx) , abs(lry-uly)))
            face_record.detection.detection_id = idx
            face_record.detection.detection_class = "FACE_%d"%idx
            #lmark = face_record.landmarks.add()
            lmarkloc = lpts[idx]
            for ldx in range(0,lmarkloc.shape[0]):
                lmark = face_record.landmarks.add()
                lmark.landmark_id = "point_%02d"%ldx
                lmark.location.x = lmarkloc[ldx][0]
                lmark.location.y = lmarkloc[ldx][1]
            
            x_min, y_min, x_max, y_max = int(ulx), int(uly), int(lrx), int(lry)
            bbox_width = abs(x_max - x_min)
            bbox_height = abs(y_max - y_min)
            x_min -= 50
            x_max += 50
            y_min -= 50
            y_max += 30
            x_min = max(x_min, 0)
            y_min = max(y_min, 0)
            x_max = min(img.shape[1], x_max)
            y_max = min(img.shape[0], y_max)

            img_mod = img[y_min:y_max,x_min:x_max]
            img_mod = Image.fromarray(img_mod)
            img_mod = self.transformations(img_mod) 
            img_shape = img_mod.size()
            img_mod = img_mod.view(1, img_shape[0], img_shape[1], img_shape[2])
            img_mod = Variable(img_mod).cuda(self.ctx_id)
            #try:
            yaw, pitch, roll = self.deep_pose_model(img_mod)
            yaw_predicted = F.softmax(yaw)
            pitch_predicted = F.softmax(pitch)
            roll_predicted = F.softmax(roll)
            yaw_predicted = torch.sum(yaw_predicted.data[0] * self.idx_tensor) * 3 - 99
            pitch_predicted = torch.sum(pitch_predicted.data[0] * self.idx_tensor) * 3 - 99
            roll_predicted = torch.sum(roll_predicted.data[0] * self.idx_tensor) * 3 - 99
            
            demographic = face_record.attributes.add()
            demographic.key = 'Yaw'
            demographic.text = str(yaw_predicted.cpu().numpy())

            demographic = face_record.attributes.add()
            demographic.key = 'Pitch'
            demographic.text = str(pitch_predicted.cpu().numpy()) 

            demographic = face_record.attributes.add()
            demographic.key = 'Roll'
            demographic.text = str(roll_predicted.cpu().numpy())
        
        if options.best:
            face_records.face_records.sort(key = lambda x: -x.detection.score)
            
            while len(face_records.face_records) > 1:
                del face_records.face_records[-1]
            
        print('Done Running Face Detector For ArcFace')
    
    def locate(self,img,face_records,options):
        '''Locate facial features.'''
        pass 

    def align(self,image,face_records):
        '''Align the images to a standard size and orientation to allow 
        recognition.'''
        pass # Not needed for this algorithm.
            
    def extract(self,img,face_records):
        '''Extract a template that allows the face to be matched.'''
        # Compute the 512D vector that describes the face in img identified by
        #shape.
        #print(type(img),img.shape)
        img = img[:,:,::-1] #convert from rgb to bgr. There is BGRtoRGB conversion in get_embedding

        for face_record in face_records.face_records:
            #print(face_record)
            if face_record.detection.score != -1:
                landmarks = np.zeros((5,2),dtype=np.float)
                for i in range(0,len(face_record.landmarks)):
                        vals = face_record.landmarks[i]
                        landmarks[i,0] = vals.location.x
                        landmarks[i,1] = vals.location.y
 
                _img = self.preprocess.norm_crop(img, landmark = landmarks)
                #print(_img.shape)            
                embedding = self.fr_model.get_embedding(_img).flatten()
                embedding_norm = np.linalg.norm(embedding)
                normed_embedding = embedding / embedding_norm
                #print(normed_embedding.shape)
            else:
                normed_embedding = np.zeros(512,dtype=float)
            
            face_record.template.data.CopyFrom(pt.vector_np2proto(normed_embedding))

                
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
        status_message.algorithm = "ArcFace-model arcface_r100_v1"

        
        return status_message
        

    def recommendedDetectionThreshold(self):
        
        return 0.5

    def recommendedScoreThreshold(self,far=-1):
       
        '''
        Arcface does not provide a match threshold
        '''
         
        return -0.42838144


