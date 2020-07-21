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

Created on Jul 26, 2018

@author: bolme
'''


import numpy as np
import pyvision as pv
import cv2
import urllib


import faro.proto.geometry_pb2 as geometry
import faro.proto.image_pb2 as image
import faro.proto.face_service_pb2 as fsd

def image_np2proto(im):
    '''Convert a numpy array to a protobuf format.'''
    #if isinstance(im,pv.Image):
    #    im = im.asOpenCV2()[:,:,::-1] # Convert bgr to rgb
    #im = np.array(im,dtype=np.uint8)
    #print('dtype',im.dtype,im.shape,im)
    assert im.dtype == np.uint8 # Currently only uint8 supported
    result = image.Image()
    result.width = im.shape[1]
    result.height = im.shape[0]
    if len(im.shape) > 2:
        result.channels = im.shape[2]
    else:
        result.channels = 1
    result.type = image.Image.UINT8
    result.data = im.tostring()
    return result
    
def image_pv2proto(im):
    '''Convert a numpy array to a protobuf format.'''
    assert isinstance(im,pv.Image)
    im = im.asOpenCV2()[:,:,::-1] # Convert bgr to rgb
    assert im.dtype == np.uint8 # Currently only uint8 supported
    result = image.Image()
    result.width = im.shape[1]
    result.height = im.shape[0]
    result.channels = im.shape[2]
    result.type = image.Image.UINT8
    result.data = im.tostring()
    return result
    
def image_proto2cv(pb_data):
    '''Convert a protobuf image to a opencv array.'''
    shape = pb_data.height,pb_data.width,pb_data.channels
    if pb_data.type == image.Image.UINT8:
        data = np.fromstring(pb_data.data,dtype=np.uint8)
        data.shape = shape
        data = data[:,:,::-1]
    elif pb_data.type in (image.Image.PNG,image.Image.JPG):
        tmp = np.fromstring(pb_data.data,dtype='uint8')
        data = cv2.imdecode(tmp,cv2.IMREAD_COLOR)
    elif pb_data.type in (image.Image.URL):
        link = pb_data.data
        f = urllib.urlopen(link)
        tmp = f.read()
        data = cv2.imdecode(tmp,cv2.IMREAD_COLOR)
    else:
        raise ValueError("ImageType not supported: "+repr(pb_data.type))
        
    return data

def image_proto2np(pb_data):
    '''Convert a protobuf image to a numpy array.'''
    data = image_proto2cv(pb_data)
    data = data[:,:,::-1] # Convert BGR to RGB
    return data

def image_proto2pv(pb_data):
    '''Convert a protobuf image to a numpy array.'''
    data = image_proto2cv(pb_data)
    data = pv.Image(data) # OpenCV to pyvision
    return data


def detection_val2proto(score=-1000000,x=0,y=0,width=0,height=0):
    det = fsd.FaceDetection()
    det.score = score
    det.location.x = x
    det.location.y = y 
    det.location.width = width
    det.location.height = height
    return det


def rect_val2proto(x=0,y=0,width=0,height=0):
    '''
    Examples:
        createRect(x,y,width,height)
    '''
    location = geometry.Rect()
    location.x = x
    location.y = y 
    location.width = width
    location.height = height
    return location

def rect_proto2pv(proto_rect):
    return pv.Rect(proto_rect.x, proto_rect.y, proto_rect.width, proto_rect.height)
    
def vector_np2proto(vec):
    protovec = geometry.Vector()
    assert len(vec.shape) == 1
    protovec.data.extend(vec)
    return protovec
    
def vector_proto2np(protovec):
    vec = np.array(protovec.data,dtype=np.float32)
    return vec
    

        
def matrix_np2proto(mat):
    result = geometry.Matrix()
    for row in mat:
        result.rows.add().CopyFrom(vector_np2proto(row))
    return result
        
    #protovec = geometry.Vector()
    #assert len(vec.shape) == 1
    #protovec.length=vec.shape[0]
    #protovec.data.extend(vec)
    #return protovec
    
def matrix_proto2np(protomat):
    mat = []
    for row in protomat.rows:
        vec = vector_proto2np(row)
        mat.append(vec)
    mat = np.array(mat,dtype=np.float32)
    return mat
    

        
