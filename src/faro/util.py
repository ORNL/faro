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

Created on Feb 10, 2019

@author: bolme
'''

import os
import sys
import socket
import subprocess
import threading
import time

_keras = None
_K = None

_tf = None
_tf_sess = None

def loadKeras(gpu_id = None):
    '''
    Use this function to load keras in a safe way that limits gpu memory usage
    and allows multiple workerns on a single gpu.
    '''        
    global _keras
    global _K
    
    if _keras is None:
        global FACE_ALG 
        import keras.backend as K
        
        config = K.tf.ConfigProto()
        config.gpu_options.allow_growth = True
        session = K.tf.Session(config=config)
        K.set_session(session)
        
        import keras
        
        _keras = keras
        _K = K
    
    return _keras, _K

def getTensorflowSession(gpu_id = None):
    
    global _tf
    global _tf_sess
    
    if _tf == None:
        import tensorflow as tf
        _tf = tf
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        #config.gpu_options.per_process_gpu_memory_fraction = 0.2
        _tf_sess = tf.Session(config=config)
        
    return _tf, _tf_sess

def optionalImport(libname):
    if getPythonVersion() == 3:
        import importlib
        try:
            module = importlib.import_module(libname)
            return module
        except Exception as E:
            print('could not load optional module: ', libname)
            return None
    elif getPythonVersion() == 2:
        import imp
        try:
            imp.find_module(libname)
            module = imp.load_module(libname)
            return module
        except ImportError:
            print('could not load optional module: ', libname)
            return None
    return None

def getPythonVersion():
    if (sys.version_info > (3, 0)):
        # Python 3 code in this block
        return 3
    else:
        # Python 2 code in this block
        return 2

def getHostName():
    fqdn = socket.gethostname()
    ip = None
    try:
        ip = socket.gethostbyname(fqdn)
    except:
        pass
    if ip is None:
        try:
            fqdn = socket.getfqdn()
            ip = socket.gethostbyname(fqdn)
        except:
            pass
    if ip is None:
        fqdn = 'localhost'
        ip = socket.gethostbyname(fqdn)
    return ip

def getServiceDomains():
    # Scan for other workers
    service_domains = ['localhost']
    if 'FARO_DOMAINS' in os.environ:
        service_domains.extend(os.environ['FARO_DOMAINS'].split(":"))
    return service_domains

def pingDomain(domain):
    process = subprocess.Popen("ping -c 1 " + domain, shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    # wait for the process to terminate
    response, err = process.communicate()
    errcode = process.returncode
    # response = os.system()
    # and then check the response...
    if errcode == 0:
        return True
    else:
        return False

def safe_tqdm():
    def progress_passthrough(v):
        return v
    try:
        from tqdm import tqdm
        return tqdm
    except:
        return progress_passthrough

def safe_tabulator():
    try:
        import tabulate
        def tabulator(x):
            import tabulate
            return tabulate.tabulate(x, headers='keys')
    except:
        print('Warning: Tabulate not installed, defaulting to string print (install via `pip install tabulate`')
        tabulator = str
    return tabulator


def readInput_unix(timeout = 5):
    pass

fgetch = None
try:
    import msvcrt
    fgetch = msvcrt.getch
except:
    pass
if fgetch is None:
    try:
        import getch
        fgetch = getch.getch
    except:
        print('warning: getch is not installed. Install via `pip install getch`')


class sigintThread(threading.Thread):
    import signal
    def signal_handler(sig, frame):
        print('You pressed Ctrl+C! Press `enter` to terminate the server')
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)


class KeyboardThread(threading.Thread):
    def run(self):
        self.timedout = False
        self.input = ''
        try:
            chr = fgetch()
            # print("char: ",ord(chr))
            self.input = chr
            # if ord(chr) == 13:
            #     break
        except Exception as e:
            print('Ended listener with exception: ',e)
        return

            # elif ord(chr) >= 32:
            # self.input += chr
            # if len(self.input) == 0 and self.timedout:
            #     break

def readInput(timeout = 5):
    if fgetch is not None:
        result = None
        it = KeyboardThread()

        # print('starting input thread')
        it.start()
        # print('joining input with ', timeout, 'seconds')
        it.join(timeout)
        # print('joined')
        it.timedout = True
        if len(it.input) > 0:
            # wait for rest of input
            it.join()
            result = it.input
        return result
    else:
        time.sleep(timeout)
        return None
