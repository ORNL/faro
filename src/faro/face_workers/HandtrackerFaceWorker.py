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

Created on April 7th, 2019

@author: srinivasn1
@ORNL
'''

import faro
import os
import faro.proto.proto_types as pt 
import faro.proto.face_service_pb2 as fsd
import numpy as np
import pyvision as pv
from google.protobuf import text_format
from faro.proto import string_int_label_map_pb2 
from PIL import Image

class HandtrackerFaceWorker(faro.FaceWorker):
    '''
    classdocs
    '''

    def __init__(self, options):
        '''
        Constructor
        '''
        import warnings
        warnings.filterwarnings('ignore', category=DeprecationWarning)
        warnings.filterwarnings('ignore', category=FutureWarning)
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
        global tf
        import tensorflow as _local_tf
        tf = _local_tf
        self.model_name = os.path.join(options.storage_dir,'models',  'hand_inference_graph')
        self.path_to_ckpt = os.path.join(self.model_name, 'frozen_inference_graph.pb')
        self.path_to_labels = os.path.join(self.model_name, 'hand_label_map.pbtxt')
        
        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(self.path_to_ckpt, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')
            self.sess = tf.Session(graph=self.detection_graph)
        print("Hand Tracking Inference graph loaded.")

        self.num_classes = 1
        #load label map
        self.label_map = self._load_labelmap(self.path_to_labels)
        self.categories = self._convert_label_map_to_categories(self.label_map, max_num_classes=self.num_classes, use_display_name=True)
        self.category_index = self._create_category_index(self.categories)
        print("End of Initilialization")

    def _convert_label_map_to_categories(self, label_map,max_num_classes, use_display_name=True):
        """Loads label map proto and returns categories list compatible with eval.
        This function loads a label map and returns a list of dicts, each of which
        has the following keys:
          'id': (required) an integer id uniquely identifying this category.
          'name': (required) string representing category name
            e.g., 'cat', 'dog', 'pizza'.
        We only allow class into the list if its id-label_id_offset is
        between 0 (inclusive) and max_num_classes (exclusive).
        If there are several items mapping to the same id in the label map,
        we will only keep the first one in the categories list.
        Args:
          label_map: a StringIntLabelMapProto or None.  If None, a default categories
            list is created with max_num_classes categories.
          max_num_classes: maximum number of (consecutive) label indices to include.
          use_display_name: (boolean) choose whether to load 'display_name' field
            as category name.  If False or if the display_name field does not exist,
            uses 'name' field as category names instead.
        Returns:
          categories: a list of dictionaries representing all possible categories.
        """
        categories = []
        list_of_ids_already_added = []
        if not label_map:
            label_id_offset = 1
            for class_id in range(max_num_classes):
                categories.append({
                    'id': class_id + label_id_offset,
                    'name': 'category_{}'.format(class_id + label_id_offset)
                })
            return categories
        for item in label_map.item:
            if not 0 < item.id <= max_num_classes:
                logging.info('Ignore item %d since it falls outside of requested '
                             'label range.', item.id)
                continue
            if use_display_name and item.HasField('display_name'):
                name = item.display_name
            else:
                name = item.name
            if item.id not in list_of_ids_already_added:
                list_of_ids_already_added.append(item.id)
                categories.append({'id': item.id, 'name': name})
        return categories
    
    def _create_category_index(self, categories):
        """Creates dictionary of COCO compatible categories keyed by category id.
        Args:
          categories: a list of dicts, each of which has the following keys:
            'id': (required) an integer id uniquely identifying this category.
            'name': (required) string representing category name
              e.g., 'cat', 'dog', 'pizza'.
        Returns:
          category_index: a dict containing the same entries as categories, but keyed
            by the 'id' field of each category.
        """
        category_index = {}
        for cat in categories:
            category_index[cat['id']] = cat
        return category_index

    def _validate_label_map(self, label_map):
        """Checks if a label map is valid.
        Args:
          label_map: StringIntLabelMap to validate.
        Raises:
          ValueError: if label map is invalid.
        """
        for item in label_map.item:
            if item.id < 1:
                raise ValueError('Label map ids should be >= 1.')

    def _load_labelmap(self, path):
        """Loads label map proto.
        Args:
          path: path to StringIntLabelMap proto text file.
        Returns:
          a StringIntLabelMapProto
        """
        with tf.gfile.GFile(path, 'r') as fid:
            label_map_string = fid.read()
            label_map = string_int_label_map_pb2.StringIntLabelMap()
            try:
                text_format.Merge(label_map_string, label_map)
            except text_format.ParseError:
                label_map.ParseFromString(label_map_string)
        self._validate_label_map(label_map)
        return label_map
    
    def detect(self,img,face_records,options):
        im_height, im_width, channels = img.shape 
        image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
        # Each box represents a part of the image where a particular object was detected.
        detection_boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
        # Each score represent how level of confidence for each of the objects.
        # Score is shown on the result image, together with the class label.
        detection_scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
        detection_classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
        num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')
        image_np_expanded = np.expand_dims(img, axis=0)
        (boxes, scores, classes, num) = self.sess.run([detection_boxes, detection_scores,detection_classes, num_detections], feed_dict={image_tensor: image_np_expanded})
        boxes = np.squeeze(boxes)
        scores = np.squeeze(scores)
        scores = scores.reshape((scores.shape[0], 1))
        #print(scores)
        detections = np.concatenate((boxes, scores), axis=1)
        final_detections = detections[detections[:, 4] > options.threshold]
        for idx in range(final_detections.shape[0]):
        #for idx in range(0,2):
            face_record = face_records.face_records.add()
            ymin, xmin, ymax, xmax, score = final_detections[idx]
            (left, right, top, bottom) = (xmin * im_width, xmax * im_width, ymin * im_height, ymax * im_height) 
            ulx, uly = (int(left), int(top))
            lrx, lry = (int(right), int(bottom))
            face_record.detection.score = score
            face_record.detection.location.CopyFrom(pt.rect_val2proto(ulx, uly, abs(lrx-ulx), abs(lry-uly)))
            face_record.detection.detection_id = idx
            face_record.detection.detection_class = "HAND_%d"%idx
         
    def locate(self,img,face_records,options):
        '''Locate facial features.'''
        pass 

    def align(self,image,face_records):
        '''Align the images to a standard size and orientation to allow 
        recognition.'''
        pass 
            
    def extract(self,img,face_records):
        '''Extract a template that allows the face to be matched.'''
        pass
                
    def scoreType(self):
        '''Return the method used to create a score from the template.
        
        By default server computation is required.
        
        SCORE_L1, SCORE_L2, SCORE_DOT, SCORE_SERVER
        '''
        pass
 
    def status(self):
        '''Return a simple status message.'''
        print("Handeling status request.")
        status_message = fsd.FaceServiceInfo()
        status_message.status = fsd.READY
        status_message.detection_support = True
        status_message.extract_support = False
        status_message.score_support = False
        status_message.detection_threshold = self.recommendedDetectionThreshold()
        status_message.algorithm = "Hand tracker - Real-time Hand-Detection using Neural Networks (SSD) on Tensorflow."

        
        return status_message
        

    def recommendedDetectionThreshold(self):
        #according to the github repo
        return 0.2

    def recommendedScoreThreshold(self,far=-1):
       
        '''
        Not required
        '''
         
        return None


