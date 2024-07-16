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
from faro.FaceGallery import SearchableGalleryWorker
import net
import torch
from face_alignment import mtcnn
from face_alignment.mtcnn import warp_and_crop_face

import PIL.Image as Image

def getGalleryWorker(options):
    print("Adaface: Creating indexed gallery worker...")
    return SearchableGalleryWorker(options,fsd.NEG_DOT)

def load_pretrained_model(architecture='ir_50',options=None):
    modelpath = os.path.join('/Users/2r6/faro_storage/models/','adaface','adaface_ir50_ms1mv2.ckpt')
    adaface_models = {
        'ir_50': modelpath
    }
    # load model and pretrained statedict
    assert architecture in adaface_models.keys()
    model = net.build_model(architecture)
    try:
        statedict = torch.load(adaface_models[architecture])['state_dict']
    except Exception as e:
        print('No GPU device available for adaface, falling back to CPU:')
        print('e')
        statedict = torch.load(adaface_models[architecture],map_location=torch.device('cpu'))['state_dict']
    model_statedict = {key[6:]:val for key, val in statedict.items() if key.startswith('model.')}
    model.load_state_dict(model_statedict)
    model.eval()
    return model


def to_input(pil_rgb_image):
    np_img = np.array(pil_rgb_image)
    brg_img = ((np_img[:, :, ::-1] / 255.) - 0.5) / 0.5
    tensor = torch.tensor(np.array([brg_img.transpose(2, 0, 1)])).float()
    return tensor


def add_padding(pil_img, top, right, bottom, left, color=(0, 0, 0)):
    width, height = pil_img.size
    new_width = width + right + left
    new_height = height + top + bottom
    result = Image.new(pil_img.mode, (new_width, new_height), color)
    result.paste(pil_img, (left, top))
    return result


def align_multi(mtcnn_model, img, limit=None):
    boxes, landmarks = mtcnn_model.detect_faces(img, mtcnn_model.min_face_size, mtcnn_model.thresholds,
                                                mtcnn_model.nms_thresholds, mtcnn_model.factor)
    if limit:
        boxes = boxes[:limit]
        landmarks = landmarks[:limit]
    faces = []
    for landmark in landmarks:
        facial5points = [[landmark[j], landmark[j + 5]] for j in range(5)]

        warped_face = warp_and_crop_face(np.array(img), facial5points, mtcnn_model.refrence,
                                         crop_size=mtcnn_model.crop_size)
        faces.append(Image.fromarray(warped_face))
    return boxes, faces, landmarks


def get_aligned_face(mtcnn_model,image_path, rgb_pil_image=None, best=True):
    if rgb_pil_image is None:
        img = Image.open(image_path).convert('RGB')
    else:
        assert isinstance(rgb_pil_image, Image.Image), 'Face alignment module requires PIL image or path to the image'
        img = rgb_pil_image
    # find face
    try:
        if best:
            limit = 1
        else:
            limit = None
        bboxes, faces, landmarks = align_multi(mtcnn_model, img, limit=limit)
        if best:
            face = ([bboxes[0]], [faces[0]], [landmarks[0]])
        else:
            face = (bboxes, faces, landmarks)
    except Exception as e:
        print('Face detection Failed due to error.')
        print(e)
        face = (None, None, None)

    return face

class AdafaceFaceWorker(faro.FaceWorker):
    '''
    classdocs
    '''

    def __init__(self, options):
        '''
        Constructor
        '''



        if options.gpuid == -1:
            ctx_id = -1
        else:
            ctx_id = int(options.gpuid)
        #self.detector.rac = 'net5'
        #set ctx_id to a gpu a predefined gpu value

        #Load the detector
        try:
            self.mtcnn_model = mtcnn.MTCNN(device='gpu:0', crop_size=(112, 112))
        except Exception as e:
            print('falling back to CPU mtcnn_model for alignment')
            self.mtcnn_model = mtcnn.MTCNN(device='cpu', crop_size=(112, 112))

        self.fr_model = load_pretrained_model('ir_50')
        # load arcface FR model

        print("ArcFace Models Loaded.")

    def pipeline(self,img, face_records, options, extract=True):
        '''Run a face detector and return rectangles.'''
        # print('Running Face Detector For ArchFace')
        # img = img[:,:,::-1] #convert from rgb to bgr . There is a reordering from bgr to RGB internally in the

        aligned_rgb_bboxes, aligned_rgb_imgs, landmarklist = get_aligned_face(self.mtcnn_model,None,
                                                                              faro.util.cv2_to_pil(img).convert('RGB'),
                                                                              best=True)
        idx = 0
        for bbox, aligned_rgb_img, landmarks in zip(aligned_rgb_bboxes, aligned_rgb_imgs, landmarklist):
            idx += 1
            face_record = face_records.face_records.add()

            face_record.detection.score = bbox[-1]
            ulx = bbox[0]
            uly = bbox[1]
            lrx = bbox[2]
            lry = bbox[3]
            face_record.detection.location.CopyFrom(pt.rect_val2proto(ulx, uly, abs(lrx - ulx), abs(lry - uly)))
            face_record.detection.detection_id = idx
            face_record.detection.detection_class = "FACE"
            facial5points = [[landmarks[j], landmarks[j + 5]] for j in range(5)]
            for ldx, landmark in enumerate(facial5points):
                lmark = face_record.landmarks.add()
                lmark.landmark_id = "point_%02d" % ldx

                lmark.location.x = int(landmark[0])
                lmark.location.y = int(landmark[1])
            if extract:
                bgr_tensor_input = to_input(aligned_rgb_img)
                feature, _ = self.fr_model(bgr_tensor_input)
                feature = feature.detach().numpy().flatten()
                face_record.template.data.CopyFrom(pt.vector_np2proto(feature))
        if options is not None:
            if options.best:
                face_records.face_records.sort(key=lambda x: -x.detection.score)
                while len(face_records.face_records) > 1:
                    del face_records.face_records[-1]
    def detect(self,img,face_records,options):
        '''Run a face detector and return rectangles.'''
        self.pipeline(img,face_records,options,extract=False)
    
    def locate(self,img,face_records,options):
        '''Locate facial features.'''
        pass #the 5 landmarks points that retina face detects are stored during detection
        
        
    def align(self,image,face_records,options):
        '''Align the images to a standard size and orientation to allow 
        recognition.'''
        pass # Not needed for this algorithm.
            
    def extract(self,img,face_records,options):
        self.pipeline(img, face_records, options, extract=True)

                
    def scoreType(self):
        '''Return the method used to create a score from the template.
        
        By default server computation is required.
        
        SCORE_L1, SCORE_L2, SCORE_DOT, SCORE_SERVER
        '''
        return fsd.SCORE_DOT
    
    def status(self):
        '''Return a simple status message.'''
        status_message = fsd.FaceServiceInfo()
        status_message.status = fsd.READY
        status_message.detection_support = True
        status_message.extract_support = True
        status_message.score_support = True
        status_message.score_type = self.scoreType()
        status_message.detection_threshold = self.recommendedDetectionThreshold()
        status_message.match_threshold = self.recommendedScoreThreshold()
        status_message.algorithm = "AdaFace-model adaface_ir50_ms1mv2"

        
        return status_message
        

    def recommendedDetectionThreshold(self):
        
        return 0.5

    def recommendedScoreThreshold(self,far=-1):
       
        '''
        Arcface does not provide a match threshold
        '''
         
        return -0.42838144


