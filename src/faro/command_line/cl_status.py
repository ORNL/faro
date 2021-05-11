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
    print('Warning: could not load Bonjour services. This worker will not be broadcast. To enable broadcasting capabilities, perform `pip install zeroconf`')

def status(options):
    active = options.active
    inactive = options.inactive
    if options.all:
        active = True
        inactive = True
    if inactive:
        inactiveWorkers = getNonrunningWorkers()
        print("\nWorkers not currently runnin gon network")
        print(tabulator(inactiveWorkers))
    if active:
        print("\nWorkers currently running on network:")
        activeWorkers = getRunningWorkers()
        print(tabulator(activeWorkers))

class ServiceListener:
    availableServices = SortedDict()
    availableServices_tableform = SortedDict()
    timeout = 1
    lastUpdate = -1
    def remove_service(self, zeroconf, type, name):
        # print("Service %s removed" % (name,))
        del self.availableServices[name]
        del self.availableServices_tableform[name]

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        self.availableServices[name] = info
        props = {k.decode():info.properties[k].decode() for k in info.properties}
        # row = {'algorithm':props['algorithm'],'address':socket.inet_ntoa(info.addresses[0]),'port':info.port,'FaRO version':props['version']}
        row = SortedDict({'address':socket.inet_ntoa(info.addresses[0]),'port':info.port})
        row.update(props)
        if 'functionality' in row:
            del row['functionality']
        self.availableServices_tableform[name] = row
        self.lastUpdate = time.time()
        # print("Service %s added, service info: %s" % (name, info))

def getRunningWorkers():
    if Zeroconf is not None:
        zeroconf = Zeroconf()
        listener = ServiceListener()
        browser = ServiceBrowser(zeroconf, "_faro._tcp.local.", listener)
        starttime = time.time()
        while True:
            if listener.lastUpdate > 0:
                if time.time()-listener.lastUpdate >= listener.timeout or time.time()-starttime > 10:
                    break
            elif time.time()-starttime > 10:
                break

        return listener.availableServices_tableform.values()
    else:
        print('\nBonjour libraries are not installed.  Please perform `pip install zeroconf` to access broadcasting capabilities')
        return []


def getNonrunningWorkers():
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
    if 'FARO_WORKER_PATH' in os.environ:
        worker_dirs = os.environ['FARO_WORKER_PATH'].split(":")
        print("Workers Dirs:", worker_dirs)
        for worker_dir in worker_dirs:

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

    for each,loc in zip(scripts,script_locations):
        name = each[:-13].lower()
        loadable = True
        row = SortedDict({"Algorithm": name,'location':loc})
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
    return tablerows
