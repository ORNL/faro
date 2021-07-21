'''
MIT License

Copyright 2020 Oak Ridge National Laboratory

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

import sys
import optparse

import faro
from faro.command_line import addConnectionOptions, connectToFaroClient

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


def galleryDeleteOptions():
    '''
    Parse command line arguments.
    '''
    args = [] # Add the names of arguments here.
    n_args = len(args)
    args = " ".join(args)
    description = '''Delete galleries for this service.'''
    epilog = '''Created by David Bolme - bolmeds@ornl.gov'''
    
    version = faro.__version__
    
    
    
    # Setup the parser
    parser = optparse.OptionParser(usage='%s command [OPTIONS] %s'%(sys.argv[0],args),version=version,description=description,epilog=epilog)

    parser.add_option( "-v", "--verbose", action="store_true", dest="verbose", default=False,
                      help="Print out more program information.")
    
    parser.add_option( "-f", "--force", action="store_true", dest="force", default=False,
                      help="Don't ask the user to confirm deletion.")
    
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



def glist():
    options,args = galleryListOptions()

    face_client = faro.command_line.connectToFaroClient(options)

    result = face_client.galleryList()
    
    print()
    print("%-24s | %10s"%('GALLERY NAME','FACE_COUNT'))
    print('-'*37)
    for gallery in result.galleries:
        print("%-24s | %10d"%(gallery.gallery_name,gallery.face_count))
    print()
    

def gdelete():
    options,args = galleryDeleteOptions()

    gallery_name = str(args[1])
    assert len(gallery_name)

    confirm = 'N'
    if not options.force:
        confirm = input("Please confirm you want to delete gallery '%s' (N/y):"%(gallery_name,))
    else:
        confirm = 'Y'

    face_client = connectToFaroClient(options)
    
    if confirm.upper() in ('Y','YES'):
        result = face_client.galleryDelete(gallery_name)
    
    print(result)