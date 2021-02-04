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
'''
__version__ = "1.1.0"

DEFAULT_PORT = "0.0.0.0:50030"
DEFAULT_MAX_MESSAGE_SIZE = 64*1024*1024 # 64MB
DEFAULT_MAX_ASYNC = 8 # The maximum number of async client calls at a time.
DEFAULT_MAX_SIZE = 1920



from .FaceWorker import FaceWorker, SCORE_L1, SCORE_L2, SCORE_DOT, SCORE_SERVER, STATUS_READY
#from faro.face_workers import DlibFaceWorker
#from faro.face_workers import VggFaceWorker
#from faro.face_workers import RcnnFaceWorker
from .util import loadKeras
from .FaceCommandLine import face_command_line

from .FaceGallery import Gallery

from .FaceClient import FaceClient, getDefaultClientOptions

import os

try:
    DEFAULT_STORAGE_DIR = os.environ['FARO_STORAGE']
except:
    DEFAULT_STORAGE_DIR = os.path.join(os.environ['HOME'],'faro_storage')




def generateFaceId(face):
    '''
    Generate a face_id code to identify this particular face.
    '''
    if len(face.source) == 0 or face.source == "UNKNOWN_SOURCE":
        raise ValueError("face.source needs to be defined in order to generate a unique face id code.")

    face_id = "%s:%s:%03d"%(face.subject_id,face.source,face.detection.detection_id)
    
    face_id = "_-_".join(face_id.split('/'))

    return face_id



