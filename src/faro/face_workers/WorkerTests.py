import unittest
import faro
import faro.proto.proto_types as pt
import faro.proto.face_service_pb2 as fsd
import faro.pyvision
class FaroDetectionOptions(object):
    #user could change these variable : User-defined variables
    def __init__(self):
        #root file
        self.results_root_path = '/home/2r6/Projects/maa/results'
        self.csvfiles_log = 'csvfiles_log'
        #Directory to save images with bounding boxes
        self.detect_log = 'detect_log'
        #Directory to save cropped face images (128*128)
        self.face_log = 'face_log'

        #Set to True if you want to save only the detection with
        #the highest detection score (confidence)
        self.best = False
        #Detection Thresh - Retinaface uses 0.5 in their examples
        self.detect_thresh = 0.5
        #Set min size. If the bouding box of the face detected is
        #less that min_size then it will be discarded.
        self.min_size = 0
        #Set the maximum number of images it can process
        self.max_images = None
        self.max_size = 250


class FaroClientConnectionOptions(object):

    def __init__(self):
        self.max_async = faro.DEFAULT_MAX_ASYNC
        self.max_message_size = faro.DEFAULT_MAX_MESSAGE_SIZE
        self.detect_port = faro.DEFAULT_PORT
        self.rec_port = faro.DEFAULT_PORT
        self.port = 'localhost:50030'
        self.certificate = None
        self.service_name = None
        self.compression = 'uint8'
        self.quality = 100
        self.verbose = True
class WorkerTest(unittest.TestCase):
    from faro.FaceService import FaceService
    local_service : FaceService = None
    client : faro.FaceClient = None
    cache = {}
    # def __init__(self,testName,local_service = None):
    #     super(WorkerTest,self).__init__(testName)
    #     self.local_service = local_service
    def setUp(self) -> None:
        pass


    def testStatus(self):
        print('running status test...')
        request = fsd.FaceStatusRequest()
        status_message = self.local_service.status(request,None)
        self.assertTrue(status_message is not None)
        self.assertTrue(status_message.detection_support or (status_message.extraction_support and status_message.score_support))
        self.assertIsNotNone(status_message.score_type)
        self.assertGreater(status_message.worker_count,0)
        self.assertIsNotNone(status_message.algorithm)
        self.assertIsNotNone(status_message.faro_version)
        self.assertGreaterEqual(int(status_message.faro_version.split('.')[0]), 1)
        self.assertGreaterEqual(int(status_message.faro_version.split('.')[1]), 1)

    def testDetect(self):
        self.assertTrue(self.client.info.detection_support)
        if self.client.info.detection_support == True:
            print('running detection test...')
            det_options = FaroDetectionOptions()
            im = faro.pyvision.Image(faro.pyvision.LENA)

            faces = self.client.detect(im)
            num_faces = len(faces.face_records)
            print('found',num_faces,'faces in the default LENA image')
            self.assertEquals(num_faces,1, "Checking if service implementation detects exactly one face")
    def testNoDetect(self):
        print('running detection test...')
        self.assertTrue(self.client.info.detection_support)
        if self.client.info.detection_support == True:
            det_options = FaroDetectionOptions()
            im = faro.pyvision.Image(faro.pyvision.FRUITS)

            faces = self.client.detect(im)

            num_faces = len(faces.face_records)
            print('found',num_faces,'faces in an image of fruit')
            self.assertEquals(num_faces,0, "Checking if service implementation correctly detects 0 faces")
    def testExtract(self):
        print('running feature extraction test...')
        self.assertTrue(self.client.info.extract_support)
        if self.client.info.extract_support == True:
            im = faro.pyvision.Image(faro.pyvision.LENA)
            cvim = im.asOpenCV2()[:, ::-1, :]
            im_mirror = faro.pyvision.Image(cvim)

            faces = self.client.detect(im)
            faces = self.client.extract(im, faces)

            faces2 = self.client.detect(im_mirror)
            faces2 = self.client.extract(im_mirror, faces)

            vect1 = pt.vector_proto2np(faces.face_records[0].template.data)
            vect2 = pt.vector_proto2np(faces2.face_records[0].template.data)
            self.assertEquals(len(faces.face_records),1,"Checking if service implementation extracts exactly one face from original image")
            self.assertEquals(len(faces2.face_records), 1, "Checking if service implementation extracts exactly one face from mirrored image")
            self.assertGreater(len(vect1),0,"making sure extractd vector 1 is not of lenght 0")
            self.assertGreater(len(vect2), 0, "making sure extractd vector 2 is not of lenght 0")
            self.assertFalse((vect1==vect2).all(),"making sure extracted vector 1 and 2 are not equal")
            self.cache['im1_faces'] = faces
            self.cache['im2_faces'] = faces2
    def testMatch(self):
        print('running match scoring test...')
        if self.client.info.score_support:
            score_self = self.client.score(self.cache['im1_faces'].face_records, self.cache['im1_faces'].face_records)
            score_mirror = self.client.score(self.cache['im1_faces'].face_records, self.cache['im2_faces'].face_records)
            self.assertEquals(score_self.shape[0],1)
            self.assertEquals(score_self.shape[1], 1)
            self.assertEquals(score_mirror.shape[0], 1)
            self.assertEquals(score_mirror.shape[1], 1)
            if self.client.info.score_type == fsd.ScoreType.L2 or self.client.info.score_type == fsd.ScoreType.L1:
                self.assertLessEqual(score_self[0,0], score_mirror[0,0],"Checking if the scoring algorithm provides a higher score (distance) for the mirrored match")
                try:
                    self.assertLessEqual(score_mirror[0,0],self.client.info.match_threshold, "Checking if the face match distance is less than the match threshold (which would indicate a match)")
                except:
                    self.assertAlmostEqual(score_mirror[0, 0], self.client.info.match_threshold,1,
                                           "Checking if the face match score is at least close to the the match threshold")
            else:
                self.assertGreaterEqual(score_self[0,0],score_mirror[0,0],"Checking if the scoring algorithm provides a higher score for the self match")
                try:
                    self.assertGreaterEqual(score_mirror[0, 0], self.client.info.match_threshold, "Checking if the face match score is greater than the match threshold (which would indicate a match)")
                except:
                    self.assertAlmostEqual(score_mirror[0, 0], self.client.info.match_threshold,1,
                                           "Checking if the face match score is at least close to the the match threshold")


def run_local_tests(local_service_instance,options=None):
    WorkerTest.local_service = local_service_instance
    if options is None:
        con_options = FaroClientConnectionOptions()

    else:
        con_options = options
    client = faro.FaceClient(con_options,local_service=local_service_instance)
    WorkerTest.client = client
    suite = unittest.makeSuite(WorkerTest)
    # suite.addTest(WorkerTest())
    # suite.addTests(WorkerTest)
    try:
        import colour_runner.runner
        textrunner = colour_runner.runner.ColourTextTestRunner
    except:
        print('fallback')
        textrunner = unittest.TextTestRunner
    textrunner(verbosity=2).run(suite)
    # unittest.main(__name__)