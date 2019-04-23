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

Created on Feb 10, 2019

@author: bolme
'''

import os

_keras = None
_K = None

_tf = None
_tf_sess = None

def loadKeras(gpu_id = None):
    '''
    Use this function to load keras in a safe way that limits gpu memory usage
    and allows multiple workerns on a single gpu.
    '''        
    global _keras
    global _K
    
    if _keras is None:
        global FACE_ALG 
        import keras.backend as K
        
        config = K.tf.ConfigProto()
        config.gpu_options.allow_growth = True
        session = K.tf.Session(config=config)
        K.set_session(session)
        
        import keras
        
        _keras = keras
        _K = K
    
    return _keras, _K

def getTensorflowSession(gpu_id = None):
    
    global _tf
    global _tf_sess
    
    if _tf == None:
        import tensorflow as tf
        _tf = tf
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        #config.gpu_options.per_process_gpu_memory_fraction = 0.2
        _tf_sess = tf.Session(config=config)
        
    return _tf, _tf_sess
