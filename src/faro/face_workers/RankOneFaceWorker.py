'''
Created on August 18th 2020

@author: Nisha Srinivas
'''
import faro
import os
import faro.proto.proto_types as pt 
import faro.proto.face_service_pb2 as fsd
import numpy as np
import pyvision as pv
import time
from PIL import Image
import json
import faro.proto.geometry_pb2 as geo
from array import array


roc = None

def getOptionsGroup(parser):

    rankone_options = parser.add_option_group("Options for RankOne")
    rankone_options.add_option("--img-quality", type=float, dest="img_quality",default=None)
    rankone_options.add_option("--num-faces", type=int, dest="num_faces", default=None)
    rankone_options.add_option("--min-face-size", type=int, dest="min_face_size", default=None)


class RankOneFaceWorker(faro.FaceWorker):
    '''
    classdocs
    '''

    def __init__(self, options):
        '''
        Constructor
        '''

        '''
        Initialize ROC SDK. looks for the license file and optionally we can provide a log file. If it cannot find the license then it will quit. Roc_ensure catches the error and aborts.
        '''
        global roc
        
        import roc as _local_roc
        roc = _local_roc
        
        if os.environ.get('ROC_LIC') is not None: 
            roc.roc_ensure(roc.roc_initialize(None,None))
        else:
            self.license_file = (roc.__file__).split('python')[0] + 'ROC.lic'
            roc.roc_ensure(roc.roc_initialize(self.license_file.encode('utf-8'),None))

        print("ROC SDK Initialized")
        
        self.img_quality = options.img_quality
        self.num_faces = options.num_faces
        self.min_face_size = options.min_face_size
        
        if self.img_quality is None:
            self.img_quality = self.recommendedImgQuality()
        
        if self.num_faces is None:
            self.num_faces = self.recommendedMaxFacesDetected()

        if self.min_face_size is None:
            self.min_face_size = self.recommendedMinFaceSize()

        '''
        ROC_Frontal : ROC frontal face detector (-30 to +30 degress yaw)
        ROC_FR : Represent in-the-wild-faces for comparison
        Note : Non-frontal faces detected by ROC_FULL and ROC_PARTIAL are not reliable for recognition.
        Therefore we advise against using ROC_FULL or ROC_PARTIAL in conjunction with ROC_FR or ROC_ID.
        ROC_FULL : ROC face detector (-100 to +100 degrees yaw)
        ROC_DEMOGRAPHICS - Return age, gender, sex
        ROC_PITCHYAW - Returns yaw and pitch
        '''
        self.algorithm_id_detect = roc.ROC_FULL
        self.algorithm_id_extract = roc.ROC_MANUAL | roc.ROC_FR | roc.ROC_DEMOGRAPHICS | roc.ROC_LANDMARKS | roc.ROC_PITCHYAW
        roc.roc_ensure(roc.roc_preload(self.algorithm_id_detect))
        roc.roc_ensure(roc.roc_preload(self.algorithm_id_extract))

    def _converttoRocImage(self,imgarray):
        #convert to PIL image (This has to be an RGB image)
        image_pillow = Image.fromarray(imgarray)
        #conver PIL to roc image
        image_roc = roc.roc_image()
        image_roc.width = image_pillow.width
        image_roc.height = image_pillow.height
        image_roc.step = 3 * image_pillow.width
        image_roc.color_space = roc.ROC_BGR24
        bytes = 3 * image_pillow.width * image_pillow.height
        image_roc.data = roc.new_uint8_t_array(bytes + 1)
        roc.memmove(image_roc.data, image_pillow.tobytes())
        #RankOne requires a BGR image
        roc.roc_ensure(roc.roc_swap_channels(image_roc))
        roc.roc_write_image(image_roc,'tmp.jpg'.encode('latin-1')) 
        return image_roc
        
        

    def _rocFlatten(self,tmpl):
        '''
        Converts roc template to serialized data.
        Datatype = bytes
        '''
        buffer_size = roc.new_size_t()
        #calculates the bytes required to  a template
        roc.roc_flattened_bytes(tmpl, buffer_size)
        buffer_size_int = roc.size_t_value(buffer_size)
        roc_buffer_src = roc.new_uint8_t_array(buffer_size_int)
        roc.roc_flatten(tmpl, roc_buffer_src)
        native_buffer = roc.cdata(roc_buffer_src, buffer_size_int)
        
        roc.delete_size_t(buffer_size)
        roc.delete_uint8_t_array(roc_buffer_src)
        
        return native_buffer

    def _rocUnFlatten(self, buff,template_dst):
        '''
        Converts serialized data back to roc template.
        '''

        #template_dst = roc.roc_template()
        roc_buffer_dst = roc.new_uint8_t_array(len(buff) + 1)
        roc.memmove(roc_buffer_dst, buff)
        roc.roc_unflatten(roc_buffer_dst, template_dst)
        
        roc.delete_uint8_t_array(roc_buffer_dst)
        
        return template_dst

    def _detect(self,im, opts):
        
        '''
        In RankOne, face detection happends within the roc_represent function.
        There is no explicit face detection step like in dlib. 
        But we will output the bounding box. but it is not really useful in this case.   
        '''

        '''
        Rank one requires the image to be of type roc_image. Hence
        we will check for the image type. In this case it is a numpy array (skimage imread). 
        Check if the image is a numpy array and if it is then conver it to a PIL image and 
        then to a roc_image. The reason I am doing this is cause rankone provides example code 
        to convert from PIL image to  roc_image.
        '''
        h,w,_ = im.shape


        if isinstance(im,np.ndarray):
            im = self._converttoRocImage(im)

        '''
        indicates the smalled face to detect
        Face detection size is measured by the width of the face in pixels. 
        The default value is 36. It roughly correspinds to 18 pixels between the eyes.
        '''
        
        detection_threshold = opts.threshold
        print(opts)
        if opts.best:
            self.num_faces = 1
        print(self.num_faces)
        #create a template array
        templates = roc.new_roc_template_array(self.num_faces)

        #roc_represent performs both face detecion and template generation
        roc.roc_represent(im, self.algorithm_id_detect, self.min_face_size, self.num_faces, detection_threshold, self.img_quality, templates)
        print(templates)
        # we don't need to check for best mode here. If a failed detection occurs then 
        #create a template by manually specifying the bounding box
        # fix the missing detection case
        curr_template = roc.roc_template_array_getitem(templates, 0)
        if (curr_template.algorithm_id == 0 or curr_template.algorithm_id & roc.ROC_INVALID):
            curr_template = roc.roc_template_array_getitem(templates, 0)
            #algorithm_id = self.algorithm_id
            curr_template.detection.x = int(w * 0.5)
            curr_template.detection.y = int(h * 0.5)
            curr_template.detection.width = w
            curr_template.detection.height = h
            roc.roc_template_array_setitem(templates,0,curr_template)


        roc.roc_free_image(im)

        return templates

    def detect(self,img,face_records,options):
        detected_templates = self._detect(img,options) 

        for i in range(0,self.num_faces):
            print(i)
            curr_template = roc.roc_template_array_getitem(detected_templates, i)
            if curr_template.algorithm_id & roc.ROC_INVALID or curr_template.algorithm_id == 0:
                '''
                indicates if a template was created
                '''
                continue
            else:
                face_record = face_records.face_records.add()
                face_record.detection.score = curr_template.detection.confidence
                xc, yc, w, h = curr_template.detection.x, curr_template.detection.y, curr_template.detection.width, curr_template.detection.height
                x = int(xc - (w*0.5))
                y = int(yc - (w*0.5))
                face_record.detection.location.CopyFrom(pt.rect_val2proto(x, y, w, h))
                face_record.detection.detection_id = i
                face_record.detection.detection_class = "FACE"
                print(face_record)
    
        #Free all the roc stuff
        for i in range(0,self.num_faces):
            roc.roc_free_template(roc.roc_template_array_getitem(detected_templates,i))

    def extract(self,img,face_records,options):
        '''
        In RankOne, face detection happends within the roc_represent function.
        There is no explicit face detection step like in dlib. 
        But we will output the bounding box. So we provide a stand alone detection method for RankOne.   
        '''
        detected_templates = self._detect(img,options)

        #check the number of faces detected 

        for i in range(0,self.recommendedMaxFacesDetected()):
            curr_template = roc.roc_template_array_getitem(detected_templates, i)
            if curr_template.algorithm_id & roc.ROC_INVALID or curr_template.algorithm_id == 0:
                '''
                indicates if a template was created
                '''
                continue
            else:
                face_record = face_records.face_records.add()
                face_record.detection.score = curr_template.detection.confidence
                xc, yc, w, h = curr_template.detection.x, curr_template.detection.y, curr_template.detection.width, curr_template.detection.height
                x = int(xc - (w*0.5))
                y = int(yc - (w*0.5))
                face_record.detection.location.CopyFrom(pt.rect_val2proto(x, y, w, h))
                face_record.detection.detection_id = i
                face_record.detection.detection_class = "FACE"   
                '''
                default metadata fields : ChinX,ChinY, IOD (inter-occular distance), LeftEyeX, LeftEyeY, NoseRootX,
                NoseRootY, Path, Pose, Quality, RightEyeX, RightEyeY, Roll
                '''
                metadata_info = json.loads(curr_template.md.decode('utf-8'))
                landmark = face_record.landmarks.add()
                landmark.landmark_id = 'Nose' 
                landmark.location.x = metadata_info['NoseRootX']
                landmark.location.y = metadata_info['NoseRootY']
                
                landmark = face_record.landmarks.add()
                landmark.landmark_id = 'LeftEye' 
                landmark.location.x = metadata_info['LeftEyeX']
                landmark.location.y = metadata_info['LeftEyeY']

                landmark = face_record.landmarks.add()
                landmark.landmark_id = 'RightEye'
                landmark.location.x = metadata_info['RightEyeX']
                landmark.location.y = metadata_info['RightEyeY']

                landmark = face_record.landmarks.add()
                landmark.landmark_id = 'ChinX'
                landmark.location.x = metadata_info['ChinX']
                landmark.location.y = metadata_info['ChinY']
                
                demographic = face_record.attributes.add()
                demographic.key = 'Age'
                demographic.text = str(metadata_info['Age'])
                
                demographic = face_record.attributes.add()
                demographic.key = 'Gender'
                demographic.text = metadata_info['Gender']

                demographic = face_record.attributes.add()
                demographic.key = 'GeographicOrigin'
                demographic.text = metadata_info['GeographicOrigin']

                demographic = face_record.attributes.add()
                demographic.key = 'Emotion'
                demographic.text = metadata_info['Emotion']

                demographic = face_record.attributes.add()
                demographic.key = 'Artwork'
                demographic.text = metadata_info['Artwork']

                demographic = face_record.attributes.add()
                demographic.key = 'Yaw'
                demographic.text = str(metadata_info['Yaw'])
 
                face_record.template.buffer = self._rocFlatten(curr_template)                       
        
        #Free all the roc stuff
        for i in range(0,self.recommendedMaxFacesDetected()):
            roc.roc_free_template(roc.roc_template_array_getitem(detected_templates,i)) 
       
            
            
    def locate(self,img,face_records,options):
        '''
        Not needed as we find the location of the eyes, nose and chin during detection and have 
        added it to face records during detection
        '''
        pass
        
        
        
    def align(self,image,face_records):
        '''Align the images to a standard size and orientation to allow 
        recognition.'''
        pass # Not needed for this algorithm.
            
        
    def scoreType(self):
        '''Return the method used to create a score from the template.
        
        By default server computation is required.
        
        SCORE_L1, SCORE_L2, SCORE_DOT, SCORE_SERVER
        '''
        return fsd.SERVER
    
   
    def score(self,score_request):
        '''Compare templates to produce scores.'''
        score_type = self.scoreType()
        result = geo.Matrix()

        # Check that this is a known score type
        if score_type not in [fsd.SERVER]:
            raise NotImplementedError("Score type <%s> not implemented."%(score_type,))

        # Check to make sure the probe and gallery records are correct
        if len(score_request.template_probes.templates) == 0:
            raise ValueError("no probe templates were found in the arguments.")

        if len(score_request.template_gallery.templates) == 0:
            raise ValueError("no gallery templates were found in the arguments.")
        
        #THIS IS NOT NECESSAY AS WE ARE ALWAYS COPYING THE TEMPLATES AND NOT USING FACE RECORD -> REFER TO 
        #FUNCTION in FaceClient.py
        
        '''
        if min(len(score_request.face_probes.face_records),len(score_request.template_probes.templates)) != 0:
            raise ValueError("probes argument cannot have both face_probes and template_probes defined.")
        if max(len(score_request.face_probes.face_records),len(score_request.template_probes.templates)) == 0:
            raise ValueError("no probe templates were found in the arguments.")
        if min(len(score_request.face_gallery.face_records),len(score_request.template_gallery.templates)) != 0:
            raise ValueError("gallery argument cannot have both face_gallery and template_gallery defined.")
        if max(len(score_request.face_gallery.face_records),len(score_request.template_gallery.templates)) == 0:
            raise ValueError("no gallery templates were found in the arguments.")
        '''

        #This is the first attempt at computing similarity scores. This is definitely not the fastest approach.
        #Also , this is going to be restricted by  memory. The whole similarity matrix be be held in memory.
        #So for large datasets this might pose a problem

        
        if score_type == fsd.SERVER:
            #rows = probe images
            #cols = gallery images
            sim_mat = np.zeros((len(score_request.template_probes.templates),len(score_request.template_gallery.templates)),dtype=np.float32)
           
            roc_probe_template = roc.roc_template() 
            roc_gallery_template_array = roc.new_roc_template_array(len(score_request.template_gallery.templates))
            sm_metric = roc.new_roc_similarity()
            for p in range(0,len(score_request.template_probes.templates)):
                self._rocUnFlatten(score_request.template_probes.templates[p].buffer,roc_probe_template)
                #print roc_probe_template
                for g in range(0,len(score_request.template_gallery.templates)):
                    #print(p,g)
                    if p == 0:
                        roc_gallery_template = roc.roc_template()
                        self._rocUnFlatten(score_request.template_gallery.templates[g].buffer,roc_gallery_template)
                        roc.roc_template_array_setitem(roc_gallery_template_array,g,roc_gallery_template)
                        
                    roc.roc_compare_templates(roc_probe_template, roc.roc_template_array_getitem(roc_gallery_template_array,g), sm_metric)
                    sim_mat[p,g] = roc.roc_similarity_value(sm_metric)
            roc.delete_roc_similarity(sm_metric)        
            roc.roc_free_template(roc_probe_template)
            for i in range(len(score_request.template_gallery.templates)):
                #print(i)
                roc.roc_ensure(roc.roc_free_template(roc.roc_template_array_getitem(roc_gallery_template_array, i)))
    
        else:
            NotImplementedError("ScoreType %s is not implemented."%(score_type,))

        #RankOne returns a similarity score of -1 if it compares with an invalid template
        #Threfore find all -1's in the matrix and replace it with a 0

        sim_mat[sim_mat == -1.0] = 0.0
        #converting the simialrity matrix to distance matrix by subtracting with 1
        dist_mat = 1.0 - sim_mat
        # Return the result
        return pt.matrix_np2proto(dist_mat)
     
    def status(self):
        '''Return a simple status message.'''
        print("Handeling status request.")
        status_message = fsd.FaceServiceInfo()
        status_message.status = fsd.READY
        status_message.detection_support = True
        status_message.extract_support = True
        status_message.score_support = False
        status_message.score_type = self.scoreType()
        status_message.detection_threshold = self.recommendedDetectionThreshold();
        status_message.match_threshold = self.recommendedScoreThreshold();
        status_message.algorithm = "RankOne_%s"%(roc.__file__);

        
        return status_message
        
    def recommendedImgQuality(self):
                
        return roc.ROC_SUGGESTED_MIN_QUALITY
 
    def recommendedDetectionThreshold(self):
        '''
        The false_detection_rate parameter specifies the allowable 
        false positive rate for face detection.The suggested default 
        value for false_detection_rate is 0.02 which corresponds to 
        one false detection in 50 images on the FDDB benchmark. A 
        higher false detection rate will correctly detect more faces 
        at the cost of also incorrectly detecting more non-faces. 
        The accepted range of values for false_detection_rate is 
        between 0 to 1. Values outside this range will be modified 
        to be at the aforementioned bounds automatically.
        
        '''
        
        return 0.02

    def recommendedMaxFacesDetected(self):
        
        return 10

    def recommendedMinFaceSize(self):
        
        return 64

    def recommendedScoreThreshold(self,far=-1):
        '''Return the method used to create a score from the template.
        
        By default server computation is required.
        
        Should return a recommended score threshold.
        
        DLIB recommends a value of 0.6 for LFW dataset    
        '''
        
        return 0.60

    def cleanexit(self):
        print('ROC SDK Deinitialized')
        roc.roc_finalize()
        
        

