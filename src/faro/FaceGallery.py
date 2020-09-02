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

Created on Feb 14, 2019

@author: bolme
'''

import numpy as np
import multiprocessing as mp
import numpy as np
import faro
import h5py
import os
import time
import faro.proto.face_service_pb2 as fsd
import scipy.spatial as spat          


import faro.proto.proto_types as pt
from faro.proto.face_service_pb2 import DetectRequest,DetectExtractRequest,ExtractRequest,FaceRecordList,GalleryList,GalleryInfo,Empty,FaceRecord

# TODO: Remove this and make it a local variable
STORAGE = {}
class GalleryWorker(object):

    def __init__(self,options):
        self.gallery_storage = os.path.join(options.storage_dir,'galleries',str(options.algorithm))
        if not os.path.isdir(self.gallery_storage):
            print( 'GALLERY WORKER: Creating directory for gallery storage:',self.gallery_storage)
            os.makedirs(self.gallery_storage)
            
        self.loadGalleries()


    def loadGalleries(self):
        '''Load gallery information into memory on startup.'''
        global STORAGE
        
        galleries = os.listdir(self.gallery_storage)
        
        galleries = list(filter(lambda x: x.endswith('.h5'), galleries))
        
        print("Loading %d galleries: %s"%(len(galleries),galleries))
        for each in galleries:
            gallery_name = each[:-3]
            path = os.path.join(self.gallery_storage,gallery_name+'.h5')
            STORAGE[gallery_name] = h5py.File(path,'a') # Open in read/write mode
            face_count = len(STORAGE[gallery_name]['faces'])

            print("   * Loaded %s with %d faces."%(gallery_name,face_count))
            
        print('Done Loading Galleries.')



    def galleryNames(self):
        return list(STORAGE)



    def size(self, gallery_name):
        ''' Return the size a gallery. '''
        return len(STORAGE[gallery_name]['faces'])





    def addFaceToGallery(self, gallery_name, gallery_key, face):
        ''' Enrolls the faces in the gallery. '''
        global STORAGE

        self.clearIndex(gallery_name)

        replaced = 0

        if gallery_name not in STORAGE:
            path = os.path.join(self.gallery_storage,gallery_name+'.h5')
            STORAGE[gallery_name] = h5py.File(path,'a')
            STORAGE[gallery_name].create_group('faces')
            STORAGE[gallery_name].create_group('sources')
            STORAGE[gallery_name].create_group('detections')
            STORAGE[gallery_name].create_group('tags')
            STORAGE[gallery_name].create_group('logs')

        enrolled = 0

        face_id = faro.generateFaceId(face)
        face.gallery_key = face_id

        enrolled += 1 

        if face_id in STORAGE[gallery_name]['faces']:
            del STORAGE[gallery_name]['faces'][face_id] # delete so it can be replaced.
            replaced += 1
        STORAGE[gallery_name]['faces'][face_id] = np.bytes_(face.SerializeToString())

        template = pt.vector_proto2np(face.template.data)
        temp_length = template.shape[0]

        if 'templates' not in STORAGE[gallery_name]:
            # Create an empty dataset
            f = STORAGE[gallery_name]
            dset = f.create_dataset('templates',data=np.zeros((0,temp_length)), maxshape=(None,temp_length),dtype=np.float32)

        if 'facelist' not in STORAGE[gallery_name]:
            # Create an empty dataset
            f = STORAGE[gallery_name]
            dt = h5py.special_dtype(vlen=str)
            dset = f.create_dataset('facelist',(0,), maxshape=(None,),dtype=dt)

        # Append to the end
        dset = STORAGE[gallery_name]['templates']
        size = dset.shape
        dset.resize((size[0]+1,size[1]))
        dset[-1,:] = template

        dset = STORAGE[gallery_name]['facelist']
        size = dset.shape
        dset.resize((size[0]+1,))
        dset[-1] = face_id

        STORAGE[gallery_name].flush()

        return enrolled, replaced



    def deleteGallery(self, gallery_name):
        ''' Delete a gallery. '''

        if gallery_name not in STORAGE:
            raise ValueError("Gallery '" + gallery_name +"' not found.")

        deleted_faces = len(STORAGE[gallery_name]['faces'])

        # Close and remove the file
        STORAGE[gallery_name].close()
        del STORAGE[gallery_name]

        # Delete the file from disk
        path = os.path.join(self.gallery_storage,gallery_name+'.h5')
        os.remove(path)

        return deleted_faces

    def enrollmentList(self, gallery_name):
        ''' List the faces enrolled in this gallery. '''
        result = FaceRecordList()
           
        global STORAGE
        count = 0
        for face_id in STORAGE[gallery_name]['faces']:
               
            data = STORAGE[gallery_name]['faces'][face_id]
            face_record = FaceRecord()
            face_record.ParseFromString(np.array(data).tobytes())

            face = result.face_records.add()
            face.gallery_key = face_id
            face.name = face_record.name
            face.subject_id = face_record.subject_id
            face.source = face_record.source
            face.frame = face_record.frame
            
            count += 1
        return result

    def subjectDelete(self, gallery_name, subject_id):
        ''' List the galleries for this service. '''
        self.clearIndex(gallery_name)

        if gallery_name not in STORAGE:
            raise ValueError("No gallery named '%s'"%(gallery_name,))

        delete_count = 0 

        keys = list(STORAGE[gallery_name]['faces'])
        for gallery_key in keys:
            tmp = STORAGE[gallery_name]['faces'][gallery_key]
            face = FaceRecord()
            face.ParseFromString(np.array(tmp).tobytes())

            if face.subject_id == subject_id:
                del STORAGE[gallery_name]['faces'][gallery_key]
                delete_count += 1

        self.clearIndex()

        STORAGE[gallery_name].flush()
        
        return delete_count

    def isSearchable(self):
        ''' Return true of the gallery implements fast search. '''
        return False


    def clearIndex(self, gallery_name):
        ''' Remove the index to free space and allow it to be regenerated when needed. '''
        pass


    def generateIndex(self, gallery_name):
        ''' Process the gallery to generate a fast index. '''
        raise NotImplementedError()


    def getAllFaceRecords(self, gallery_name):
        ''' Get all the face records in the gallery. '''
        if gallery_name not in STORAGE:
            raise ValueError("Unknown gallery: "+gallery_name)

        gallery = FaceRecordList()
        for key in STORAGE[gallery_name]['faces']:
            tmp = STORAGE[gallery_name]['faces'][key]
            face = FaceRecord()
            face.ParseFromString(np.array(tmp).tobytes())
            gallery.face_records.add().CopyFrom(face)

        return gallery

    def getFaceRecord(self, gallery_name, face_id):
        ''' Get all the face records in the gallery. '''
        if gallery_name not in STORAGE:
            raise ValueError("Unknown gallery: "+gallery_name)

        tmp = STORAGE[gallery_name]['faces'][face_id]
        face = FaceRecord()
        face.ParseFromString(np.array(tmp).tobytes())

        return face



class SearchableGalleryWorker(GalleryWorker):
    ''' Implements a fast gallery to speed up searches. Requires templates to be simple vectors.'''

    def __init__(self,options,score_type):
        GalleryWorker.__init__(self,options)

        self.score_type = score_type
        self.indexes = {}
        self.face_ids = {}


    def isSearchable(self):
        ''' Return true of the gallery implements fast search. '''
        return True


    def clearIndex(self, gallery_name):
        ''' Remove the index to free space and allow it to be regenerated when needed. '''

        if gallery_name not in STORAGE:
            raise ValueError("Unknown gallery: "+gallery_name)

        try:
            del STORAGE[gallery_name]['index']
        except:
            pass

        try:
            del STORAGE[gallery_name]['face_ids']
        except:
            pass

        try:
            del self.indexes[gallery_name]
        except:
            pass

        try:
            del self.face_ids[gallery_name]
        except:
            pass



    def generateIndex(self, gallery_name):
        ''' Process the gallery to generate a fast index. '''

        #try:
        #    print("Gallery Names:",list(STORAGE[gallery_name]))
        #    self.clearIndex(gallery_name)
        #except:
        #    print("Problem clearing index.")

        if gallery_name not in STORAGE:
            raise ValueError("Unknown gallery: "+gallery_name)

        if gallery_name in self.indexes:
            # This seems to exist and be loaded into memory so just continue
            return 

        if 'index' in STORAGE[gallery_name]:
            # Use the existing index
            self.indexes[gallery_name] = np.array(STORAGE[gallery_name]['index'],dtype=np.float32)
            self.face_ids[gallery_name] = list(STORAGE[gallery_name]['face_ids']) 
            return

        else:
            # Generate the index
            start = time.time()

            gsize = self.size(gallery_name)
            
            dset = None

            print("Building Gallery Index...")
            i = 0
            for key in STORAGE[gallery_name]['faces']:
                i += 1
                if i % 1000 == 0: print("Scanning ",i," of ",gsize)
                tmp = STORAGE[gallery_name]['faces'][key]
                face = FaceRecord()
                face.ParseFromString(np.array(tmp).tobytes())
                vec = pt.vector_proto2np(face.template.data)
                
                # Figure out the size of the vectors
                assert len(vec.shape) == 1
                cols = vec.shape[0]

                # Store into an h5 datasets to keep memory requirements low
                if dset is None:
                    try:
                        del STORAGE[gallery_name]['index']
                    except:
                        pass
                    dset = STORAGE[gallery_name].create_dataset("index", (0,cols), maxshape=(None, cols),dtype='f4')
                    dt = None
                    try:
                        dt = h5py.string_dtype() # h5py > 2.10.0
                    except:
                        dt = h5py.special_dtype(vlen=str) # h5py==2.9.0
                    try:
                        del STORAGE[gallery_name]['face_ids']
                    except:
                        pass
                    fset = STORAGE[gallery_name].create_dataset("face_ids", (0,), maxshape=(None,),dtype=dt)

                r,c = dset.shape
                dset.resize((r+1,cols))
                dset[r,:] = vec
                fset.resize((r+1,))
                fset[r] = key

            stop = time.time()

            # save the index in memory
            self.indexes[gallery_name] = np.array(STORAGE[gallery_name]['index'],dtype=np.float32)
            self.face_ids[gallery_name] = list(STORAGE[gallery_name]['face_ids']) 
            print("   Index Complete: %d faces in %0.3fs  Total Size: %s"%(self.size(gallery_name),stop-start, STORAGE[gallery_name]['index'].shape))


    def search(self, gallery_name, probes, max_results, threshold):
        ''' search the gallery using the index. '''

        score_type = self.score_type

        probe_mat = [pt.vector_proto2np(face_rec.template.data) for face_rec in probes.face_records]
        probe_mat = np.array(probe_mat,dtype=np.float32)

        gal_mat = self.indexes[gallery_name]
                
        # Compute the distance
        if score_type == fsd.L1:
            scores = spat.distance_matrix(probe_mat,gal_mat,1)
        elif score_type == fsd.L2:
            scores = spat.distance_matrix(probe_mat,gal_mat,2)
        elif score_type == fsd.NEG_DOT:
            scores = -np.dot(probe_mat,gal_mat.T)
        else:
            NotImplementedError("ScoreType %s is not implemented."%(score_type,))

        
        face_ids = self.face_ids[gallery_name]

        for p in range(scores.shape[0]):
            #probe = probes.face_records[p]
            #out = result.probes.face_records[p].search_results
            matches = []
            for g in range(scores.shape[1]):
                score = scores[p,g]
                if score > threshold:
                    continue
                face = self.getFaceRecord(gallery_name,face_ids[g])
                matches.append( [ score, face ] )
            
            matches.sort(key=lambda x: x[0])
            
            if max_results > 0:
                matches = matches[:max_results]
            
            for score,face in matches:
                probes.face_records[p].search_results.face_records.add().CopyFrom(face)
                probes.face_records[p].search_results.face_records[-1].score=score


        return probes








