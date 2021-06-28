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
import copy

import faro
import importlib
import sys
from sortedcollections import SortedDict
from faro.command_line.cl_common import connectToFaroClient
try:
    import tabulate
    def tabulator(x):
        return tabulate.tabulate(x,headers='keys')
except:
    print('Warning: Tabulate not installed, defaulting to string print (install via `pip install tabulate`')
    tabulator = str

try:
    from zeroconf import ServiceInfo,Zeroconf,ServiceBrowser
except:
    Zeroconf = None
    print('Warning: could not load Bonjour services. This worker will not be broadcast. To enable broadcasting capabilities, install via `pip install zeroconf`')

try:
    from tqdm import tqdm
except:
    tqdm = None

def status(options):
    active = options.active
    inactive = options.inactive
    if options.all:
        active = True
        inactive = True
    if inactive:
        availableFaceWorkers = getFaceWorkers()
        print("\nCurrently available FaRO Face Workers")
        print(tabulator(availableFaceWorkers))
    if active:
        print('Scanning for workers on network...')
        activeWorkers = getRunningWorkers(options)
        if len(activeWorkers) > 0:
            print("\nWorkers currently running on network:")
            print(tabulator(activeWorkers))
        else:
            print("No actively broadcasting workers found")
        # getRunningLocalWorkers(options)

class ServiceListener:
    availableServices = SortedDict()
    availableServices_tableform = SortedDict()
    timeout = 1
    lastUpdate = -1
    def __init__(self):
        self.hostname = faro.util.getHostName()
    def remove_service(self, zeroconf, type, name):
        # print("Service %s removed" % (name,))
        del self.availableServices[name]
        del self.availableServices_tableform[name]

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        self.availableServices[name] = info
        props = {k.decode():info.properties[k].decode() for k in info.properties}
        # row = {'algorithm':props['algorithm'],'address':socket.inet_ntoa(info.addresses[0]),'port':info.port,'FaRO version':props['version']}
        address = socket.inet_ntoa(info.addresses[0])
        if self.hostname == address:
            address = "localhost"
        row = SortedDict({'address':address,'port':info.port,'found via':'bonjour'})
        row.update(props)
        if 'functionality' in row:
            del row['functionality']
        self.availableServices_tableform[name] = row
        self.lastUpdate = time.time()
        # print("Service %s added, service info: %s" % (name, info))

def getRunningLocalWorkers(options): #no zeroconf
    localservices = []
    for domain in faro.util.getServiceDomains():
        # print('looking at', domain)
        if faro.util.pingDomain(domain):
            portrange = range(50000,50254)
            if options.verbose: portrange = tqdm(portrange)
            options.service_name=None
            for portnum in portrange:
                t0 = time.time()
                port = domain+":"+str(portnum)
                options.port = port

                face_client = connectToFaroClient(options,no_exit=True,quiet=True,timeout=2)
                available,message = face_client.status(timeout=2)
                if available:
                    row = SortedDict({'address': domain, 'port': str(portnum),'Algorithm':message.algorithm,"workers":message.worker_count,"Name":message.instance_name,"FaRO version":message.faro_version,"found via":'port sweep'})
                    localservices.append(row)
                t1 = time.time()
                if t1-t0 > 2: #this connection is taking too long
                    break
        else:
            if options.verbose:
                print('Domain ', domain, ' is unavailable')
    return localservices


def getRunningWorkers(options,asDict=False,keyedOn='Name'):
    bonjourservicesLocations = []
    if Zeroconf is not None:
        zeroconf = Zeroconf()
        listener = ServiceListener()
        browser = ServiceBrowser(zeroconf, "_faro._tcp.local.", listener)
        starttime = time.time()
        # if tqdm is not None:
        #     pbar = tqdm(total=100)
        # while True:
        #     if listener.lastUpdate > 0:
        #         if time.time()-listener.lastUpdate >= listener.timeout or time.time()-starttime > 10:
        #             break
        #     elif time.time()-starttime > 1.75:
        #         break
        #     pbar.update(8)
        #     time.sleep(.1)
        localservices = getRunningLocalWorkers(copy.copy(options))
        bonjourservices = list(listener.availableServices_tableform.values())
        bonjourservicesLocations = [s['address']+str(s['port']) for s in bonjourservices]
        for s in localservices:
            if s['address']+str(s['port']) not in bonjourservicesLocations:
                bonjourservices.append(s)
        if asDict:
            return {s[keyedOn]:s for s in bonjourservices}
        return bonjourservices

    else:
        print('\nBonjour libraries are not installed.  Please perform `pip install zeroconf` to access WLAN broadcasting capabilities')
        try:
            localservices = getRunningLocalWorkers(copy.copy(options))
            if asDict:
                return {s[keyedOn]: s for s in localservices}
            return localservices
        except Exception as e:
            print(e)
        if asDict: return {}
        return []


def getFaceWorkers(asDict=False):
    # Scan for faro workers
    import_dir = faro.__path__[0]
    scripts = os.listdir(os.path.join(import_dir, 'face_workers'))
    scripts = filter(lambda x: x.endswith('FaceWorker.py'), scripts)
    sys.path.append(os.path.join(import_dir, 'face_workers'))
    scripts = list(scripts)
    script_locations = [import_dir]*len(scripts)
    scripts.sort()
    FACE_WORKER_LIST = SortedDict()
    # Scan for other workers

    #TODO make the services path an env, not hard coded
    SERVICE_DIRS=[]
    if os.getenv('FARO') is not None:
        SERVICE_DIRS.append(os.path.join(os.getenv('FARO'), 'services'))
    print("service dirs:",SERVICE_DIRS)

    if 'FARO_WORKER_PATH' in os.environ:
        worker_dirs = os.environ['FARO_WORKER_PATH'].split(":")
        for worker_dir in worker_dirs:
            print('worker_dir:',worker_dirs)
            # import_dir = faro.__path__[0]
            try:
                worker_scripts = os.listdir(worker_dir)
            except:
                print("ERROR - Could not read directory in FARO_WORKER_PATH:", worker_dir)
                raise
            worker_scripts = list(filter(lambda x: x.endswith('FaceWorker.py'), worker_scripts))
            sys.path.append(worker_dir)
            scripts += list(worker_scripts)
            script_locations += [worker_dir]*len(list(worker_scripts))
            scripts.sort()
    tablerows = []

    availableServices = {}
    for sdir in SERVICE_DIRS:
        if os.path.exists(sdir) and os.path.isdir(sdir):
            availableServices.update({d:os.path.join(sdir,d) for d in os.listdir(sdir)})
    for each,loc in zip(scripts,script_locations):
        name = each[:-13].lower()
        loadable = True

        # Check if the given FaceWorker has an associated service environment
        serviceLocation = None
        serviceLoadType = []
        loc2 = loc
        if name in availableServices:
            serviceLocation = availableServices[name]
            serviceFiles = os.listdir(serviceLocation)
            loc2 = serviceLocation
            if "Dockerfile" in serviceFiles:
                serviceLoadType.append("Docker")
            if "environment.yml" in serviceFiles:
                serviceLoadType.append("Conda")
            if "requirements.txt" in serviceFiles:
                serviceLoadType.append("venv")
        if len(serviceLoadType)==0:
            serviceLoadType.append('native')

        row = SortedDict({"Algorithm": name, 'location': loc2, 'service files':serviceLocation,'environment Type':serviceLoadType})



        try:
            module = importlib.import_module(each[:-3])
            class_obj = getattr(module, each[:-3])
            # print("    Loaded: ", name, '-', class_obj)
            FACE_WORKER_LIST[name] = [class_obj, None, None]
            row['gallery capabilities'] = False
            if 'getOptionsGroup' in dir(module):
                FACE_WORKER_LIST[name][1] = module.getOptionsGroup
            if 'getGalleryWorker' in dir(module):
                FACE_WORKER_LIST[name][2] = module.getGalleryWorker
                row['gallery capabilities'] = True
            row['natively loadable'] = True
        except Exception as e:
            row['natively loadable'] = False
            row['error'] = e
        tablerows.append(row)
    if asDict:
        return {s['Algorithm']:s for s in tablerows}
    return tablerows
