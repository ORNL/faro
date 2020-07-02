'''
Created on Dec 3, 2019 at Oak Ridge National Laboratory

@author: qdb
'''
import sys
import optparse
import os

import faro
import pyvision as pv
import cv2
import faro.proto.proto_types as pt
import csv
from faro.proto.face_service_pb2 import FaceRecordList,GalleryListRequest
import time

FACE_COUNT = 0


def addConnectionOptions(parser):
    """
    Add options for connecting to the faro service.
    """

    connection_group = optparse.OptionGroup(parser, "Connection Options",
                                            "Control the connection to the FaRO service.")

    connection_group.add_option("--max-async", type="int", dest="max_async", default=faro.DEFAULT_MAX_ASYNC,
                                help="The maximum number of asyncronous call to make at a time. Default=%d" % faro.DEFAULT_MAX_ASYNC)

    connection_group.add_option("--max-message-size", type="int", dest="max_message_size",
                                default=faro.DEFAULT_MAX_MESSAGE_SIZE,
                                help="Maximum GRPC message size. Set to -1 for unlimited. Default=%d" % (
                                    faro.DEFAULT_MAX_MESSAGE_SIZE))

    connection_group.add_option("-p", "--port", type="str", dest="port", default="localhost:50030",
                                help="The port used for the recognition service.")

    parser.add_option_group(connection_group)


def addDetectorOptions(parser):
    """
    Add options for detections to the parser.
    """

    detector_group = optparse.OptionGroup(parser, "Detector Options",
                                          "Configuration for the face detector.")

    detector_group.add_option("-d", "--detections-csv", type="str", dest="detections_csv", default=None,
                              help="Save detection data to the file.")

    detector_group.add_option("-a", "--attributes-csv", type="str", dest="attributes_csv", default=None,
                              help="Save attributes data to the file.")

    detector_group.add_option("--detect-log", type="str", dest="detect_log", default=None,
                              help="A directory for detection images.")

    detector_group.add_option("--face-log", type="str", dest="face_log", default=None,
                              help="A directory for faces.")

    detector_group.add_option("-b", "--best", action="store_true", dest="best", default=False,
                              help="Detect the 'best' highest scoring face in the image.")

    detector_group.add_option("--detect-thresh", type="float", dest="detect_thresh", default=None,
                              help="The threshold for a detection.")

    detector_group.add_option("--min-size", type="int", dest="min_size", default=64,
                              help="Faces with a height less that this will be ignored.")

    detector_group.add_option("--attribute-filter", type="str", dest="attribute_filter", default=None,
                              help="A comma seperated list of filters example: 'Male>0.5'"
                              )

    parser.add_option_group(detector_group)


def addEnrollOptions(parser):
    """
    Add options for enrollment into a gallery.
    """

    enroll_group = optparse.OptionGroup(parser, "Enrollment Options",
                                        "Configuration for enrollment.")

    enroll_group.add_option("-e", "--enroll-csv", type="str", dest="enroll_csv", default=None,
                            help="Save a log of the enrollments.")

    enroll_group.add_option("--gallery", type="str", dest="enroll_gallery", default='default',
                            help="Select the gallery to enroll into.")

    enroll_group.add_option("--name", type="str", dest="subject_name", default='UNKNOWN',
                            help="Enroll detected faces into a gallery.")

    enroll_group.add_option("--subject-id", type="str", dest="subject_id", default='unknown',
                            help="Enroll detected faces into a gallery.")

    parser.add_option_group(enroll_group)


def addSearchOptions(parser):
    """
    Add options for search of a gallery.
    """

    search_group = optparse.OptionGroup(parser, "Search Options",
                                        "Configuration for gallery search.")

    search_group.add_option("-s", "--search-csv", type="str", dest="search_csv", default='default',
                            help="Save the search results.")

    search_group.add_option("--search-log", type="str", dest="search_log", default='default',
                            help="Save the search results.")

    search_group.add_option("--gallery", type="str", dest="search_gallery", default='default',
                            help="Select the gallery to search.")

    parser.add_option_group(search_group)


def addTestOptions(parser):
    """
    Add options for a test.
    """

    search_group = optparse.OptionGroup(parser, "Test Options",
                                        "Configuration for a face recognition test.")

    search_group.add_option("--is-match", type="str", dest="search_csv", default=None,
                            help="A function that can parse two image paths and determine ground "
                                 "truth if they are the same subject.  i.e. match the first five "
                                 "characters 'lambda x,y: x[:5] == y[:5]'")

    search_group.add_option('-m', "--distance-matrix", type="str", dest="distance_matrix", default=None,
                            help="Save the distance matrix to this file.")

    search_group.add_option("-s", "--test-summary", type="str", dest="test_summary", default=None,
                            help="A csv file summarizing test results.")

    search_group.add_option("-t", "--threshold", type="float", dest="test_threshold", default=None,
                            help="A score threshold to determine matches.")

    search_group.add_option("--matches-log", type="str", dest="matches_log", default=None,
                            help="A directory containing matching face images.")

    search_group.add_option("--false-matches-log", type="str", dest="false_matches_log", default=None,
                            help="A directory containing matching face images.")

    search_group.add_option("--false-reject-log", type="str", dest="false_reject_log", default=None,
                            help="A directory containing matching face images.")

    parser.add_option_group(search_group)


def preprocessImage(im, options):
    # Reduce the size if the image is too large
    scale = 1.0
    while max(*im.shape[:2]) > options.max_size:
        if max(*im.shape[:2]) > 2 * options.max_size:
            im = cv2.pyrDown(im)
            scale *= 0.5
        else:
            w, h = im.shape[:2]
            s = options.max_size / max(w, h)
            scale *= s
            w = int(s * w)
            h = int(s * h)
            im = cv2.resize(im, (w, h))
    return im


def detectParseOptions():
    """
    Parse command line arguments.
    """
    args = ['[image] [image_directory] [video] [...]']  # Add the names of arguments here.
    n_args = len(args)
    args = " ".join(args)
    description = '''Run detection on a collection of images.'''
    epilog = '''Created by David Bolme - bolmeds@ornl.gov'''

    version = faro.__version__

    # Setup the parser
    parser = optparse.OptionParser(usage='%s command [OPTIONS] %s' % (sys.argv[0], args),
                                   version=version, description=description, epilog=epilog)

    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False,
                      help="Print out more program information.")

    parser.add_option("-n", "--max-images", type="int", dest="max_images", default=None,
                      help="Process at N images and then stop.")

    parser.add_option("--maximum-size", type="int", dest="max_size", default=faro.DEFAULT_MAX_SIZE,
                      help="If too large, images will be scaled to have this maximum size. Default=%d" % (
                          faro.DEFAULT_MAX_SIZE))

    addDetectorOptions(parser)
    addConnectionOptions(parser)
    # Here are some templates for standard option formats.
    # parser.add_option("-q", "--quiet", action="store_false", dest="verbose", default=True,
    #                 help="Decrease the verbosity of the program")

    # parser.add_option("-b", "--bool", action="store_true", dest="my_bool", default=False,
    #                  help="don't print status messages to stdout")

    # parser.add_option( "-c","--choice", type="choice", choices=['c1','c2','c3'], dest="my_choice", default="c1",
    #                  help="Choose an option.")

    # parser.add_option( "-f","--float", type="float", dest="my_float", default=0.0,
    #                  help="A floating point value.")

    # parser.add_option( "-i","--int", type="int", dest="my_int", default=0,
    #                  help="An integer value.")

    # parser.add_option( "-s","--str", type="str", dest="my_str", default="default",
    #                  help="A string value.")

    # parser.add_option( "--enroll", type="str", dest="enroll_gallery", default=None,
    #                  help="Enroll detected faces into a gallery.")

    # parser.add_option( "--search", type="str", dest="search_gallery", default=None,
    #                  help="Search images for faces from a gallery.")

    # parser.add_option( "--name", type="str", dest="subject_name", default=None,
    #                  help="Enroll detected faces into a gallery.")

    # parser.add_option( "--subject-id", type="str", dest="subject_id", default=None,
    #                  help="Enroll detected faces into a gallery.")

    # parser.add_option( "--search-log", type="str", dest="search_log", default=None,
    #                  help="Enroll detected faces into a gallery.")

    # parser.add_option( "-m","--match-log", type="str", dest="match_log", default=None,
    #                  help="A directory to store matching faces.")

    # parser.add_option( "--same-person", type="str", dest="same_person", default=None,
    #                  help="Specifies a python function that returns true if the filenames indicate a match.  Example: lambda x,y: x[:5] == y[:5]")

    # parser.add_option( "-s","--scores-csv", type="str", dest="scores_csv", default=None,
    #                  help="Save similarity scores to this file.")

    # Parse the arguments and return the results.
    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.print_help()
        print()
        print(("Please supply exactly %d arguments." % n_args))
        print()
        exit(-1)

    return options, args

def statusParseOptions():
    """
    Parse command line arguments.
    """
    args = ['']  # Add the names of arguments here.
    n_args = len(args)
    args = " ".join(args)
    description = '''Check the server status and display algorithm and version information.'''
    epilog = '''Created by David Bolme - bolmeds@ornl.gov'''

    version = faro.__version__

    # Setup the parser
    parser = optparse.OptionParser(usage='%s command [OPTIONS] %s' % (sys.argv[0], args),
                                   version=version, description=description, epilog=epilog)

    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False,
                      help="Print out more program information.")

    addConnectionOptions(parser)
    # Here are some templates for standard option formats.
    # parser.add_option("-q", "--quiet", action="store_false", dest="verbose", default=True,
    #                 help="Decrease the verbosity of the program")

    # parser.add_option("-b", "--bool", action="store_true", dest="my_bool", default=False,
    #                  help="don't print status messages to stdout")

    # parser.add_option( "-c","--choice", type="choice", choices=['c1','c2','c3'], dest="my_choice", default="c1",
    #                  help="Choose an option.")

    # parser.add_option( "-f","--float", type="float", dest="my_float", default=0.0,
    #                  help="A floating point value.")

    # parser.add_option( "-i","--int", type="int", dest="my_int", default=0,
    #                  help="An integer value.")

    # parser.add_option( "-s","--str", type="str", dest="my_str", default="default",
    #                  help="A string value.")

    # parser.add_option( "--enroll", type="str", dest="enroll_gallery", default=None,
    #                  help="Enroll detected faces into a gallery.")

    # parser.add_option( "--search", type="str", dest="search_gallery", default=None,
    #                  help="Search images for faces from a gallery.")

    # parser.add_option( "--name", type="str", dest="subject_name", default=None,
    #                  help="Enroll detected faces into a gallery.")

    # parser.add_option( "--subject-id", type="str", dest="subject_id", default=None,
    #                  help="Enroll detected faces into a gallery.")

    # parser.add_option( "--search-log", type="str", dest="search_log", default=None,
    #                  help="Enroll detected faces into a gallery.")

    # parser.add_option( "-m","--match-log", type="str", dest="match_log", default=None,
    #                  help="A directory to store matching faces.")

    # parser.add_option( "--same-person", type="str", dest="same_person", default=None,
    #                  help="Specifies a python function that returns true if the filenames indicate a match.  Example: lambda x,y: x[:5] == y[:5]")

    # parser.add_option( "-s","--scores-csv", type="str", dest="scores_csv", default=None,
    #                  help="Save similarity scores to this file.")

    # Parse the arguments and return the results.
    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.print_help()
        print()
        print(("Please supply exactly %d arguments." % 0))
        print()
        exit(-1)

    return options, args


def enrollParseOptions():
    """
    Parse command line arguments.
    """
    args = ['[image] [image_directory] [video] [...]']  # Add the names of arguments here.
    n_args = len(args)
    args = " ".join(args)
    description = '''Run detection on a collection of images.'''
    epilog = '''Created by David Bolme - bolmeds@ornl.gov'''

    version = faro.__version__

    # Setup the parser
    parser = optparse.OptionParser(usage='%s command [OPTIONS] %s' % (sys.argv[0], args),
                                   version=version, description=description, epilog=epilog)

    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False,
                      help="Print out more program information.")

    parser.add_option("-n", "--max-images", type="int", dest="max_images", default=None,
                      help="Process at N images and then stop.")

    parser.add_option("--maximum-size", type="int", dest="max_size", default=faro.DEFAULT_MAX_SIZE,
                      help="If too large, images will be scaled to have this maximum size. Default=%d" % (
                          faro.DEFAULT_MAX_SIZE))

    addDetectorOptions(parser)
    addEnrollOptions(parser)
    addConnectionOptions(parser)

    # Parse the arguments and return the results.
    (options, args) = parser.parse_args()

    if len(args) < 2:
        parser.print_help()
        print()
        print(("Error: Please supply at least one directory, image, or video."))
        print()
        exit(-1)

    return options, args


def galleryListOptions():
    '''
    Parse command line arguments.
    '''
    args = [] # Add the names of arguments here.
    n_args = len(args)
    args = " ".join(args)
    description = '''List galleries avalible on the service.'''
    epilog = '''Created by David Bolme - bolmeds@ornl.gov'''
    
    version = faro.__version__
    
    
    
    # Setup the parser
    parser = optparse.OptionParser(usage='%s command [OPTIONS] %s'%(sys.argv[0],args),version=version,description=description,epilog=epilog)

    parser.add_option( "-v", "--verbose", action="store_true", dest="verbose", default=False,
                      help="Print out more program information.")
    
    addConnectionOptions(parser)

    # Parse the arguments and return the results.
    (options, args) = parser.parse_args()
    
    if len(args) < 1:
        parser.print_help()
        print()
        print(( "Error: No position arguments required."))
        print()
        exit(-1)
        
        
    return options,args

def faceListOptions():
    '''
    Parse command line arguments.
    '''
    args = ['gallery_name'] # Add the names of arguments here.
    n_args = len(args)
    args = " ".join(args)
    description = '''List faces in a gallery.'''
    epilog = '''Created by David Bolme - bolmeds@ornl.gov'''
    
    version = faro.__version__
    
    
    
    # Setup the parser
    parser = optparse.OptionParser(usage='%s command [OPTIONS] %s'%(sys.argv[0],args),version=version,description=description,epilog=epilog)

    parser.add_option( "-v", "--verbose", action="store_true", dest="verbose", default=False,
                      help="Print out more program information.")
    
    addConnectionOptions(parser)

    # Parse the arguments and return the results.
    (options, args) = parser.parse_args()
    
    if len(args) < 1:
        parser.print_help()
        print()
        print(( "Error: No position arguments required."))
        print()
        exit(-1)
        
        
    return options,args


def searchParseOptions():
    """
    Parse command line arguments.
    """
    args = ['[image] [image_directory] [video] [...]']  # Add the names of arguments here.
    n_args = len(args)
    args = " ".join(args)
    description = '''Run detection on a collection of images.'''
    epilog = '''Created by David Bolme - bolmeds@ornl.gov'''

    version = faro.__version__

    # Setup the parser
    parser = optparse.OptionParser(usage='%s command [OPTIONS] %s' % (sys.argv[0], args),
                                   version=version, description=description, epilog=epilog)

    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False,
                      help="Print out more program information.")

    parser.add_option("-n", "--max-images", type="int", dest="max_images", default=None,
                      help="Process at N images and then stop.")

    parser.add_option("--maximum-size", type="int", dest="max_size", default=faro.DEFAULT_MAX_SIZE,
                      help="If too large, images will be scaled to have this maximum size. Default=%d" % (
                          faro.DEFAULT_MAX_SIZE))

    addSearchOptions(parser)
    addDetectorOptions(parser)
    addConnectionOptions(parser)

    # Parse the arguments and return the results.
    (options, args) = parser.parse_args()

    if len(args) < 2:
        parser.print_help()
        print()
        print(("Error: Please supply at least one directory, image, or video."))
        print()
        exit(-1)

    return options, args


def testParseOptions():
    """
    Parse command line arguments.
    """
    args = ['gallery_dir probe_dir']  # Add the names of arguments here.
    n_args = len(args)
    args = " ".join(args)
    description = '''Run a test to compute the distance matrix between images in probe and gallery directories.'''
    epilog = '''Created by David Bolme - bolmeds@ornl.gov'''

    version = faro.__version__

    # Setup the parser
    parser = optparse.OptionParser(usage='%s command [OPTIONS] %s' % (sys.argv[0], args),
                                   version=version, description=description, epilog=epilog)

    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False,
                      help="Print out more program information.")

    parser.add_option("-n", "--max-images", type="int", dest="max_images", default=None,
                      help="Process at N images and then stop.")

    parser.add_option("--maximum-size", type="int", dest="max_size", default=faro.DEFAULT_MAX_SIZE,
                      help="If too large, images will be scaled to have this maximum size. Default=%d" % (
                          faro.DEFAULT_MAX_SIZE))

    addTestOptions(parser)
    addDetectorOptions(parser)
    addConnectionOptions(parser)

    # Parse the arguments and return the results.
    (options, args) = parser.parse_args()

    if len(args) < 2:
        parser.print_help()
        print()
        print(("Error: Please supply at least one directory, image, or video."))
        print()
        exit(-1)

    return options, args


def connectToFaroClient(options):
    if options.verbose:
        print('Connecting to FaRO Service...')

    face_client = faro.FaceClient(options)

    is_ready, status = face_client.status(verbose=options.verbose)
    if not is_ready:
        print("ERROR: the FaRO service is not ready.")
        print(status)
        exit(-1)
    else:
        if options.verbose:
            print('Connection to FaRO service established. [ algorithm: %s ]' % (status.algorithm))

    return face_client


def collect_files(args, options):
    if options.verbose:
        print('Scanning for videos and images...')

    image_list = []
    video_list = []

    for each in args:
        if os.path.isdir(each):
            for path, dirs, files in os.walk(each):
                for filename in files:
                    if pv.isImage(filename):
                        image_list.append(os.path.join(path, filename))
                    elif pv.isVideo(filename):
                        video_list.append(os.path.join(path, filename))

        elif os.path.isfile(each):
            if pv.isImage(each):
                image_list.append(each)
            elif pv.isVideo(each):
                video_list.append(each)
            else:
                raise ValueError("The file <%s> is not in a supported image or video type." % (each))
        else:
            raise ValueError("The path <%s> is not found." % (each))

    if options.verbose:
        print("    Found %d images." % (len(image_list)))
        print("    Found %d videos." % (len(video_list)))

    return image_list, video_list


def processAttributeFilter(face, options):
    if options.attribute_filter is None:
        return True

    # Parse the filter
    terms = options.attribute_filter.split(',')
    new_terms = []
    for each in terms:
        try:
            parts = each.split('>')
            parts = parts[0], '>', float(parts[1])
            assert len(parts) == 3
        except:
            try:
                parts = each.split('<')
                # print (parts)
                parts = parts[0], '<', float(parts[1])
                assert len(parts) == 3
            except:
                raise ValueError("Could not parse term '%s'." % each)

        new_terms.append(parts)

    satisfied = 0

    attributes = list(face.attributes)
    attributes.sort(key=lambda x: x.key)

    for attribute in attributes:
        key = attribute.key
        value = attribute.fvalue
        for tkey, tcmp, tval in new_terms:
            if tkey == key and value > tval and tcmp == '>':
                satisfied += 1
            if tkey == key and value < tval and tcmp == '<':
                satisfied += 1

    # assert satisfied <= len(terms) # Make sure we get an expected answer

    return satisfied == len(terms)


DETECTIONS_FILE = None
DETECTIONS_CSV = None
ATTRIBUTES_FILE = None
ATTRIBUTES_CSV = None


def processDetections(each):
    im, results, options = each
    if results.done():
        recs = results.result().face_records
        i = 0

        dimg = None
        for idx, face in enumerate(recs):
            global FACE_COUNT
            FACE_COUNT += 1
            # Filter faces based on min size
            size = min(face.detection.location.width, face.detection.location.height)
            if size < options.min_size:
                continue

            # Filter faces based on attributes
            if not processAttributeFilter(face, options):
                continue

            # Process Detections
            if options.detections_csv is not None:
                global DETECTIONS_CSV
                global DETECTIONS_FILE
                import csv
                if DETECTIONS_CSV == None:
                    DETECTIONS_FILE = open(options.detections_csv, 'w')
                    DETECTIONS_CSV = csv.writer(DETECTIONS_FILE)
                    csv_header = ['source', 'frame', 'detect_id', 'type', 'score', 'x', 'y', 'w', 'h']
                    if len(face.landmarks) > 0:
                        for each_lpt in face.landmarks:
                            pt_id_label = each_lpt.landmark_id
                            xpt_label = pt_id_label + '_x'
                            ypt_label = pt_id_label + '_y'
                            csv_header.append(pt_id_label)
                            csv_header.append(xpt_label)
                            csv_header.append(ypt_label)

                    DETECTIONS_CSV.writerow(csv_header)

                csv_eachline = [face.source,
                                face.frame,
                                i,
                                face.detection.detection_class,
                                face.detection.score,
                                face.detection.location.x,
                                face.detection.location.y,
                                face.detection.location.width,
                                face.detection.location.height]

                if len(face.landmarks) > 0:
                    for each_lpt in face.landmarks:
                        pt_id_label = each_lpt.landmark_id
                        xpt_label = each_lpt.location.x
                        ypt_label = each_lpt.location.y
                        csv_eachline.append(pt_id_label)
                        csv_eachline.append(xpt_label)
                        csv_eachline.append(ypt_label)
                DETECTIONS_CSV.writerow(csv_eachline)

                DETECTIONS_FILE.flush()

            # Process Detections
            if options.attributes_csv is not None:
                global ATTRIBUTES_CSV
                global ATTRIBUTES_FILE
                import csv

                if ATTRIBUTES_CSV == None:
                    ATTRIBUTES_FILE = open(options.attributes_csv, 'w')
                    ATTRIBUTES_CSV = csv.writer(ATTRIBUTES_FILE)
                    csv_header = ['source', 'frame', 'detect_id', 'type', 'score', 'x', 'y',
                                  'w', 'h', 'attribute', 'value']
                    if len(face.landmarks) > 0:
                        for each_lpt in face.landmarks:
                            pt_id_label = each_lpt.landmark_id
                            xpt_label = pt_id_label + '_x'
                            ypt_label = pt_id_label + '_y'
                            csv_header.append(pt_id_label)
                            csv_header.append(xpt_label)
                            csv_header.append(ypt_label)
                    ATTRIBUTES_CSV.writerow(csv_header)

                attributes = list(face.attributes)
                attributes.sort(key=lambda x: x.key)
                for attribute in attributes:
                    key = attribute.key
                    value = attribute.fvalue
                    csv_eachline = [face.source,
                                    face.frame,
                                    i,
                                    face.detection.detection_class,
                                    face.detection.score,
                                    face.detection.location.x,
                                    face.detection.location.y,
                                    face.detection.location.width,
                                    face.detection.location.height,
                                    key,
                                    value]
                    if len(face.landmarks) > 0:
                        for each_lpt in face.landmarks:
                            pt_id_label = each_lpt.landmark_id
                            xpt_label = each_lpt.location.x
                            ypt_label = each_lpt.location.y
                            csv_eachline.append(pt_id_label)
                            csv_eachline.append(xpt_label)
                            csv_eachline.append(ypt_label)
                    ATTRIBUTES_CSV.writerow(csv_eachline)
                ATTRIBUTES_FILE.flush()

            # Save Images with Detections

            if options.detect_log:
                if not os.path.exists(options.detect_log):
                    os.makedirs(options.detect_log, exist_ok=True)
                rect = pt.rect_proto2pv(face.detection.location)
                if dimg is None:
                    dimg = pv.Image(im[:, :, ::-1])
                dimg.annotateThickRect(rect)
                dimg.annotateLabel(pv.Point(rect.x + 5, rect.y + 5), face.detection.detection_class)
                dimg.annotateLabel(pv.Point(rect.x + 5, rect.y + 20),
                                   "Score: %0.4f" % (face.detection.score,), color='yellow')
                if len(face.landmarks) > 0:
                    for each_lmark in face.landmarks:
                        dimg.annotateCircle(pv.Point(each_lmark.location.x, each_lmark.location.y),
                                            radius=3, color='green', fill='green')

            if options.face_log:
                if not os.path.exists(options.face_log):
                    os.makedirs(options.face_log, exist_ok=True)
                # print(face.detection.location)

                rect = pt.rect_proto2pv(face.detection.location)
                rect = rect.rescale(1.5)
                affine = pv.AffineFromRect(rect, (128, 128))
                try:
                    pvim = pv.Image(im[:, :, ::-1])
                    view = affine(pvim)
                    # print('Face',rect)
                    # print(view)
                    base_name, ext = os.path.splitext(os.path.basename(face.source))
                    out_path = os.path.join(options.face_log,
                                            os.path.basename(base_name) + '_face_%03d' % (
                                            face.detection.detection_id,) + ext)

                    view.save(out_path)
                    print('Saving face:', out_path)
                except:
                    print("WARNING: Image not processed correctly:", face.source)

                out_path = os.path.join(options.face_log, os.path.basename(base_name) + '_orig' + ext)

                if not os.path.lexists(out_path):
                    os.symlink(os.path.abspath(face.source), out_path)
            i += 1
        if options.detect_log and dimg is not None:
            dimg.asAnnotated().save(os.path.join(options.detect_log, os.path.basename(base_name) + ext))
        return False
    return True


ENROLL_FILE = None
ENROLL_CSV = None


def processEnrollments(each):
    im, results, options = each

    if results.done():
        recs = results.result().face_records
        i = 0
        for face in recs:
            # Filter faces based on min size
            size = min(face.detection.location.width, face.detection.location.height)
            if size < options.min_size:
                continue

            # Filter faces based on attributes
            if not processAttributeFilter(face, options):
                continue

            # Process Detections
            if options.enroll_csv is not None:
                global ENROLL_CSV
                global ENROLL_FILE
                import csv
                if ENROLL_CSV == None:
                    ENROLL_FILE = open(options.enroll_csv, 'w')
                    ENROLL_CSV = csv.writer(ENROLL_FILE)
                    ENROLL_CSV.writerow(['gallery_key', 'source', 'frame', 'detect_id',
                                         'type', 'score', 'x', 'y', 'w', 'h'])

                ENROLL_CSV.writerow([face.gallery_key, face.source,
                                     face.frame,
                                     i,
                                     face.detection.detection_class,
                                     face.detection.score,
                                     face.detection.location.x,
                                     face.detection.location.y,
                                     face.detection.location.width,
                                     face.detection.location.height
                                     ]),
                ENROLL_FILE.flush()

            i += 1
        return False
    return True


SEARCH_CSV = None
SEARCH_FILE = None


def processSearchResults(each):
    im, results, options = each
    im = pv.Image(im[:,:,::-1]) # RGB to BGR

    if results.done():
        recs = results.result().face_records

        i = 0

        if options.search_log is not None:
            try:
                os.makedirs(options.search_log)
            except:
                pass

        for face in recs:
            # Filter faces based on min size
            size = min(face.detection.location.width, face.detection.location.height)
            if size < options.min_size:
                continue

            # Filter faces based on attributes
            if not processAttributeFilter(face, options):
                continue

            face_source = face.source
            face_detect_id = face.detection.detection_id
            face_detect_rect = pt.rect_proto2pv(face.detection.location)

            # Process Detections
            if options.search_csv is not None:
                global SEARCH_CSV
                global SEARCH_FILE
                import csv
                if SEARCH_CSV == None:
                    # if options.verbose:
                    SEARCH_FILE = open(options.search_csv, 'w')
                    SEARCH_CSV = csv.writer(SEARCH_FILE)
                    SEARCH_CSV.writerow(['face_source', 'face_detect_id',
                                         'gal_sub_id', 'gal_name', 'gal_source',
                                         'gal_score', 'gal_key', 'x', 'y', 'w', 'h'])


            if options.search_log is not None:

                if len(face.search_results.face_records) > 0:
                    gal = face.search_results.face_records[0]
                    gal_name = gal.name
                    gal_sub_id = gal.subject_id
                    gal_source = gal.source
                    gal_score = gal.score
                    gal_key = gal.gallery_key

                    # face.search_results.face_records
                    # string subject_id = 1;
                    # string name = 5;
                    # string source = 4;
                    # int64 frame = 14;
                    # string notes = 6;
                    # string gallery_key = 15;

                    SEARCH_CSV.writerow([face_source, face_detect_id,
                                         gal_sub_id, gal_name, gal_source, gal_score, gal_key, face_detect_rect.x,face_detect_rect.y,face_detect_rect.w,face_detect_rect.h
                                         ]),

                    im.annotateThickRect(face_detect_rect,width=3,color='yellow')
                    im.annotateLabel(pv.Point(face_detect_rect.x,face_detect_rect.y+face_detect_rect.h+5),"%s - %s"%(gal_sub_id,gal_name),font=16,color='yellow')
                else:
                    im.annotateRect(face_detect_rect,color='white')

                SEARCH_FILE.flush()

            i += 1

        if options.search_log is not None:
            out_name = os.path.join(options.search_log,os.path.basename(face_source))
            im.asAnnotated().save(out_name)

        return False
    return True

VIDEO_HEADER_FILE = None

def process_video_detections(each):
    global VIDEO_HEADER_FILE
    im, results, options, file_identifier = each
    if results.done():
        recs = results.result().face_records
        i = 0
        detect_log_dir = None
        frame_id = None
        dimg = None
        for idx, face in enumerate(recs):
            base_name, ext = os.path.splitext(os.path.basename(face.source))
            # Filter faces based on min size
            size = min(face.detection.location.width, face.detection.location.height)
            if size < options.min_size:
                continue

            if (options.detections_csv is not None):    
                if VIDEO_HEADER_FILE:
                    csv_header = ['source', 'frame', 'detect_id', 'type', 'score', 'x', 'y', 'w', 'h']
                    if len(face.landmarks) > 0:
                        for each_lpt in face.landmarks:
                            pt_id_label = each_lpt.landmark_id
                            xpt_label = pt_id_label + '_x'
                            ypt_label = pt_id_label + '_y'
                            csv_header.append(pt_id_label)
                            csv_header.append(xpt_label)
                            csv_header.append(ypt_label)
                    file_identifier.writerow(csv_header)
                    VIDEO_HEADER_FILE = False

                csv_eachline = [face.source,
                                face.frame,
                                i,
                                face.detection.detection_class,
                                face.detection.score,
                                face.detection.location.x,
                                face.detection.location.y,
                                face.detection.location.width,
                                face.detection.location.height]

                if len(face.landmarks) > 0:
                    for each_lpt in face.landmarks:
                        pt_id_label = each_lpt.landmark_id
                        xpt_label = each_lpt.location.x
                        ypt_label = each_lpt.location.y
                        csv_eachline.append(pt_id_label)
                        csv_eachline.append(xpt_label)
                        csv_eachline.append(ypt_label)

                file_identifier.writerow(csv_eachline)

            if options.detect_log:
                detect_log_dir = os.path.join(os.path.join(options.detect_log, base_name))
                frame_id = face.frame
                if not os.path.exists(detect_log_dir):
                    os.makedirs(detect_log_dir, exist_ok=True)

                rect = pt.rect_proto2pv(face.detection.location)
                if dimg is None:
                    dimg = pv.Image(im[:, :, ::-1])
                dimg.annotateThickRect(rect)
                dimg.annotateLabel(pv.Point(rect.x + 5, rect.y + 5), face.detection.detection_class)
                dimg.annotateLabel(pv.Point(rect.x + 5, rect.y + 20),
                                   "Score: %0.4f" % (face.detection.score,), color='yellow')
                if len(face.landmarks) > 0:
                    for each_lmark in face.landmarks:
                        dimg.annotateCircle(pv.Point(each_lmark.location.x, each_lmark.location.y),
                                            radius=3, color='green', fill='green')

            if options.face_log:
                face_log_dir = os.path.join(options.face_log, base_name)
                if not os.path.exists(face_log_dir):
                    os.makedirs(face_log_dir, exist_ok=True)

                rect = pt.rect_proto2pv(face.detection.location)
                rect = rect.rescale(1.5)
                affine = pv.AffineFromRect(rect, (128, 128))
                try:
                    pvim = pv.Image(im[:, :, ::-1])
                    view = affine(pvim)
                    out_path = os.path.join(face_log_dir, os.path.basename(base_name) +
                                            '_Frame_%09d' % face.frame +
                                            '_face_%03d' % (face.detection.detection_id,) + '.jpg')
                    if len(face.landmarks) > 0:
                        for each_lmark in face.landmarks:
                            transformed_lmarks = affine(pv.Point(each_lmark.location.x, each_lmark.location.y))
                            view.annotateCircle(transformed_lmarks, radius=3, color='green', fill='green')
                    view.asAnnotated().save(out_path)
                    #print('Saving face:', out_path)
                except:
                    print("WARNING: Image not processed correctly:", face.source)
            i += 1

        if options.detect_log and detect_log_dir is not None:
            dimg.asAnnotated().save(os.path.join(detect_log_dir,
                                                 os.path.basename(base_name) + '_Frame_%09d' % frame_id + '.jpg'))
        return False
    return True


def process_single_videos(each_video, face_client, options):
    global VIDEO_HEADER_FILE
    VIDEO_HEADER_FILE = True
    detect_queue = []
    # Read Video
    video = pv.Video(each_video)
    video_name, ext = os.path.splitext(os.path.basename(each_video))
    
    if options.detections_csv:
        _, tmp_ext = os.path.splitext(os.path.basename(options.detections_csv))
        if tmp_ext:
            save_video_csvfile_dir = os.path.dirname(options.detections_csv)
            if len(save_video_csvfile_dir) == 0:
                save_video_csvfile_dir = os.getcwd()
        else:
            save_video_csvfile_dir = options.detections_csv
        if not os.path.isdir(save_video_csvfile_dir):
            os.makedirs(save_video_csvfile_dir)    
        fid = open(os.path.join(save_video_csvfile_dir, video_name + '.csv'), 'w')
        video_detections_csv = csv.writer(fid)
    else:
        video_detections_csv = None

    start_time = time.time()
    for frame_id, each_frame in enumerate(video):

        each_frame = each_frame.asOpenCV2()[:, :, ::-1]  # convert to opencv and then bgrtorgb
        if options.max_size is not None:
            each_frame = preprocessImage(each_frame, options)
        results = face_client.detect(each_frame, best=options.best,
                                     threshold=options.detect_thresh,
                                     min_size=options.min_size,
                                     run_async=True,
                                     source=each_video,
                                     frame=frame_id + 1)
        detect_queue.append([each_frame, results, options, video_detections_csv])
        detect_queue = list(filter(process_video_detections, detect_queue))

    while len(detect_queue):
        detect_queue = list(filter(process_video_detections, detect_queue))
        time.sleep(0.05)

    end_time = time.time()
    print("Processed %d frames in %0.3f seconds: %f images/second" % (frame_id + 1, end_time - start_time,
                                                                      (frame_id + 1) / (end_time - start_time)))

    if options.detections_csv:
        fid.close()


def process_videos(vlist, face_client, options):
    
    if options.verbose:
        print("Processing videos")

    for each_video in vlist:
        print('Processing Video: ', each_video)
        process_single_videos(each_video, face_client, options)



def process_images(ilist, face_client, options):
    
    if options.verbose:
        print("Processing images.")

    image_count = 0
    detect_queue = []

    start = time.time()
    for filename in ilist:
        print("Processing:", filename)
        im = cv2.imread(filename)

        if im is None:
            continue

        im = im[:, :, ::-1]  # BGR to RGB

        im = preprocessImage(im, options)

        results = face_client.detect(im, best=options.best, threshold=options.detect_thresh, min_size=options.min_size,
                                     run_async=True, source=filename, frame=-1)

        detect_queue.append([im, results, options])
        detect_queue = list(filter(processDetections, detect_queue))
        image_count += 1
        if options.max_images is not None and image_count >= options.max_images:
            break

    while len(detect_queue):
        detect_queue = list(filter(processDetections, detect_queue))
        time.sleep(0.05)

    end = time.time()
    print("Processed %d images in %0.3f seconds: %f images/second" % (
         image_count, end - start, image_count / (end - start)))
    print(
        "Processed %d faces in %0.3f seconds: %f faces/second" % (FACE_COUNT, end - start, FACE_COUNT / (end - start)))

def detect():
    options, args = detectParseOptions()
    face_client = connectToFaroClient(options)

    if options.verbose:
        print("Scanning directories for images and videos.")

    image_list, video_list = collect_files(args[1:], options)
        

    if len(image_list) != 0:
        process_images(image_list, face_client, options)

    if len(video_list) != 0:
        process_videos(video_list, face_client, options)


def detectExtract():
    options, args = detectParseOptions()
    face_client = connectToFaroClient(options)

    if options.verbose:
        print("Scanning directories for images and videos.")

    image_list, video_list = collect_files(args[1:], options)

    if options.verbose:
        print("Processing images.")

    image_count = 0
    detect_queue = []
    start = time.time()
    for filename in image_list:
        print("Processing:", filename)
        im = cv2.imread(filename)
        im = im[:, :, ::-1]  # BGR to RGB

        im = preprocessImage(im, options)

        results = face_client.detectExtract(im, best=options.best, threshold=options.detect_thresh,
                                            min_size=options.min_size, run_async=True, source=filename, frame=-1)

        detect_queue.append([im, results, options])
        detect_queue = list(filter(processDetections, detect_queue))

        image_count += 1
        if options.max_images is not None and image_count >= options.max_images:
            break

    end = time.time()

    while len(detect_queue):
        detect_queue = list(filter(processDetections, detect_queue))
        time.sleep(0.05)

    if len(video_list) > 0:
        print("WARNING: Video Processing Is Not Implemented. %d videos skipped." % (video_list,))

    print("Processed %d images in %0.3f seconds: %f images/second" % (
    image_count, end - start, image_count / (end - start)))
    print(
        "Processed %d faces in %0.3f seconds: %f faces/second" % (FACE_COUNT, end - start, FACE_COUNT / (end - start)))


def extractOnly():
    options, args = detectParseOptions()
    face_client = connectToFaroClient(options)

    if options.verbose:
        print("Scanning directories for images and videos.")

    f = open(args[1], 'r')
    csv_f = csv.DictReader(f)

    process_queue = []
    current_file = None
    for row in csv_f:
        if current_file == None or current_file != row['source']:
            current_file = row['source']
            detections = FaceRecordList()
            process_queue.append([current_file, detections])

        face = detections.face_records.add()
        face.source = row['source']
        face.frame = int(row['frame'])
        face.detection.detection_id = int(row['detect_id'])
        face.detection.score = float(row['score'])
        face.detection.detection_class = row['type']
        face.detection.location.x = float(row['x'])
        face.detection.location.y = float(row['y'])
        face.detection.location.width = float(row['w'])
        face.detection.location.height = float(row['h'])

    # image_list, video_list = collect_files(args[1:],options)

    if options.verbose:
        print("Processing images.")

    image_count = 0
    detect_queue = []
    start = time.time()
    for filename, detections in process_queue:
        # print("Processing:",filename)
        im = cv2.imread(filename)
        im = im[:, :, ::-1]  # BGR to RGB

        im = preprocessImage(im, options)

        results = face_client.extract(im, detections, run_async=True)

        detect_queue.append([im, results, options])
        detect_queue = list(filter(processDetections, detect_queue))

        image_count += 1
        if options.max_images is not None and image_count >= options.max_images:
            break
    end = time.time()

    while len(detect_queue):
        detect_queue = list(filter(processDetections, detect_queue))
        time.sleep(0.05)

    # if len(video_list) > 0:
    #    print("WARNING: Video Processing Is Not Implemented. %d videos skipped."%(video_list,))

    print("Processed %d images in %0.3f seconds: %f images/second" % (
          image_count, end - start, image_count / (end - start)))
    print(
        "Processed %d faces in %0.3f seconds: %f faces/second" % (FACE_COUNT, end - start, FACE_COUNT / (end - start)))


def enroll():
    options, args = enrollParseOptions()
    face_client = connectToFaroClient(options)

    if options.verbose:
        print("Scanning directories for images and videos.")

    image_list, video_list = collect_files(args[1:], options)

    if options.verbose:
        print("Processing images.")

    image_count = 0
    detect_queue = []
    enroll_queue = []

    for filename in image_list:
        print("Processing:", filename)
        im = cv2.imread(filename)
        im = im[:, :, ::-1]  # BGR to RGB

        im = preprocessImage(im, options)

        results = face_client.detectExtractEnroll(im, enroll_gallery=options.enroll_gallery, best=options.best,
                                                  threshold=options.detect_thresh, min_size=options.min_size,
                                                  run_async=True, source=filename, frame=-1,
                                                  subject_name=options.subject_name, subject_id=options.subject_id)

        detect_queue.append([im, results, options])
        enroll_queue.append([im, results, options])

        # Process results that are completed.
        detect_queue = list(filter(processDetections, detect_queue))
        enroll_queue = list(filter(processEnrollments, enroll_queue))

        image_count += 1
        if options.max_images is not None and image_count >= options.max_images:
            break

    import time

    # Finish processing.
    while len(detect_queue):
        detect_queue = list(filter(processDetections, detect_queue))
        time.sleep(0.05)

    while len(enroll_queue):
        enroll_queue = list(filter(processEnrollments, enroll_queue))
        time.sleep(0.05)

    if len(video_list) > 0:
        print("WARNING: Video Processing Is Not Implemented. %d videos skipped." % (video_list,))

def glist():
    options,args = galleryListOptions()
    face_client = connectToFaroClient(options)

    result = face_client.galleryList()
    
    print()
    print("%-24s | %10s"%('GALLERY NAME','FACE_COUNT'))
    print('-'*37)
    for gallery in result.galleries:
        print("%-24s | %10d"%(gallery.gallery_name,gallery.face_count))
    print()
    
def flist():
    options,args = faceListOptions()
    face_client = connectToFaroClient(options)
    
    gallery_name = args[1]
    result = face_client.faceList(gallery_name)
    
    print()
    print("%-48s | %-16s | %-32s | %-40s | %10s"%('KEY','SUBJECT_ID','NAME','SOURCE','FRAME'))
    print('-'*158)
    for face in result.face_records:
        print("%-48s | %-16s | %-32s | %-40s | %10d"%(face.gallery_key, face.subject_id, face.name, face.source, face.frame))
    print()
    
def search():
    options, args = searchParseOptions()
    face_client = connectToFaroClient(options)

    if options.verbose:
        print("Scanning directories for images and videos.")

    image_list, video_list = collect_files(args[1:], options)

    if options.verbose:
        print("Processing images.")

    image_count = 0
    detect_queue = []
    search_queue = []

    for filename in image_list:
        print("Processing:", filename)
        im = cv2.imread(filename)
        im = im[:, :, ::-1]  # BGR to RGB

        im = preprocessImage(im, options)

        results = face_client.detectExtractSearch(im, search_gallery=options.search_gallery, best=options.best,
                                                  threshold=options.detect_thresh, min_size=options.min_size,
                                                  run_async=True, source=filename, frame=-1)

        detect_queue.append([im, results, options])
        search_queue.append([im, results, options])

        # Process results that are completed.
        detect_queue = list(filter(processDetections, detect_queue))
        search_queue = list(filter(processSearchResults, search_queue))

        image_count += 1
        if options.max_images is not None and image_count >= options.max_images:
            break

    import time

    # Finish processing.
    while len(detect_queue):
        detect_queue = list(filter(processDetections, detect_queue))
        time.sleep(0.05)

    while len(search_queue):
        search_queue = list(filter(processSearchResults, search_queue))
        time.sleep(0.05)

    if len(video_list) > 0:
        print("WARNING: Video Processing Is Not Implemented. %d videos skipped." % (video_list,))

def test():
    """
    Run a recognition test and compute a distance matrix and optionally other results.
    """
    options, args = testParseOptions()

    face_client = connectToFaroClient(options)

    if options.verbose:
        print("Scanning directories for images and videos.")

    image_list, video_list = collect_files(args[1:], options)

    if options.verbose:
        print("Processing images.")

    image_count = 0
    detect_queue = []
    search_queue = []

    for filename in image_list:
        print("Processing:", filename)
        im = cv2.imread(filename)
        im = im[:, :, ::-1]  # BGR to RGB

        im = preprocessImage(im, options)

        results = face_client.detectExtract(im, search_gallery=options.search_gallery, best=options.best,
                                            threshold=options.detect_thresh, min_size=options.min_size, run_async=True,
                                            source=filename, frame=-1)

        detect_queue.append([im, results, options])

        # Process results that are completed.
        detect_queue = list(filter(processDetections, detect_queue))

        image_count += 1
        if options.max_images is not None and image_count >= options.max_images:
            break

    import time

    # Finish processing.
    while len(detect_queue):
        detect_queue = list(filter(processDetections, detect_queue))
        time.sleep(0.05)

    if len(video_list) > 0:
        print("WARNING: Video Processing Is Not Implemented. %d videos skipped." % (video_list,))

def status():
    """
    Conects to the server and gets status information.
    """
    options,args = statusParseOptions()

    face_client = connectToFaroClient(options)

    message = face_client.status()

    print()
    print (message)
    print()

 

COMMANDS = {
    'status' : ['Connects to the server and displays version and status information.',status],
    'detect' : ['Only run face detection.',detect],
    'detectExtract' : ['Run face detection and template extraction.',detectExtract],
    'extractOnly' : ['Only run face extraction and attribute extraction.',extractOnly],
    'enroll' : ['Extract faces and enroll faces in a gallery.',enroll],
    'flist' : ['List the faces in a gallery.',flist],
    'glist' : ['List the galleries on the service.',glist],
    'search' : ['Search images for faces in a gallery.',search],
    'test' : ['Process a probe and gallery directory and produce a distance matrix.',test],
            }

def face_command_line():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        # Display a basic help message if no command is specified
        print()
        print("ERROR: You must a command command.  For more help run %s <command> --help.\n\nCommands:" % (sys.argv[0]))
        for each in COMMANDS:
            print("    %s - %s" % (each, COMMANDS[each][0]))
        print()
        exit(-1)

    # Jump to the entry point for the command.
    COMMANDS[sys.argv[1]][1]()


if __name__ == '__main__':
    face_command_line()
