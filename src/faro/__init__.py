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

DEFAULT_PORT = "localhost:50030"
DEFAULT_MAX_MESSAGE_SIZE = 64*1024*1024 # 64MB



from .FaceWorker import FaceWorker, SCORE_L1, SCORE_L2, SCORE_DOT, SCORE_SERVER, STATUS_READY
#from faro.face_workers import DlibFaceWorker
#from faro.face_workers import VggFaceWorker
#from faro.face_workers import RcnnFaceWorker
from .util import loadKeras

from .FaceGallery import Gallery

from .FaceClient import FaceClient

import os


DEFAULT_STORAGE_DIR = os.path.join(os.environ['HOME'],'faro_storage')
