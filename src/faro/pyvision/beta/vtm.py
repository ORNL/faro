'''
Created on Oct 21, 2011

@author: bolme
'''

import time
from collections import defaultdict
import cProfile
import traceback
import shelve


class EmptyData(object):
    def __str__(self):
        return "<MissingData>"

class DefaultData(object):
    def __init__(self,default):
        self.default = default
    
    def __str__(self):
        tmp = str(self.default)
        tmp = " ".join(tmp.split()) # Flatten to one line an collapse white space to single spaces
        if len(tmp) > 40:
            tmp = tmp[:37] + "..."
        return "<DefaultData:%s>"%(tmp,)

EMPTY_DATA = EmptyData()

#############################################################################
# Video tasks are opperations to be run on a frame.
#############################################################################
class VideoTask(object):
    '''
    This provides an interface and support functions for a video processing 
    task.  Typically a subclass will overide the constructor which will 
    be used as a task factory and will create the task and specify the 
    arguments.
    '''
    
    # TODO: optional args should also be added which are included if avalible but will not delay execution if they are not avalible. 
    def __init__(self,frame_id,args=[]):
        '''
        @param frame_id: the frame_id associated with this task.
        @param args: specification of the data that is required to execute the task.
        '''
        self.frame_id = frame_id
        self.args = args

        self.task_id = None
        self.label = self.__class__.__name__
        if not hasattr(self,'subgraph'):
            self.subgraph = None
        if not hasattr(self,'color'):
            self.color = None

        self._arg_map = {}
        self._added_args = 0 # keep track of how many arguments have been found.
        self._default_args = 0 # keep track of how many arguments are currently default.
        for i in range(len(args)):
            each = args[i]
            dtype = each[0]
            fid = each[1]
            key = (dtype,fid)
            #if self._arg_map.has_key(key):
            #    continue
            if len(each) == 2:
                self._arg_map[key] = EMPTY_DATA
            elif len(each) == 3:
                self._arg_map[key] = DefaultData(each[2])
                self._default_args += 1
            else:
                raise ValueError("Argument should have 2 or 3 values: %s"%each)
                        
        self.collected_args = [False for each in self.args]
        self.processed_args = [each for each in self.args]
        self.distributable = False
        self.is_ready = False
        
    
    def addData(self, data_item):
        '''
        Check to see if the data item is needed for this task.  If it is then keep a reference.
        '''
        # Compute the key
        key = (data_item.getType(),data_item.getFrameId())
        
        # Check if this task needs the data
        if key in self._arg_map:
            curr_val = self._arg_map[key]
            
            # If no default save the data and update counts
            if curr_val == EMPTY_DATA: 
                self._arg_map[key] = data_item.getData()
                self._added_args += 1
                return True
            
            # If there is a default replace and update counts
            elif isinstance(curr_val,DefaultData):
                self._arg_map[key] = data_item.getData()
                self._added_args += 1
                self._default_args -= 1
                assert self._default_args >= 0 # This should only fail if there is an error in counting.
                return True
        return False
            
        
    def ready(self):
        '''
        Returns True if this task is ready to run.
        '''
        return self._added_args == len(self._arg_map)

    
    def couldRun(self):
        '''
        Returns True if this task could run with the default arguments.
        '''        
        return self._added_args + self._default_args == len(self._arg_map)

        
    def run(self):
                
        args = []
        for i in range(len(self.args)):
            each = self.args[i]
            key = (each[0],each[1])
            if isinstance(self._arg_map[key],DefaultData):
                args.append(self._arg_map[key].default)
            else:
                args.append(self._arg_map[key])
                            
        return self.execute(*args)
    
        
    def getFrameId(self):
        '''
        @returns: the frame_id associated with this task.
        '''
        return self.frame_id
    
    def required(self):
        '''
        @returns: the list of required data.
        '''
        return self.args
        
    def execute(self, *args, **kwargs):
        '''
        This is an abstract method that needs to be implemented in subclasses.
        One argument is suppled for each item in the required arguments. This
        method should return a list of new data items.  If no data is 
        generated by this method an empty list should be returned.
        '''
        raise NotImplementedError("Abstract Method")
    
    def printInfo(self):
        print("VideoTask {%s:%d}"%(self.__class__.__name__,self.getFrameId()))
        for key in list(self._arg_map.keys()):
            dtype,frame_id = key
            
            if self._arg_map[key] is EMPTY_DATA or isinstance(self._arg_map[key],DefaultData):
                print("    Argument <%s,%d> -> %s"%(dtype,frame_id,str(self._arg_map[key])))
            
            else:
                tmp = str(self._arg_map[key])
                tmp = " ".join(tmp.split()) # Flatten to one line an collapse white space to single spaces
                if len(tmp) > 40:
                    tmp = tmp[:37] + "..."
                print("    Argument <%s,%d> -> %s"%(dtype,frame_id,tmp))    


class _VideoDataItem(object):
    '''
    This class keeps track of data items and when they are used.
    '''
    def __init__(self,data_tuple):
        self._data_type = data_tuple[0] 
        self._frame_id = data_tuple[1]
        self._data = data_tuple[2]
        self._touched = 0
    
    def getType(self):
        ''' Get the item type. '''
        return self._data_type
    
    def getFrameId(self):
        ''' Get the frame id. '''
        return self._frame_id
    
    def getData(self):
        ''' Get the actual data. '''
        return self._data
    
    def getKey(self):
        ''' Get the key. '''
        return (self._data_type,self._frame_id)
    
    def touch(self):
        ''' Count the number of times this data was touched. '''
        self._touched += 1
        
    def getTouched(self):
        ''' Return the number of times the data was touched. '''
        return self._touched
    
    def __repr__(self):
        return "_VideoDataItem((%s,%s,%s)"%(self._data_type,self._frame_id,self._data)



def vtmProcessor(task_queue,results_queue,options):
    '''
    Each task_queue item should have three items (task_id,frame_id,command/task).
    the command "quit" is used to stop the process.
    
    The vtmProcessor will return (task_id, frame_id, results).  If there is an exception
    then the result will be replaced by the exception and a stack trace will be printed.
    '''
    
    while True:
        item = task_queue.get()
        try:
            task_id,frame_id,task = item
            
            result = task.run()

            results_queue.put((task_id,frame_id,result))
            
        except Exception as error:
            traceback.print_exc()
            results_queue.put((task_id,frame_id,error))
            

#############################################################################
# This class manages the workflow for video items.
#############################################################################
# TODO: Should we keep this name?
class VideoTaskManager(object):
    '''
    The framework provide by this class will allow complex video processing 
    systems to be constructed from simple tasks.  Often video processing 
    loops can be complicated because data needs to persist across many frame
    and many operations or tasks need to be completed to solve a video analysis
    problem.  This class allows for many small and simple tasks to be managed 
    in a way that can produce a complex and powerful system. #
        
    Tasks request only the data they need, which keeps the complexity of tasks 
    as simple as possible.  This also reduces the coupling between tasks and 
    eliminates complex video processing loops. The video task manager handles 
    much of the complexity of the video processing system like data buffering, 
    and insures that each task gets its required data. #

    This class manages tasks that are run on video frames.  The video task 
    manager maintains a list of data objects and task objects.  Each task is 
    a listener for data objects.  When the data objects are avalible required 
    to execute a task the tasks execute method will be called and the required 
    data items will be passed as arguments. #
    
    New frames are added using the addFrame method.  When a frame is added 
    it creates a data item that includes a frame_id, a data type of "FRAME",
    and a pv.Image that contains the frame data.  Tasks can register to 
    receive that frame data or any data products of other tasks and when
    that data becomes available the task will be executed.
    '''
    
    def __init__(self,debug_level=0, buffer_size=10, show = False):
        '''
        Create a task manager.
        
        @param debug_level: 0=quiet, 1=errors, 2=warnings, 3=info, 4=verbose
        @type debug_level: int
        @param buffer_size: the size of the frame and data buffer.
        @type buffer_size: int
        '''
        self.debug_level = debug_level
        
        # Initialize data.
        self.frame_id = 0
        self.task_list = []
        self.task_factories = []
        self.buffer_size = buffer_size
        
        self.frame_list = []
        self.show = show
        
        # Initialize information for flow analysis.
        self.flow = defaultdict(set)
        self.task_set = set()
        self.data_set = set((('FRAME',None),('LAST_FRAME',None),))
        self.task_data = defaultdict(dict)
        self.task_id = 0
        
        self.lastFrameCreated = 0

        self.recording_shelf = None
        self.playback_shelf = None
        self.recording_filter = None
        self.task_filter = None
        self.playback_filter = None
        
        if self.debug_level >= 3:
            print("TaskManager[INFO]: Initialized")
            

    def addTaskFactory(self,task_factory,*args,**kwargs):
        '''
        This function add a task factory function to the video task manager.
        The function is called once for every frame processed by the 
        VideoTaskManager.  This function should take one argument which
        is the frame_id of that frame.  The task factory should return an
        instance of the VideoTask class that will perform processing on this
        frame.  There are three options for implementing a task factory. #
         - A class object for a VideoTask which has a constructor that takes 
           a frame_id as an argument.  When called the constructor for that 
           class and will create a task.
         - A function that takes a frame id argument.  The function can 
           create and return a task.
         - Any other object that implements the __call__ method which 
           returns a task instance.
         
        Any additional arguments or keyword arguments passed to this 
        to this function will be pased after the frame_id argument
        to the task factory. #
        
        @param task_factory: a function or callible object that returns a task.
        @type  task_factory: callable 
        @param profile: Keyword argument.  If true, profile data will be 
                        generated for each call to this task.
        @type profile: True | False
        '''
        self.task_id += 1
        profile = False
        if 'profile' in kwargs:
            profile = kwargs['profile']
            del kwargs['profile']
        self.task_factories.append((task_factory,args,kwargs,profile,self.task_id))
        
        
    def addFrame(self,frame,ilog=None):
        '''
        Adds a new frame to the task manager and then start processing.
        
        @param frame: the next frame of video.
        @type  frame: pv.Image 
        '''
        # Add the frame to the data manager
        start = time.time()
        
        frame_data = _VideoDataItem(("FRAME",self.frame_id,frame))
        self._createTasksForFrame(self.frame_id)
        self.addDataItem(frame_data)
        last_data = _VideoDataItem(("LAST_FRAME",self.frame_id-1,False))
        self.addDataItem(last_data)
        self.frame_list.append(frame_data)
        
        # Playback the recording
        if self.playback_shelf != None and str(self.frame_id) in self.playback_shelf:
            data_items = self.playback_shelf[str(self.frame_id)]
            for each in data_items:
                if self.playback_filter==None or each.getType() in self.playback_filter:
                    self.addDataItem(each)
                    self.data_set.add((each.getKey()[0],None))
                    self.flow[('Playback',each.getType())].add(0)
                    
        # Run any tasks that can be completed with the current data.
        self._runTasks()
  
        if self.recording_shelf != None:
            self.recording_shelf.sync()
        # Delete old data
        #self._cleanUp()

        
        stop = time.time()
        
        # Set up for the next frame and display the results.
        self.frame_id += 1

        self.showFrames(ilog=ilog)
        
        if self.debug_level >= 3:
            print("TaskManager[INFO]: Frame Processing Time=%0.3fms"%(1000*(stop-start),))

    def addData(self,data_list):
        '''
        Add additional data for this frame. The data list should contain a list tuples where each tuple of (label, data)
        '''
        for each in data_list:
            data = _VideoDataItem((each[0],self.frame_id,each[1]))
            self.addDataItem(data)
            self.flow[('Data Input',data.getType())].add(0)
            self.data_set.add((data.getKey()[0],None))


        
        
    def addDataItem(self,data_item):
        '''
        Process any new data items and associate them with tasks.
        '''
        if self.recording_shelf != None:
            frame_id = str(self.frame_id)
            if frame_id not in self.recording_shelf:
                self.recording_shelf[frame_id] = []
            if self.recording_filter == None or data_item.getType() in self.recording_filter:
                self.recording_shelf[frame_id].append(data_item)
            
        for task in self.task_list:
            was_added = task.addData(data_item)
            if was_added:
                # Compute the dataflow
                self.flow[(data_item.getKey()[0],task.task_id)].add(data_item.getKey()[1]-task.getFrameId())

            
    def _createTasksForFrame(self,frame_id):
        '''
        This calls the task factories to create tasks for the current frame. 
        '''
        while self.lastFrameCreated < frame_id + self.buffer_size:
            start = time.time()
            count = 0
            for factory,args,kwargs,profile,task_id in self.task_factories:
                display_vars = ['display_color','display_subgraph']
                display_options = {k:v for (k,v) in kwargs.items() if k in display_vars}
                kwargs = {k:v for (k,v) in kwargs.items() if k not in display_vars}
                task = factory(self.lastFrameCreated,*args,**kwargs)
                
                # Setup Graph Display Options
                if 'display_color' in display_options:
                    print('setting color',display_options['display_color'])
                    task.color = display_options['display_color']
                if 'display_subgraph' in display_options:
                    print('setting subgraph',display_options['display_subgraph'])
                    task.subgraph = display_options['display_subgraph']
                    
                task.task_id=task_id
                self.task_data[task.task_id]['class_name'] = task.__class__.__name__

                task.profile=profile
                count += 1

                if self.task_filter == None or task.__class__.__name__ in self.task_filter:
                    self.task_list += [task]
            stop = time.time() - start
            if self.debug_level >= 3:
                print("TaskManager[INFO]: Created %d new tasks for frame %s. Total Tasks=%d.  Time=%0.2fms"%(count,self.lastFrameCreated,len(self.task_list),stop*1000))
            self.lastFrameCreated += 1
        
    def _runTasks(self,flush=False):
        '''
        Run any tasks that have all data available.
        '''
        if self.debug_level >= 3: print("TaskManager[INFO]: Running Tasks...")
        while True:
            start_count = len(self.task_list)
            remaining_tasks = []
            for task in self.task_list:
                if self._evaluateTask(task,flush=flush):
                    remaining_tasks.append(task)
            self.task_list = remaining_tasks
            if start_count == len(self.task_list):
                break

            
    def flush(self):
        '''
        Run all tasks that can be run and then finish up.  The LAST_FRAME data
        item will be set to true for the last frame inserted.
        '''
        last_data = _VideoDataItem(("LAST_FRAME",self.frame_id-1,True))
        self.addDataItem(last_data)

        self._runTasks(flush=True)
        
    def _evaluateTask(self,task,flush=False):
        '''
        Attempts to run a task.  This is intended to be run within a filter operation.
        
        @returns: false if task should be deleted and true otherwise.
        '''
        self.task_set.add(task.task_id)


        should_run = False
        
        if task.ready():
            should_run = True
        elif (flush or self.frame_id - task.getFrameId() > self.buffer_size) and task.couldRun():
            should_run = True
        elif (flush or self.frame_id - task.getFrameId() > self.buffer_size) and not task.couldRun():
            if self.debug_level >= 2: 
                print("TaskManager[WARNING]: Task %s for frame %d was not executed."%(task,task.getFrameId()))
                task.printInfo()
            
            # If the task is beyond the buffer, then delete it.
            return False

        # If the task is not ready then skip it for now.
        if not should_run:
            return True
        
        # Run the task.
        start = time.time()
        
        # Start the profiler
        if task.profile:
            prof = cProfile.Profile()
            prof.enable()
            
        # RUN THE TASK
        result = task.run()
        
        # Stop the profiler and show that information.
        if task.profile:
            prof.disable()
            print()
            print("Profiled task:",task.__class__.__name__)
            prof.print_stats('time')
            print()
            
        # Check that the task did return a list.
        try:
            len(result)
        except:
            raise Exception("Task did not return a valid list of data.\n    Task: %s\n    Data:%s"%(task,result))
                            
        # Record the dataflow information.
        for each in result:
            self.flow[(task.task_id,each[0])].add(0)
            self.data_set.add((each[0],task.subgraph))
            
        # Compute the dataflow
        for i in range(len(task.collected_args)):
            if task.collected_args[i]:
                each = task.processed_args[i]
                self.flow[(each.getKey()[0],task.task_id)].add(each.getKey()[1]-task.getFrameId())
                self.data_set.add((each.getKey()[0],task.subgraph))

                
        # Add the data to the cache.
        for data_item in result:
            if len(data_item) != 3:
                raise Exception("Task returned a data item that does not have 3 elements.\n    Task: %s\n    Data: %s"%(task,data_item))
            data_item = _VideoDataItem(data_item)
            self.addDataItem(data_item)
        stop = time.time() - start
        if self.debug_level >= 3:
            print("TaskManager[INFO]: Evaluate task %s for frame %d. Time=%0.2fms"%(task,task.getFrameId(),stop*1000))
        
        # Compute task statistics
        if 'time_sum' not in self.task_data[task.task_id]:
            self.task_data[task.task_id]['time_sum'] = 0.0
            self.task_data[task.task_id]['call_count'] = 0
        self.task_data[task.task_id]['time_sum'] += stop
        self.task_data[task.task_id]['call_count'] += 1
        self.task_data[task.task_id]['color'] = task.color
        self.task_data[task.task_id]['subgraph'] = task.subgraph
        
        # Return false so that the task is deleted.
        return False
    
    
    def _remainingTasksForFrame(self,frame_id):
        '''
        @returns: the number of tasks that need to be run for this frame.
        '''
        count = 0
        for task in self.task_list:
            if task.getFrameId() == frame_id:
                count += 1
        return count
    
    # TODO: I don't really like how show frames works.  I would like display of frames to be optional or maybe handled outside of this class.  How should this work.
    def showFrames(self,ilog=None):
        '''
        Show any frames with no remaining tasks.
        '''
        while len(self.frame_list) > 0:
            frame_data = self.frame_list[0]
            frame_id = frame_data.getFrameId()
            frame = frame_data.getData()
            task_count = self._remainingTasksForFrame(frame_id)
            # If the frame is complete then show it.
            if task_count == 0:
                if self.show:
                    frame.show(delay=1)
                if ilog != None:
                    ilog(frame,ext='jpg')
                del self.frame_list[0]
            else:
                break
    
    def recordingFile(self,filename):
        '''
        Set up an output file for recording.
        '''
        assert self.playback_shelf == None
        self.recording_shelf = shelve.open(filename, flag='n', protocol=2, writeback=True) 
    
    def playbackFile(self,filename,cache=False):
        '''
        Set up an input file for playback.
        '''
        assert self.recording_shelf == None
        self.playback_shelf = shelve.open(filename, flag='r', protocol=2, writeback=False) 
    
    def recordingFilter(self,data_types):
        '''
        Only recorded data_types in the list.
        '''
        self.recording_filter = set(data_types)
    
    def taskFilter(self,task_types):
        '''
        Only generate tasks in the list.
        '''
        self.task_filter = set(task_types)
    
    def playbackFilter(self,data_types):
        '''
        Only playback data_types in the list.
        '''
        self.playback_filter = set(data_types)
    
    def asGraph(self,as_image=False):
        '''
        This uses runtime analysis to create a dataflow graph for this VTM.
        '''
        import pydot
        import faro.pyvision as pv
        import PIL.Image
        from io import StringIO
        
        def formatNum(n):
            '''
            This formats frame offsets correctly: -1,0,+1
            '''
            if n == 0:
                return '0'
            else:
                return "%+d"%n
            
        def record_strings(my_list):
            return '{''}'
            
        # Create the graph.
        graph = pydot.Dot(graph_type='digraph',nodesep=.3,ranksep=.5)
        graph.add_node(pydot.Node("Data Input",shape='invhouse',style='filled',fillcolor='#ffCC99'))
        graph.add_node(pydot.Node("Video Input",shape='invhouse',style='filled',fillcolor='#ffCC99'))
        graph.add_edge(pydot.Edge("Video Input","FRAME"))
        graph.add_edge(pydot.Edge("Video Input","LAST_FRAME"))
        
        if self.playback_shelf != None:
            graph.add_node(pydot.Node("Playback",shape='invhouse',style='filled',fillcolor='#ffCC99'))

        subgraphs = {None:graph}
        
        # Add task nodes        
        for each in self.task_set:
            if 'call_count' in self.task_data[each]:
                class_name = self.task_data[each]['class_name']
                call_count = self.task_data[each]['call_count']
                mean_time = self.task_data[each]['time_sum']/call_count
                node_label = "{" + " | ".join([class_name,
                                           "Time=%0.2fms"%(mean_time*1000.0,),
                                           "Calls=%d"%(call_count,),
                                           ]) + "}"
                color = '#99CC99'
                print(each, self.task_data[each])
                if self.task_data[each]['color'] is not None:
                    color = self.task_data[each]['color']
                subgraph = self.task_data[each]['subgraph']
                subgraph_name = subgraph
                if subgraph_name != None:
                    subgraph_name = "_".join(subgraph.split())
                if subgraph not in subgraphs:
                    print("adding subgraph",subgraph)
                    subgraphs[subgraph_name] = pydot.Cluster(subgraph_name,label=subgraph,shape='box',style='filled',fillcolor='#DDDDDD',nodesep=1.0) 
                    subgraphs[None].add_subgraph(subgraphs[subgraph_name])
                print("adding node",each,subgraph)
                subgraphs[subgraph_name].add_node(pydot.Node(each,label=node_label,shape='record',style='filled',fillcolor=color))
            else:
                # The task node was never executed
                call_count = 0
                mean_time = -1
                class_name = self.task_data[each]['class_name']
                node_label = "{" + " | ".join([class_name,
                                           "Time=%0.2fms"%(mean_time*1000.0,),
                                           "Calls=%d"%(call_count,),
                                           ]) + "}"
                graph.add_node(pydot.Node(each,label=node_label,shape='record',style='filled',fillcolor='#CC3333'))

        # Add Data Nodes
        for each,subgraph in self.data_set:
            subgraph_name = subgraph
            if subgraph_name != None:
                subgraph_name = "_".join(subgraph.split())
            subgraphs[subgraph_name].add_node(pydot.Node(each,shape='box',style='rounded, filled',fillcolor='#9999ff'))
            
        # Add edges.
        for each,offsets in self.flow.items():
            offsets = list(offsets)
            if len(offsets) == 1 and list(offsets)[0] == 0:
                graph.add_edge(pydot.Edge(each[0],each[1]))
            else:
                offsets = formatOffsets(offsets)
                graph.add_edge(pydot.Edge(each[0],each[1],label=offsets,label_scheme=2,labeldistance=2,labelfloat=False))

        # Create a pv.Image containing the graph.                
        if as_image:
            data = graph.create_png()
            f = StringIO(data)
            im = pv.Image(PIL.Image.open(f))
            return im
        return graph

def formatGroup(group):
    try:
        if len(group) > 3:
            return formatGroup(group[:1])+"..."+formatGroup(group[-1:])
    except:
        pass
    return ",".join(["%+d"%each for each in group])

def groupOffsets(offsets):
    offsets.sort()
    group = []
    groups = [group]
    for each in offsets:
        if len(group) == 0 or each == group[-1]+1:
            group.append(each)
        else:
            group = [each]
            groups.append(group)
            
    
    return groups

def formatOffsets(offsets):
    groups = groupOffsets(offsets)
    out = "("+ ",".join([formatGroup(each) for each in groups]) + ")"
    return out
    
if __name__ == '__main__':
    offsets = [-3,-2,-1,0,1,3,4,5,6,7,8,10,15,20,21,22,23,-21,-22,56,57]
    offsets.sort()
    
    print(offsets)
    groups = groupOffsets(offsets)
    print(groups)
    print(",".join([formatGroup(each) for each in groups]))
