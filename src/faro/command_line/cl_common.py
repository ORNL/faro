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

import optparse

import faro

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

    parser.add_option_group(connection_group)



def connectToFaroClient(options,no_exit=False,quiet=False,timeout=None,return_status=False):
    if options.verbose and not quiet:
        print('Connecting to FaRO Service...')

    face_client = faro.FaceClient(options,timeout=timeout)
    message = face_client.initial_status
    is_ready = message[0]
    status = message[1]
    # is_ready, status = face_client.status(verbose=options.verbose,timeout=timeout)
    if not is_ready:
        if not quiet:
            print("ERROR: the FaRO service is not ready.")
            print(status)
        if not no_exit:
            exit(-1)
    else:
        if options.verbose:
            if not quiet:
                print('Connection to FaRO service established. [ algorithm: %s ]' % (status.algorithm))
    if return_status:
        return face_client,status
    else:
        return face_client
