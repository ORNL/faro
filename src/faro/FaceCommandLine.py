'''
Created on Dec 3, 2019 at Oak Ridge National Laboratory

@author: qdb
'''
import sys
import optparse
import os
import faro.FaceService as ffs
import faro
import faro.proc
import faro.pyvision as pv
import cv2
import faro.proto.proto_types as pt
import csv
from faro.proto.face_service_pb2 import FaceRecordList,GalleryListRequest
import time
import traceback
from faro.command_line import addConnectionOptions, connectToFaroClient
import faro.command_line as command_line


def addConnectionOptions(parser):
    """
    Add options for connecting to the faro service.
    """

    connection_group = optparse.OptionGroup(parser, "Connection Options",
                                            "Control the connection to the FaRO service.")

    connection_group.add_option("--max-async", type="int", dest="max_async", default=faro.DEFAULT_MAX_ASYNC,
                                help="The maximum number of asyncronous call to make at a time. Default=%d" % faro.DEFAULT_MAX_ASYNC)

    connection_group.add_option( "--compression", type="choice", choices=['uint8','jpg','png'], dest="compression", default="uint8",
                                help="Choose a compression format for data transmissions [uint8, jpg, png]. Default=uint8")

    connection_group.add_option( "--quality", type="int", dest="quality", default=95,
                                help="Compression quality level [0-100]. Default=95")

    connection_group.add_option("--max-message-size", type="int", dest="max_message_size",
                                default=faro.DEFAULT_MAX_MESSAGE_SIZE,
                                help="Maximum GRPC message size. Set to -1 for unlimited. Default=%d" % (
                                    faro.DEFAULT_MAX_MESSAGE_SIZE))

    connection_group.add_option("-p", "--port", type="str", dest="port", default="localhost:50030",
                                help="The port used for the recognition service.")
    connection_group.add_option("--service-name",type="str",dest="service_name",default=None,help="The name of a visible service on the network (enumerate services using `faro status --active`")

    connection_group.add_option("--stream", type="str", dest="stream", default=None,
                                help="Process incoming frames from a camera stream. Currently only works for webcam")
    connection_group.add_option("-c","--certificate", type="str", dest="certificate", default=None,
                                help="Use a secure gRPC channel. For a client, point to a .pem public key")

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


def addFaceDeleteOptions(parser):
    """
    Add options for deleting faces.
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

    search_group.add_option("-s", "--search-csv", type="str", dest="search_csv", default=None,
                            help="Save the search results.")

    search_group.add_option("--search-log", type="str", dest="search_log", default=None,
                            help="Save the search results.")

    search_group.add_option("--search-index", type="str", dest="search_index", default=None,
                            help="Save the search results.")

    search_group.add_option("--gallery", type="str", dest="search_gallery", default='default',
                            help="Select the gallery to search.")

    search_group.add_option("--search-threshold", type="float", dest="search_threshold", default=None,
                            help="Set the maximum threshold for a match.")

    search_group.add_option("--max-results", type="int", dest="max_results", default=3,
                            help="Set the maximum number of search results returned for each face.")

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
    
def addFuseOptions(parser):
    fuse_group = optparse.OptionGroup(parser, "Fusion Options",
                                        "Configuration for fusing scored results")
    fuse_group.add_option('-m', "--distance-matrix", type="str", dest="distance_matrix", default=None,
                            help="Save the fused distance matrix to this file.")     
    fuse_group.add_option("--fusion-method", type="str", dest="method", default="minmax",
                            help="method to use for fusion. Options are minmax, Options are minmax, weighted, gmm, llr, mlp")  
    fuse_group.add_option("--training-data", type="str", dest="training", default=None,
                            help="Comma separated list of .csv files used for training, each file pertaining to a unique method's scores")                                
    parser.add_option_group(fuse_group)


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
    parser.add_option("-a", "--all", action='store_true',dest='all',default=False,help='Show all possible workers (sniffs the network), active and inactive (searches in FARO_WORKER_DIR)')
    parser.add_option("--active",action="store_true",dest="active",default=False,help='Show only worker services currently active and available on the network')
    parser.add_option("--inactive",action="store_true",dest='inactive',default=False,help="Show only worker services that are currently not loaded")
    parser.add_option("--sweep",action="store_true",dest='sweep',default=False,help="Perform a port sweep for active workers")

    addConnectionOptions(parser)

    # Parse the arguments and return the results.
    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.print_help()
        print()
        print(("Please supply exactly %d arguments." % 0))
        print()
        exit(-1)

    return options, args

def startParseOptions():
    """
    Parse command line arguments.
    """
    args = ['']  # Add the names of arguments here.
    n_args = len(args)
    args = " ".join(args)
    description = '''Start up an available FaRO service using its given container instructions. To see available services, perform `faro status -a`'''
    epilog = '''Created by Joel Brogan - broganjr@ornl.gov'''

    version = faro.__version__

    # Setup the parser
    parser = optparse.OptionParser(usage='%s command [OPTIONS] %s' % (sys.argv[0], args),
                                   version=version, description=description, epilog=epilog,conflict_handler="resolve")

    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False,
                      help="Print out more program information.")
    # parser.add_option("--service-name",type="str",dest="service_name",default=None,help="The name to be given to the service")
    # parser.add_option("--algorithm",type="str",dest="algorithm",default=None,help="the algorithm to start up")
    parser.add_option( "--mode", type="choice", choices=['docker','venv','conda','native',None], dest="mode", default=None,
                     help="Choose an option.")
    # parser.add_option("--worker-count", type="int", dest="num_workers", default=1,
    #                   help="How many workers to start up for asyrconous usage. Default=1")

    # addConnectionOptions(parser)

    # Parse the arguments and return the results.

    addConnectionOptions(parser)
    ffs.addServiceOptionsGroup(parser)
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


def enrollCsvParseOptions():
    """
    Parse command line arguments.
    """
    args = ['enroll_list.csv']  # Add the names of arguments here.
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
        print(("Error: Please supply a csv file with fields subject_id,name,filename."))
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

def subjectDeleteOptions():
    '''
    Parse command line arguments.
    '''
    args = ['gallery_name','subject_id'] # Add the names of arguments here.
    n_args = len(args)
    args = " ".join(args)
    description = '''Delete subjects in a gallery.'''
    epilog = '''Created by David Bolme - bolmeds@ornl.gov'''
    
    version = faro.__version__
    
    
    
    # Setup the parser
    parser = optparse.OptionParser(usage='%s command [OPTIONS] %s'%(sys.argv[0],args),version=version,description=description,epilog=epilog)

    parser.add_option( "-v", "--verbose", action="store_true", dest="verbose", default=False,
                      help="Print out more program information.")
    
    addConnectionOptions(parser)

    # Parse the arguments and return the results.
    (options, args) = parser.parse_args()
    
    if len(args) < n_args:
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

def fuseParseOptions():
    """
    Parse command line arguments.
    """
    args = ['score_file_dir']  # Add the names of arguments here
    n_args = len(args)
    args = " ".join(args)
    description = '''Fuse scored results from different algorithms'''
    epilog = '''Created by Joel Brogan - broganjr@ornl.gov'''
    version = faro.__version__

    # Setup the parser
    parser = optparse.OptionParser(usage='%s command [OPTIONS] %s' % (sys.argv[0], args),
                                   version=version, description=description, epilog=epilog)
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False,
                      help="Print out more program information.")
    addFuseOptions(parser)

    (options, args) = parser.parse_args()
    if len(args) < 2:
        parser.print_help()
        print()
        print(("Error: Please supply at least one directory or two csv score files for fusion"))
        print()
        exit(-1)

    return options, args

def detect():
    options, args = detectParseOptions()
    faro.command_line.detect(options,args)

def detectExtract():
    options, args = detectParseOptions()
    faro.command_line.detectExtract(options,args)

def extractOnly():
    options, args = detectParseOptions()
    faro.command_line.extractOnly(options,args)

def enroll():
    options, args = enrollParseOptions()
    faro.command_line.enroll(options,args)

def enroll_csv():
    options, args = enrollCsvParseOptions()
    faro.command_line.enroll_csv(options,args)

def elist():
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
    
def sdelete():
    options,args = subjectDeleteOptions()
    face_client = connectToFaroClient(options)
    gallery_name = args[1]
    subject_id = args[2]
    result = face_client.subjectDelete(gallery_name,subject_id)
    print("Deleted %d records."%(result.delete_count))
    
def search():
    options, args = searchParseOptions()
    options.search_log = options.search_csv
    faro.command_line.search(options,args)

def test():
    """
    Run a recognition test and compute a distance matrix and optionally other results.
    """
    options, args = testParseOptions()
    faro.command_line.test(options,args)

def fuse():
    options, args = fuseParseOptions()
    command_line.fuse(options, args)
    
    
def status():
    """
    Conects to the server and gets status information.
    """
    options,args = statusParseOptions()
    command_line.status(options)

def secure():
    faro.util.generateKeys(os.path.join(faro.__path__[0],'keystore'))

def start():
    options,args = startParseOptions()
    command_line.startService(options)

COMMANDS = {
    'status' : ['Connects to the server and displays version and status information.',status],
    'start' : ['Starts up an instance of a given FaRO service',start],
    'detect' : ['Only run face detection.',detect],
    'detectExtract' : ['Run face detection and template extraction.',detectExtract],
    'extractOnly' : ['Only run face extraction and attribute extraction.',extractOnly],
    'enroll' : ['Extract faces and enroll faces in a gallery.',enroll],
    'enrollCsv' : ['Extract faces and enroll faces in a gallery.',enroll_csv],
    'elist' : ['List the enrollments in a gallery.',elist],
    'sdelete' : ['Delete a subjects in a gallery.',sdelete],
    'glist' : ['List the galleries on the service.',command_line.glist],
    'gdelete' : ['Delete a gallery.',command_line.gdelete],
    'search' : ['Search images for faces in a gallery.',search],
    'test' : ['Process a probe and gallery directory and produce a distance matrix.',test],
    'fuse' : ['Fuse scored results from different algorithms',fuse],
    'secure' : ['create RSA certificates for secured communication', secure]
            }

def face_command_line():
    cv2.setNumThreads(16) # TODO: Make this an option

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
    raise NotImplementedError("This main function has been removed. Please use: 'python -m faro ...'")
