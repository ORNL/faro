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
import faro.proto.proto_types as pt
from faro.proto.face_service_pb2 import DetectRequest,DetectExtractRequest,ExtractRequest,FaceRecordList
import csv
import multiprocessing as mp
import optparse
import sys
import socket
import faro
import os
import h5py


LOG_FORMAT = "%-20s: %8.4fs: %-15s - %s"
#FFD = dlib.get_frontal_face_detector()



FACE_ALG = None
        
FACE_WORKER_LIST = {}     


WORKER_GPU_MAPPING = {}
GALLERIES = {}
STORAGE = {}

def filterDetectMinSize(face_records, min_size):
    if min_size is not None:
        # iterate through the list in reverse order because we are deleting as we go
        for i in range(len(face_records.face_records))[::-1]:
            if face_records.face_records[i].detection.location.width < min_size:
                del face_records.face_records[i]
    return face_records
        
def filterDetectBest(face_records, im, best):
    # TODO: This is a temporary fix.
    if best and len(face_records.face_records) > 1:
        print( "WARNING: detector service does not seem to support best mode.  To many faces returned." )
        face_records.face_records.sort(key=lambda x: -x.detection.score)
        #print(detections.detections)
        while len(face_records.face_records) > 1:
            del face_records.face_records[-1]
            
        assert len(face_records.face_records) == 1
    
    if best and len(face_records.face_records) == 0:
        print( "WARNING: detector service does not seem to support best mode.  No faces returned." )
        
        # in this case select the center of the image
        det = face_records.face_records.add().detection
        h,w = im.shape[:2]
        s = 0.8*min(w,h)
        det.location.CopyFrom(pt.rect_val2proto(0.5*w-0.5*s,0.5*h-0.5*s, s, s))
        det.score = -1.0 
        
        det.detection_id = 1
        
        assert len(face_records.face_records) == 1     
        
    return face_records       
   

def worker_init(options):
    ''' Initalize the worker processes. '''
    
    print("Starting worker process:",mp.current_process())
    
    global MYNET,WORKER_INDEX,OPTIONS
    global FACE_WORKER_LIST
    global WORKER_GPU_MAPPING

    #cfg.TEST.HAS_RPN = True  # Use RPN for proposals
    proc = mp.current_process()
    WORKER_INDEX = (int(proc.name.split('-')[-1])-1)%options.worker_count

    OPTIONS = options
 
    assert WORKER_INDEX >= 0
    if options.gpus is not "":
        # This should rotate through the gpus selected for each worker
        gpus = [each for each in options.gpus.split(',')]
        gpu_id = gpus[WORKER_INDEX%len(gpus)]
        options.gpuid = gpu_id
        WORKER_GPU_MAPPING[WORKER_INDEX] = gpu_id
        os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID" 
        os.environ["CUDA_VISIBLE_DEVICES"] = gpu_id
    else:
        options.gpuid = -1    
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
    global WORKER_GPU_MAPPING
    assert FACE_ALG is not None
    try:
        # uncomment this line to check that the image is comming through properly.
        # skimage.io.imsave('/tmp/test.png', mat)
        face_record_list = FaceRecordList()
        FACE_ALG.detect(mat,face_record_list,options)
        
        filterDetectMinSize(face_record_list, options.min_size)
        filterDetectBest(face_record_list, mat, options.best)
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
        
        self.gallery_storage = os.path.join(options.storage_dir,'galleries',str(options.algorithm))
        if not os.path.isdir(self.gallery_storage):
            print( 'Creating directory for gallery storage:',self.gallery_storage)
            os.makedirs(self.gallery_storage)
            
        self.loadGalleries()
        
    def loadGalleries(self):
        '''Load gallery information into memory on startup.'''
        global STORAGE, GALLERIES
        
        galleries = os.listdir(self.gallery_storage)
        
        galleries = list(filter(lambda x: x.endswith('.h5'), galleries))
        
        print("Loading %d galleries: %s"%(len(galleries),galleries))
        for each in galleries:
            gallery_name = each[:-3]
            path = os.path.join(self.gallery_storage,gallery_name+'.h5')
            STORAGE[gallery_name] = h5py.File(path)
            GALLERIES[gallery_name] = {}
            
            #print(each,gallery_name,path)
            #print(list(STORAGE[gallery_name]))
            for each in STORAGE[gallery_name]:
                data = STORAGE[gallery_name][each]
                #print(data)
                fr = fsd.FaceRecord()
                #print(data)
                #print(dir(data))
                #print(list(data))
                fr.ParseFromString(np.array(data).tobytes())
                #print(each,fr)
                GALLERIES[gallery_name][each] = fr
        print('Done Loading Galleries.')

                
            
        
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
            options = request.detect_options
            notes = "Image Size %s"%(mat.shape,)
            #print('time_check AA:',time.time()-start)
            worker_result = self.workers.apply_async(worker_detect,[mat,options])
            #print('time_check BB:',time.time()-start)
            face_records_list = worker_result.get()
            
            notes += ", Detections %s"%(len(face_records_list.face_records),)
            #print('time_check CC:',time.time()-start)
                        
            for face in face_records_list.face_records:
                face.source = request.source
                face.frame = request.frame
                face.subject_id = request.subject_id
                face.name = request.subject_name
                            
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
            start = time.time()
            
            gallery_name = request.enroll_gallery
            
            global GALLERIES, STORAGE

            if gallery_name not in GALLERIES:
                print("Creating gallery",gallery_name)
                GALLERIES[gallery_name] = {}
                
                path = os.path.join(self.gallery_storage,gallery_name+'.h5')
                STORAGE[gallery_name] = h5py.File(path)

            count = 0
            for face in request.records.face_records:
                face_id = faro.generateFaceId(face)
                face.gallery_key = face_id
                #face_id = "-".join(face_id.split('/'))
                #print('face_id:',face_id)
                count += 1 
                GALLERIES[gallery_name][face_id] = face
                if face_id in STORAGE[gallery_name]:
                    del STORAGE[gallery_name][face_id] # delete so it can be replaced.
                STORAGE[gallery_name][face_id] = np.bytes_(face.SerializeToString())
                STORAGE[gallery_name].flush()
                
            #response = fsd.ErrorMessage()

            stop = time.time()
            notes = "Enrolled %d faces into gallery '%s'.  Gallery size = %d."%(count,gallery_name,len(GALLERIES[gallery_name]))
            global LOG_FORMAT
            print(( LOG_FORMAT%(pv.timestamp(),stop-start,"enroll()",notes)))

            return request.records
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
            #result = fsd.SearchResponse()
            #result.probes.CopyFrom(request.probes)

            # Collect the options
            search_gallery = request.search_gallery
            probes = request.probes
            max_results = request.max_results
            threshold = request.threshold
            
            if search_gallery not in GALLERIES:
                raise ValueError("Unknown gallery: "+search_gallery)
            
            gallery = fsd.FaceRecordList()
            for key in GALLERIES[search_gallery]:
                face = GALLERIES[search_gallery][key]
                gallery.face_records.add().CopyFrom(face)
                
            score_request = fsd.ScoreRequest()
            score_request.face_probes.CopyFrom(probes)
            score_request.face_gallery.CopyFrom(gallery)
            
            # Compute the scores matrix
            scores = self.score(score_request,None)
            scores = pt.matrix_proto2np(scores)
            
            matched = 0
            for p in range(scores.shape[0]):
                #probe = probes.face_records[p]
                #out = result.probes.face_records[p].search_results
                matches = []
                for g in range(scores.shape[1]):
                    score = scores[p,g]
                    if score > threshold:
                        continue
                    matches.append( [ score, gallery.face_records[g] ] )
                
                matches.sort(key=lambda x: x[0])
                
                if max_results > 0:
                    matches = matches[:max_results]
                    matched += 1
                
                for score,face in matches:
                    probes.face_records[p].search_results.face_records.add().CopyFrom(face)
                    probes.face_records[p].search_results.face_records[-1].score=score
                    
            # Count the matches
            count = len(probes.face_records)
            notes = "Processed %d probes. %d matched."%(count,matched)
            stop = time.time()
            print(( LOG_FORMAT%(pv.timestamp(),stop-start,"search()",notes)))
            return probes
        except:
            traceback.print_exc()
            raise
            


    
    def verify(self,face_template,gallery_name):
        ''' Verify a that two face templates are the same person. '''
        
        raise NotImplementedError("'verify' is currently not implemented.")
        

    def detectExtract(self,request,context):
        ''' runs the face detector and extraction in one call and returns extracted faces. '''
        try:
            # Run detection
            face_records_list = self.detect(request.detect_request,context)
            
            # Run extract
            extract_request = request.extract_request
            extract_request.image.CopyFrom( request.detect_request.image )
            extract_request.records.CopyFrom(face_records_list)
            
            face_records_list = self.extract(extract_request, context)
            
            return face_records_list
        except:
            traceback.print_exc()
            raise
    

    def detectExtractEnroll(self,request,context):
        ''' runs the face detector and extraction in one call and returns extracted faces. '''
        try:
            # Run detection
            face_records_list = self.detect(request.detect_request,context)
            
            # Run extract
            extract_request = request.extract_request
            extract_request.image.CopyFrom( request.detect_request.image )
            extract_request.records.CopyFrom(face_records_list)
            
            face_records_list = self.extract(extract_request, context)
            
            enroll_request = request.enroll_request
            enroll_request.records.CopyFrom(face_records_list)
            
            results = self.enroll(enroll_request, context)
            
            #print("enroll result",results)
            
            return results
        except:
            traceback.print_exc()
            raise
    

    def detectExtractSearch(self,request,context):
        ''' runs the face detector and extraction in one call and returns extracted faces. '''
        try:
            # Run detection
            face_records_list = self.detect(request.detect_request,context)
            
            # Run extract
            extract_request = request.extract_request
            extract_request.image.CopyFrom( request.detect_request.image )
            extract_request.records.CopyFrom(face_records_list)
            
            face_records_list = self.extract(extract_request, context)
            
            search_request = request.search_request
            search_request.probes.CopyFrom(face_records_list)
            
            face_records_list = self.search(search_request, context)
            
            return face_records_list
        except:
            traceback.print_exc()
            raise
    


        
    def cleanexit(self):
        ''' Deinitialize commercial softwares. '''
        worker_result = self.workers.apply_async(worker_cleanexit,[])
        worker_result.get()
  
def parseOptions(face_workers_list):
    '''
    Parse command line arguments.
    '''
    args = [] # Add the names of arguments here.
    n_args = len(args)
    args = " ".join(args)
    description = '''Scan a directory of images and recognize faces.  To scan for new face workers add python files ending with FaceWorker.py to a directory and add the directory to an environment variable called FARO_WORKER_PATH. '''
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

    parser.add_option( "--gpus", type="str", dest="gpus", default="",
                      help="Specify the gpus to use.")

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
    
    for key in face_workers_list:
        if face_workers_list[key][1] is not None:
            face_workers_list[key][1](parser)



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
    
    # Scan for faro workers
    import_dir = faro.__path__[0]
    scripts = os.listdir(os.path.join(import_dir,'face_workers'))
    scripts = filter(lambda x: x.endswith('FaceWorker.py'),scripts)
    import importlib
    sys.path.append(os.path.join(import_dir,'face_workers'))
    scripts = list(scripts)
    scripts.sort()
    
    print('scripts1',scripts)
    
    # Scan for other workers
    if 'FARO_WORKER_PATH' in os.environ:
        worker_dirs = os.environ['FARO_WORKER_PATH'].split(":")
        print("Workers Dirs:",worker_dirs)
        for worker_dir in worker_dirs:
    
            #import_dir = faro.__path__[0]
            try:
                worker_scripts = os.listdir(worker_dir)
            except:
                print("ERROR - Could not read directory in FARO_WORKER_PATH:", worker_dir)
                raise
            worker_scripts = list(filter(lambda x: x.endswith('FaceWorker.py'),worker_scripts))
            sys.path.append(worker_dir)
            scripts += list(worker_scripts)
            scripts.sort()
            
    print('scripts2',scripts)
    
    for each in scripts:
        module = importlib.import_module(each[:-3])
        class_obj = getattr(module,each[:-3])
        name = each[:-13].lower()
        print("    Loaded: ",name,'-',class_obj)
       
        FACE_WORKER_LIST[name] = [class_obj,None]
        if 'getOptionsGroup' in dir(module):
            FACE_WORKER_LIST[name][1] = module.getOptionsGroup
    
    options,_ = parseOptions(FACE_WORKER_LIST)
    
    
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
        print('Server Stopped.')


if __name__ == '__main__': 
    serve()
    
    
