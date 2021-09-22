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
import cv2
import time
#from _thread import _local
dlib = None
from pathlib import Path
import tensorflow as tf
from tf_bodypix.api import download_model, load_model, BodyPixModelPaths

class BodyPixFaceWorker(faro.FaceWorker):
    '''
    classdocs
    '''

    def __init__(self, options):
        '''
        Constructor
        '''

        # load model (once)
        self.bodypix_model = load_model(download_model(
            BodyPixModelPaths.MOBILENET_FLOAT_50_STRIDE_16
        ))


        
    def detect(self,img,face_records,options):

        # get prediction result
        image = img[:,:,::-1]#tf.keras.preprocessing.image.load_img(local_input_path)
        image_array = tf.keras.preprocessing.image.img_to_array(image)
        result = self.bodypix_model.predict_single(image_array)

        # simple mask
        mask = result.get_mask(threshold=0.75).numpy().astype('uint8')
        mask2 = cv2.resize(mask,(mask.shape[1],mask.shape[0]))
        pvmask = pv.Image(mask2)
        face_record = face_records.face_records.add()
        face_record.view.CopyFrom(pt.image_pv2proto(pvmask))

    def status(self):
        '''Return a simple status message.'''
        status_message = fsd.FaceServiceInfo()
        status_message.status = fsd.READY
        status_message.detection_support = True
        status_message.extract_support = True
        status_message.score_support = True
        status_message.score_type = self.scoreType()
        status_message.detection_threshold = self.recommendedDetectionThreshold();
        status_message.match_threshold = self.recommendedScoreThreshold();
        status_message.algorithm = "TF_BODYPIX_%s"%("1.0");

        
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


def runtestsegment():


    # setup input and output paths
    output_path = Path('./data/example-output')
    output_path.mkdir(parents=True, exist_ok=True)
    input_url = (
        'https://www.dropbox.com/s/7tsaqgdp149d8aj/serious-black-businesswoman-sitting-at-desk-in-office-5669603.jpg?dl=1'
    )
    local_input_path = tf.keras.utils.get_file(origin=input_url)

    # load model (once)
    bodypix_model = load_model(download_model(
        BodyPixModelPaths.MOBILENET_FLOAT_50_STRIDE_16
    ))

    # get prediction result
    image = tf.keras.preprocessing.image.load_img(local_input_path)
    image_array = tf.keras.preprocessing.image.img_to_array(image)
    result = bodypix_model.predict_single(image_array)

    # simple mask
    mask = result.get_mask(threshold=0.75)
    tf.keras.preprocessing.image.save_img(
        f'{output_path}/output-mask.jpg',
        mask
    )

    # colored mask (separate colour for each body part)
    # colored_mask = result.get_colored_part_mask(mask)
    # tf.keras.preprocessing.image.save_img(
    #     f'{output_path}/output-colored-mask.jpg',
    #     colored_mask
    # )

    # poses
    from tf_bodypix.draw import draw_poses  # utility function using OpenCV

    # poses = result.get_poses()
    m = mask.numpy()*255



if __name__ == '__main__':
    runtestsegment()