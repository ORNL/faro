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

import faro.util

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

import signal
class sigintThread(threading.Thread):
    def signalint_handler(sig, frame):
        faro.util.setGlobalValue('shouldstopserver',1)
        verbose = False
        # if verbose:
        # sys.exit(0)
    signal.signal(signal.SIGINT, signalint_handler)

import multiprocessing as mp

class KeyboardThread(mp.Process):
    def __init__(self,inputVar):
        super(KeyboardThread, self).__init__()
        self.input = inputVar
    def run(self):
        self.timedout = False

        try:
            try:
                inp = fgetch()
                self.input.value = inp
            except OverflowError as e:
                pass

        except Exception as e:
            # print('exit from sigint',e)
            self.input.value = chr(27)
        return

def waitForInput():
    return fgetch()

def readInput(timeout = 5):
    if fgetch is not None:
        result = None
        inputVar = mp.Manager().Value('c','')
        it = KeyboardThread(inputVar)
        it.start()
        it.join(timeout)
        it.timedout = True
        if len(it.input.value) > 0:
            result = it.input.value
        return result
    else:
        time.sleep(timeout)
        return None


from multiprocessing import Manager
globaldict = None
def getGlobalValue(key):
    # print('get global val',key)
    try:
        global globaldict
        if globaldict == None:
            # print('starting dictionary singleton')
            globaldict = Manager().dict()
    except Exception as e:
        pass
        # print('error in getglobalval')

    try:
        if key in globaldict:
            return globaldict[key]
    except:
        return None
def setGlobalValue(key,val):
    try:
        global globaldict
        if globaldict == None:
            # print('starting dictionary singleton')
            globaldict = Manager().dict()
    except Exception as e:
        pass
        # print('error in getglobalval')
    try:
        # print('set global val',val)
        globaldict[key] = val
    except:
        pass

def getcv2info(key):
    import cv2
    cv2_info = cv2.getBuildInformation().split('\n')
    for l in cv2_info:
        if key.lower() in l.lower():
            if 'yes' in l.lower():
                return True
    return False

def generateKeys(keystore_dir,country='US',state='Tennessee',city='Knoxville',commonname='localhost',org='Oak Ridge National Laboratory',email='default@ornl.gov'):
    import socket
    keypath = os.path.join(keystore_dir,'server.key')
    crtpath = os.path.join(keystore_dir,'server.crt')
    if not os.path.exists(keystore_dir):
        os.makedirs(keystore_dir)
    #method outlined in:
    # https://stackoverflow.com/questions/23523456/how-to-give-a-multiline-certificate-name-cn-for-a-certificate-generated-using
    # https://security.stackexchange.com/questions/74345/provide-subjectaltname-to-openssl-directly-on-the-command-line
    dnsnames = ["DNS:"+socket.gethostname(),'DNS:127.0.0.1','DNS:localhost']
    command1 = 'openssl genrsa -out ' + keypath +' 2048'
    command2 = 'openssl req -new -x509 -sha256 -key ' + keypath + ' -out ' + crtpath + ' -days 3650 -addext "subjectAltName = ' + ",".join(dnsnames) + '"' + ' -subj "'
    subj = ''
    if country is not None:
        command2 += '/C=' + country
    if state is not None:
        command2 += '/ST=' + state
    if city is not None:
        command2 += '/L=' + city
    if org is not None:
        command2 += '/O=' + org
    if commonname is not None:
        command2 += '/CN=' + commonname
    if email is not None:
        command2 += '/emailAddress=' + email
    subj = subj+'"'
    command2 += subj
    print('Generating server-client SHA keys and certificates...')
    os.system(command1)
    os.system(command2)
    if os.path.exists(keypath) and os.path.exists(crtpath):
        print('Secure key pairs have been successfully written! Please copy "', crtpath, '" to the client machine and load via the "--certificate" flag')
    else:
        print('An error occured in generating the key pair')
    #https://github.com/joekottke/python-grpc-ssl
    #~/cfssl/bin/cfssl gencert -initca ca-csr.json | ~/cfssl/bin/cfssljson -bare ca
    #~/cfssl/bin/cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -hostname='127.0.0.1,localhost' server-csr.json | ~/cfssl/bin/cfssljson -bare server
    #~/cfssl/bin/cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json client-csr.json | ~/cfssl/bin/cfssljson -bare client
