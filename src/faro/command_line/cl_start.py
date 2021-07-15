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
import os
import socket
import time

import faro
import importlib
import sys
from sortedcollections import SortedDict
from faro.command_line.cl_common import connectToFaroClient
tqdm = faro.util.safe_tqdm()


#To start a service:
# 1) check if name is already running as a local or bonjour service
# 2) check if


def startService(options):
    #Check if a service is already running with the given name
    service_name = options.service_name
    options.service_name = None
    currentlyRunningServices = faro.command_line.getRunningWorkers(options, asDict=True)

    if service_name in currentlyRunningServices:
        print('we have found a service already running with the name ',service_name)

    else:
        available_algorithms = faro.command_line.getFaceWorkers(options,asDict=True)
        if options.algorithm in available_algorithms:
            print('we can start the algorithm, ', options.algorithm)
            alg = available_algorithms[options.algorithm]
            startup_modes = alg['environment Type']
            startupMode = None
            if options.mode is not None:
                if options.mode in startup_modes:
                    print('Algorithm ', options.algorithm,' is bootable via ', options.mode)
                else:
                    assert False, 'Algorithm ' + options.algorithm + ' is not bootable via ' + options.mode
            if options.mode is None:
                if startup_modes is None or len(startup_modes) == 0:
                    startupMode = 'Native'
                elif len(startup_modes) > 0:
                    startupMode = startup_modes[0]
                    print('chosing startup mode ', startupMode)

            if startupMode is None:
                startupMode = 'native'

            if startupMode.lower() == "docker":
                print('calling docker loader...')
                faro.ServiceEnvironmentLoader.startByDocker(options,service_name,alg["service files"])



