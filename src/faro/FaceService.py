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

Created on Jul 18, 2018

@author: bolme
'''
import grpc
import pyvision as pv
import numpy as np
import faro.proto.face_service_pb2_grpc as fs
import faro.proto.face_service_pb2 as fsd
from concurrent import futures
import traceback
import time
#import dlib
import faro.proto.proto_types as pt
from faro.proto.face_service_pb2 import DetectionRequest,FaceRecordList
import csv
#from faro import FaceAlgorithms
import multiprocessing as mp
import optparse
import sys
import socket
import faro
import os

import skimage.io

LOG_FORMAT = "%-20s: %8.4fs: %-15s - %s"
#FFD = dlib.get_frontal_face_detector()



FACE_ALG = None
        
FACE_WORKER_LIST = {}        

def worker_init(options):
    ''' Initalize the worker processes. '''
    
    print("Starting worker process:",mp.current_process())
    
    global MYNET,WORKER_INDEX,OPTIONS
    global FACE_WORKER_LIST
    #cfg.TEST.HAS_RPN = True  # Use RPN for proposals
    proc = mp.current_process()
    WORKER_INDEX = (int(proc.name.split('-')[-1])-1)%options.worker_count

    OPTIONS = options
    
    assert WORKER_INDEX >= 0

    gpu_id = 0
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID" 
    os.environ["CUDA_VISIBLE_DEVICES"] = "%d"%gpu_id
    global FACE_ALG 
    
    try: 
        FACE_ALG = FACE_WORKER_LIST[options.algorithm][0](options)
        
    except:
        print ("ERROR: Worker %d could not be started."%WORKER_INDEX)
        traceback.print_exc() 
        raise   

    print( "Worker %d Ready."%(WORKER_INDEX) )


def worker_status():
    global FACE_ALG
    assert FACE_ALG is not None
    
    try:
        status_message = FACE_ALG.status()
        return status_message
    except:
        print("ERROR in worker executing status method.")
        traceback.print_exc()
        raise
    

def worker_detect(mat,options):
    global FACE_ALG
    assert FACE_ALG is not None
    
    try:
        # uncomment this line to check that the image is comming through properly.
        # skimage.io.imsave('/tmp/test.png', mat)
        face_record_list = FaceRecordList()
        FACE_ALG.detect(mat,face_record_list,options)
        return face_record_list
    except:
        print("ERROR in worker executing detect method.")
        traceback.print_exc()
        raise
    

#def worker_detect_extract(mat,options):
#    global FACE_ALG
#    assert FACE_ALG is not None
#
#    try:
#        face_record_list = FaceRecordList()
#        FACE_ALG.detectAndExtract(mat,face_record_list,options)
#        return face_record_list
#    except:
#        print("ERROR in worker executing detection and extraction method.")
#        traceback.print_exc()
#        raise
#


def worker_extract(mat,face_record_list):
    global FACE_ALG
    assert FACE_ALG is not None
    
    try:
        FACE_ALG.extract(mat,face_record_list)
        return face_record_list
    except:
        print("ERROR in worker executing extract method.")
        traceback.print_exc()
        raise

def worker_score(request):
    global FACE_ALG
    assert FACE_ALG is not None
    
    try:
        dist_mat = FACE_ALG.score(request)
        return dist_mat
    except:
        print("ERROR in worker executing extract method.")
        traceback.print_exc()
        raise

def worker_extractTile(mat):
    global FACE_ALG
    assert FACE_ALG is not None
    
    return FACE_ALG.extractTile(mat)

def worker_cleanexit():
    global FACE_ALG
    assert FACE_ALG is not None

    try:
        FACE_ALG.cleanexit()
    except:
        print("ERROR in worker executing extract method.")
        traceback.print_exc()
        raise

class FaceService(fs.FaceRecognitionServicer):
    
    def __init__(self,options):
        #self.alg = FaceAlgorithms.FaceAlgorithms()
        self.galleries = {}
        self.workers = mp.Pool(options.worker_count, worker_init, [options])

        
    def status(self,request,context):
        ''' Returns the status of the service. '''
        worker_result = self.workers.apply_async(worker_status,[])
        status_message = worker_result.get()
        #status_message.worker_count = len(self.workers);

        
        print('Status Request', '<',status_message,'>')

        return status_message

    def detect(self,request,context):
        ''' Runs a face detector and return rectangles. '''
        try:
            
            start = time.time()
            mat = pt.image_proto2np(request.image)
            options = request.options
            notes = "Image Size %s"%(mat.shape,)
            
            worker_result = self.workers.apply_async(worker_detect,[mat,options])
            face_records_list = worker_result.get()
            
            notes += ", Detections %s"%(len(face_records_list.face_records),)
            
            #date = request.image.date
            #time_ = request.image.time
            #module = request.image.module
            #camera = request.image.camera
            #event = request.image.event
            #image_num = request.image.image_num

            stop = time.time()
            global LOG_FORMAT
            print(( LOG_FORMAT%(pv.timestamp(),stop-start,"detect()",notes)))
    
            #print (face_records_list)
            return face_records_list
        
        except:
            traceback.print_exc()
            raise

    
    def detectAndExtract(self,request,context):
        ''' runs the face detector and returns face extracted faces. '''
        '''
        I am assuming this funtion does both detection and feature extraction
        and returns a list of face records.
        I feel like we should discuss about some design issues going forward.
        And this is because Commercial Algorithms gives us access to templates/
        feature vectors in custom data structure formats
        '''
        
       # try:
       #     
       #     start = time.time()
       #     mat = pt.image_proto2np(request.image)
       #     options = request.options
       #     notes = "Image Size %s"%(mat.shape,)
       #     
       #     worker_result = self.workers.apply_async(worker_detect_extract,[mat,options])
       #     face_records_list = worker_result.get()
       #     
       #     notes += ", Detections %s"%(len(face_records_list.face_records),)
       #     
       #     #date = request.image.date
       #     #time_ = request.image.time
       #     #module = request.image.module
       #     #camera = request.image.camera
       #     #event = request.image.event
       #     #image_num = request.image.image_num

       #     stop = time.time()
       #     global LOG_FORMAT
       #     print(( LOG_FORMAT%(pv.timestamp(),stop-start,"detect()",notes)))
    
       #     #print (face_records_list)
       #     return face_records_list
       # 
       # except:
       #     traceback.print_exc()
       #     raise



        #try:
        #    start = time.time()
        #    
        #    display = False
        #    #print 'Calling stuff\n'
        #    mat = pt.image_proto2pv(request.image)
        #    #print 'Returned from proto2pv\n'
        #    detections = self.detect(request,context)
        #    #print 'Returned from detect\n'
        #    result = fsd.FaceRecordList()
        #    
        #    templates = []
        #    for detect in detections.detections:
        #        temp = self.extract(mat, detect)
        #        rect = pt.rect_proto2pv(detect.location)
        #        view = mat.crop(rect).thumbnail((256,256))
        #        #view.show(delay=10)
        #        templates.append(temp)
        #        face_record = result.face_records.add()
        #        face_record.subject_id = 'unknown'
        #        face_record.source = 'unknown'
        #        face_record.detection.CopyFrom(detect)
        #        face_record.template.CopyFrom(pt.vector_np2proto(temp))
        #        face_record.view.CopyFrom(pt.image_pv2proto(view))
        #        if display:
        #            mat.annotateRect(rect, 'red')
        #    
        #    if display:
        #        mat.show(delay=10000)
        #        
        #    stop = time.time()
        #    notes = "None"
        #    print(( LOG_FORMAT%(pv.timestamp(),stop-start,"detectAndExtract()",notes)))
    
        #    return result
    
        #except:
        #    traceback.print_exc()
        #    raise


    def extract(self,request,context):
        ''' Extracts faces from the image for the given face detections. '''
        try:
            start = time.time()
            
            #display = False
            img = pt.image_proto2np(request.image)
            face_records = request.records
            
            worker_result = self.workers.apply_async(worker_extract,[img,face_records])
            face_records_list = worker_result.get()

            notes = "Image Size %s"%(img.shape,)
                        
            notes += ", Faces %s"%(len(face_records_list.face_records),)

            stop = time.time()
            global LOG_FORMAT
            print(( LOG_FORMAT%(pv.timestamp(),stop-start,"extract()",notes)))

            return face_records_list
    
        except:
            traceback.print_exc()
            raise


    def enroll(self,request,context):
        ''' Enrolls the faces in the gallery. '''
        try:
            name = request.gallery_name
            if name not in self.galleries:
                self.galleries[name] = faro.Gallery()
            
            for each in request.records.face_records:
                self.galleries[name].addTemplate( each )
                
            response = fsd.ErrorMessage()
            return response
        except:
            traceback.print_exc()
            raise

    
    def score(self,request,context):
        try:
            start = time.time()
            
            #face_records = request.records
            
            worker_result = self.workers.apply_async(worker_score,[request])
            dist_mat = worker_result.get()
            stop = time.time()

            size = "?X?"
            speed = "? per second"
            try:
                size = "%dX%d"%(len(dist_mat.rows),len(dist_mat.rows[0].data))
                speed = "%0.1f per second"%(len(dist_mat.rows)*len(dist_mat.rows[0].data)/(stop-start))
            except: 
                pass
            notes = ""                        
            notes += "Matrix %s - %s"%(size,speed)

            global LOG_FORMAT
            print(( LOG_FORMAT%(pv.timestamp(),stop-start,"score()",notes)))

            return dist_mat
    
        except:
            traceback.print_exc()
            raise
        
    def echo(self,request,context):
        try:
            start = time.time()
            
            #face_records = request.records
            
            #worker_result = self.workers.apply_async(worker_score,[request])
            #dist_mat = worker_result.get()
            stop = time.time()

            size = "?X?"
            #speed = "? per second"
            try:
                size = "%dX%d"%(len(request.rows),len(request.rows[0].data))
                #speed = "%0.1f per second"%(len(dist_mat.rows)*len(dist_mat.rows[0].data)/(stop-start))
            except: 
                pass
            notes = ""                        
            notes += "Matrix %s"%(size)

            global LOG_FORMAT
            print(( LOG_FORMAT%(pv.timestamp(),stop-start,"echo()",notes)))

            return request
    
        except:
            traceback.print_exc()
            raise
        
    def search(self, request, context):
        '''
        Search a gallery for a face.
        
        request - should be a SearchRequest protobuf.
        
        returns: SearchResponse protobuf
        '''
        try:
            start = time.time()
            result = fsd.SearchResponse()
            name = request.gallery_name
            temp = pt.vector_proto2np(request.face_record.template)
            max_results = request.max_results
            if max_results <= 0:
                max_results = None
            
            data = self.galleries[name].search(temp,max_results=max_results)
            
            for each in data:
                #print "result:",len(each),str(each[0])[:30],str(each[1])[:30]
                result.matches.add().CopyFrom(each[0])
                result.matches[-1].similarity_score = each[1]
                #result.scores.append(each[1])
                #print "   %12.8f: %s"%(each[1],each[0].name)
                
            notes = "Returned %d Results"%(len(result.matches))
            stop = time.time()
            print(( LOG_FORMAT%(pv.timestamp(),stop-start,"search()",notes)))
            return result
        except:
            traceback.print_exc()
            raise
            


    
    def verify(self,face_template,gallery_name):
        ''' Verify a that two face templates are the same person. '''
        
        raise NotImplementedError("'verify' is currently not implemented.")
        
    
    def batchLoad(self,filepath,gallery_name):
        start = time.time()
        f = open(filepath)
        loadinfo = csv.DictReader(f)
        image_count = 0
        face_count = 0
        for each in loadinfo:
            image_count += 1
            #print each
            request = DetectionRequest()
            im = pv.Image(each['image_path'])
            request.image.CopyFrom( pt.image_np2proto(im.asOpenCV2()))#[:,:,::-1]))
            request.options.best=False
            
            detected_faces = self.detectAndExtract(request, None)
            
            if len(detected_faces.face_records) == 1:
                face_count += 1
                request = fsd.EnrollRequest()
                request.gallery_name = gallery_name
                face = detected_faces.face_records[0]
                face.subject_id = each['subject_id']
                face.name = each['name']
                face.source = each['image_path']
                
                request.records.face_records.add().CopyFrom(face)

                #result.face_records[0].name=each['name']
                #result.face_records[0].subject_id=each['subject_id']
                
                self.enroll(request, None)
                
                #print "Added %s to gallery %s"%(each,gallery_name)
            
            else:
                print(( "WARNING: Face not found for image %s."%each))
            stop = time.time()
        notes = "Loaded %d faces from %d images."%(face_count,image_count)
        print(( LOG_FORMAT%(pv.timestamp(),stop-start,"batchLoad()",notes)))

        
    def cleanexit(self):
        ''' Deinitialize commercial softwares. '''
        worker_result = self.workers.apply_async(worker_cleanexit,[])
        worker_result.get()
  
def parseOptions():
    '''
    Parse command line arguments.
    '''
    args = [] # Add the names of arguments here.
    n_args = len(args)
    args = " ".join(args)
    description = '''Scan a directory of images and recognize faces.'''
    epilog = '''Created by David Bolme - bolmeds@ornl.gov'''
    
    version = "0.0.0"
    
    # Setup the parser
    parser = optparse.OptionParser(usage='%s [OPTIONS] %s'%(sys.argv[0],args),version=version,description=description,epilog=epilog)

    # Here are some templates for standard option formats.
    #parser.add_option("-q", "--quiet", action="store_false", dest="verbose", default=True,
    #                 help="Decrease the verbosity of the program")
    
    parser.add_option("--cpu", action="store_true", dest="cpu_mode", default=False,
                      help="When possible run on the cpu and ignore the GPU.")

    #parser.add_option("-b", "--bool", action="store_true", dest="my_bool", default=False,
    #                  help="don't print status messages to stdout")
    
    #parser.add_option( "-c","--choice", type="choice", choices=['c1','c2','c3'], dest="my_choice", default="c1",
    #                  help="Choose an option.")

    ALG_NAMES = list(FACE_WORKER_LIST.keys())
    ALG_NAMES.sort()
    if 'dlib' in ALG_NAMES:
        DEFAULT_ALG_NAME = 'dlib'
    else: # just pick one
        DEFAULT_ALG_NAME = ALG_NAMES[0]
        
    parser.add_option( "--algorithm", type="choice", choices=ALG_NAMES, dest="algorithm", default=DEFAULT_ALG_NAME,
                      help="Choose an algorithm; default=%s - %s"%(DEFAULT_ALG_NAME,ALG_NAMES))

    #parser.add_option( "-f","--float", type="float", dest="my_float", default=0.0,
    #                  help="A floating point value.")

    #parser.add_option( "--match-thresh", type="float", dest="match_thresh", default=0.5218667,
    #                  help="The threshold for a match.")

    #parser.add_option( "-i","--int", type="int", dest="my_int", default=0,
    #                  help="An integer value.")

    parser.add_option( "-w","--worker-count", type="int", dest="worker_count", default=1,
                      help="Specify the number of worker processes.")

    parser.add_option( "--max-message-size", type="int", dest="max_message_size", default=faro.DEFAULT_MAX_MESSAGE_SIZE,
                      help="Maximum GRPC message size. Set to -1 for unlimited. Default=%d"%(faro.DEFAULT_MAX_MESSAGE_SIZE))

    #parser.add_option( "-n","--max-images", type="int", dest="max_images", default=None,
    #                  help="Process at N images and then stop.")

    #parser.add_option( "--min-size", type="int", dest="min_size", default=50,
    #                  help="Faces with a height less that this will be ignored.")

    #parser.add_option( "-s","--str", type="str", dest="my_str", default="default",
    #                  help="A string value.")

    
    parser.add_option( "--storage", type="str", dest="storage_dir", default=faro.DEFAULT_STORAGE_DIR,
                      help="A location to store persistant files. DEFAULT=%s"%faro.DEFAULT_STORAGE_DIR)

    model_options = parser.add_option_group("Options for machine learning models.")
    model_options.add_option( "--detect-model", type="str", dest="detect_model", default='default',
                      help="A model file to use for detection.")

    model_options.add_option( "--extract-model", type="str", dest="extract_model", default='default',
                      help="A model file to use for template extraction.")

    model_options.add_option( "--classify-model", type="str", dest="classify_model", default='default',
                      help="A model file to use for classification.")

    #parser.add_option( "--face-log", type="str", dest="face_log", default=None,
    #                  help="A directory for faces.")

    #parser.add_option( "--match-log", type="str", dest="match_log", default=None,
    #                  help="A directory to store matching faces.")

    #parser.add_option( "-d","--detect-port", type="str", dest="detect_port", default="localhost:50030",
    #                  help="The port used for the recognition service.")

    #parser.add_option( "-r","--recognition-port", type="str", dest="rec_port", default="localhost:50035",
    #                  help="The port used for the recognition service.")

    port = socket.gethostname() + ":50030"

    parser.add_option( "-p","--port", type="str", dest="port", default=port,
                      help="Service port.  Default=%s"%port)



    # Parse the arguments and return the results.
    (options, args) = parser.parse_args()
    
    if len(args) != n_args:
        parser.print_help()
        print()
        print(( "Please supply exactly %d arguments."%n_args ))
        print()
        exit(-1)
        
    return options,args

    
    
def serve():
    print('Configuring Server...')
    
    print('Detecting Workers...')
    
    import_dir = faro.__path__[0]
    scripts = os.listdir(os.path.join(import_dir,'face_workers'))
    scripts = filter(lambda x: x.endswith('FaceWorker.py'),scripts)
    import importlib
    sys.path.append(os.path.join(import_dir,'face_workers'))
    scripts = list(scripts)
    scripts.sort()
    
    for each in scripts:
        module = importlib.import_module(each[:-3])
        class_obj = getattr(module,each[:-3])
        name = each[:-13].lower()
        print("    Loaded: ",name,'-',class_obj)
       
        FACE_WORKER_LIST[name] = [class_obj]
    
    options,_ = parseOptions()
    
    
    print("storage",os.environ['HOME'])
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2*options.worker_count),
                         options=[('grpc.max_send_message_length', options.max_message_size),
                                  ('grpc.max_receive_message_length', options.max_message_size)])
    
    face_client = FaceService(options)
    
    print("Batch loading a watchlist.")
    #face_client.batchLoad("../tests/watchlist.csv", 'authorized')

    fs.add_FaceRecognitionServicer_to_server(face_client, server)

    server.add_insecure_port(options.port)
    print('Starting Server on port: %s'%options.port)
    server.start()
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        face_client.cleanexit()
        server.stop(0)
        print('Sever Stopped.')


if __name__ == '__main__': 
    serve()
    
    
