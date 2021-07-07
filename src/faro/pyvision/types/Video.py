# faro.pyvision License
#
# Copyright (c) 2006-2008 David S. Bolme, Stephen O'Hara
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
# 
# 3. Neither name of copyright holders nor the names of its contributors
# may be used to endorse or promote products derived from this software
# without specific prior written permission.
# 
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import time
import os
import faro.pyvision as pv
import random


class VideoInterface(object):
    '''
    VideoInterface is an abstract class meant only to define a common interface
    for all Video subtypes. The VideoInterface defines the methods that every
    video data source should provide.
    '''    
    def query(self):
        '''
        Must be overridden to implement the specific frame-grabbing required
        by different video sources.
        '''
        raise NotImplemented
    
    def grab(self):
        '''
        This is a placeholder for the open cv webcam interface that sometimes 
        requires this call.
        '''
        pass
    
    def next(self):
        return self.__next__()
    
    def __next__(self):
        '''
        The next method calls self.query(), so it is common to most video sources
        and may not need to be overridden.
        @return: The next frame in the sequence, or raise StopIteration if done.
        '''
        frame = self.query()
        if frame == None:
            raise StopIteration("End of video sequence")
        return frame
            
    def resize(self,frame):
        '''
        Used to resize the source frame to the desired output size. This
        method is common to most sources and may not need to be overridden.
        The query() method will typically call this resize() method prior
        to returning the captured image.
        @param frame: An openCV image (note: not a faro.pyvision image)
        @return: An openCV image with the new dimensions
        '''
        if self.size == None:
            return frame
        else:
            import cv2
            #depth = frame.depth
            #channels = frame.channels
            w,h = self.size
            #resized = cv.CreateImage( (w,h), depth, channels )
            resized = cv2.resize( frame, (w,h), cv2.INTER_LINEAR )
            return resized
    
    def __iter__(self):
        '''
        Override to provide an appropriate iterator for your video source
        so that it can be used in a for loop as "for im in videoX: ..."
        '''
        raise NotImplemented
    
    def play(self, window="Input", pos=None, delay=20, 
             annotate=True, imageBuffer=None, startframe=0, endframe=None,
             onNewFrame=None, **kwargs ):
        '''
        Plays the video, calling the onNewFrame function after loading each
         frame from the video. The user may interrupt video playback by
         hitting (sometimes repeatedly) the spacebar, upon which they are
         given a text menu in the console to abort program, quit playback,
         continue playback, or step to the next frame.
        @param window: The window name used to display the video. If None,
        then the video won't be shown, but onNewFrame will be called at
        each frame.
        @param pos: A tuple (x,y) where the output window should be located
        on the users screen. None indicates default openCV positioning algorithm
        will be used.
        @param delay: The delay in ms between window updates. This allows the user
        to control the playback frame rate. A value of 0 indicates that the video
        will wait for keyboard input prior to advancing to the next frame. This
        delay is used by the pauseAndPlay interface, so it will affect the rate
        at which onNewFrame is called as well.
        @param annotate: If True, the image will be annotated with the frame number
        in the upper left corner. Set false for no frame number annotation.
        @param imageBuffer: An optional faro.pyvision ImageBuffer object to contain the
        most recent frames. This is useful if a buffer is required for background
        subtraction, for example. The buffer contents is directly modified each
        time a new image is captured from the video, and a reference to the buffer
        is passed to the onNewFrame function (defined below).
        @param startframe: If > 0, then the video will cue itself by quickly fast-forwarding
        to the desired start frame before any images are shown. During the cueing process,
        any _onNewFrame function callbacks (or VideoStreamProcessor objects) will NOT be
        activated.
        @param endframe: If not None, then the playback will end after this frame has
        been processed.
        @param onNewFrame: A python callable object (function) with a
        signature of 'foo( pvImage, frameNum, key=None, buffer=None )', where key is
        the key pressed by the user (if any) during the pauseAndPlay interface, and
        buffer is a reference to the optional image buffer provided to the play method.
        @param kwargs: Optional keyword arguments that should be passed
        onto the onNewFrame function.
        @return: The final frame number of the video, or the frame number at which
        the user terminated playback using the 'q'uit option.
        '''
        fn = -1
        vid = self
        if delay==0:
            delayObj = {'wait_time':20, 'current_state':'PAUSED'}
        else:
            delayObj = {'wait_time':delay, 'current_state':'PLAYING'}
        key=''
        for fn, img in enumerate(vid):
            if fn == 0 and startframe > 0: print("Cueing video to start at %d"%startframe)
            if fn < startframe: continue
            if not endframe is None and fn > endframe: break
            
            if imageBuffer != None:
                imageBuffer.add(img)
                
            if annotate:
                pt = pv.Point(10, 10)
                img.annotateLabel(label="Frame: %d"%(fn+1), point=pt, color="white", background="black")
                
            if window != None:
                img.show(window=window,pos=pos,delay=1)
            
            if onNewFrame != None:
                onNewFrame( img, fn, key=key, imageBuffer=imageBuffer, **kwargs )
                
            key = self._pauseAndPlay(delayObj)
            if key == 'q': break #user selected quit playback
        
        #if window != None: cv.DestroyWindow(window)
        return(fn)
    
    def _pauseAndPlay(self,delayObj={'wait_time':20, 'current_state':'PLAYING'}):
        '''
        This function is intended to be used in the playback loop of a video.
        It allows the user to interrupt the playback to pause the video, to 
        step through it one frame at a time, and to register other keys/commands
        that the user may select.
        @param delayObj: The "delay object", which is just a dictionary that
        specifies the wait_time (the delay in ms between frames), and
        the current_state of either 'PLAYING' or 'PAUSED'
        '''
        state = delayObj['current_state']
        wait = delayObj['wait_time']
        #print state, wait
        
        if state=="PAUSED":
            print("PAUSED: Select <a>bort program, <q>uit playback, <c>ontinue playback, or <s>tep to next frame.")
            wait = 0
            
        c = cv.WaitKey(wait)
        c = c & 127 #bit mask to get only lower 8 bits
        
        #sometimes a person has to hold down the spacebar to get the input
        # recognized by the cv.WaitKey() within the short time limit. So
        # we need to 'soak up' these extra inputs when the user is still
        # holding the spacebar, but we've gotten into the pause state.
        while c==ord(' '):
            print("PAUSED: Select <a>bort program, <q>uit playback, <c>ontinue playback, or <s>tep to next frame.")
            c = cv.WaitKey(0)
            c = c & 127 #bit mask to get only lower 8 bits
        
        #At this point, we have a non-spacebar input, so process it.
        if c == ord('a'):   #abort
            print("User Aborted Program.")
            raise SystemExit
        elif c == ord('q'): #quit video playback
            return 'q'
        elif c == ord('c'): #continue video playback
            delayObj['current_state'] = "PLAYING"
            return 'c'
        elif c == ord('s'): #step to next frame, keep in paused state
            delayObj['current_state'] = "PAUSED"
            return 's'
        else:   #any other keyboard input is just returned
            #delayObj['current_state'] = "PAUSED"
            return chr(c)
        
# TODO: The default camera on linux appears to be zero and 1 on MacOS
#  svohara note on above...I'm not sure this is true. As of OpenCV 2.2 on my iMac,
#  the built-in webcam is index 0.

# Video capture is an alterative for windows http://videocapture.sourceforge.net/
# An option for linux http://code.google.com/p/python-video4linux2/
# On linux it may be possible to use something like v4lctl to capture in a separate process.        
class Webcam(VideoInterface):
    def __init__(self,camera_num=0,size=(640,480),flipped=False):
        '''
        Web camera interface for cameras attached to your computer via USB or built-in.
        For IP/network cameras, use the Video object instead.
        @param camera_num: The camera index. Usually 0 if you only have a single webcam
        on your computer. See the OpenCV highgui documentation for details.
        @param flipped: Set to true if camera is installed upside-down.
        '''
        import cv2
        self.cv_capture = cv2.VideoCapture( camera_num )  
        self.flipped = flipped      
        #cv.SetCaptureProperty(self.cv_capture,cv.CV_CAP_PROP_FRAME_WIDTH,1600.0)
        #cv.SetCaptureProperty(self.cv_capture,cv.CV_CAP_PROP_FRAME_HEIGHT,1200.0)
        #print cv.GetCaptureProperty(self.cv_capture,cv.CV_CAP_PROP_FRAME_WIDTH)
        # print cv.GetCaptureProperty(self.cv_capture,cv.CV_CAP_PROP_FRAME_HEIGHT)
        self.size = size
    
    def __iter__(self):
        ''' Return an iterator for this video '''
        return self
    
    def query(self):
        '''
        The returned image also include a field named orig_frame which returns 
        the original image returned before rescaling.
        
        @returns: the frame rescaled to a given size.
        '''
        # TODO: Video capture is unreliable under linux.  This may just be a timing issue when running under parallels.
        retval,frame = self.cv_capture.read()
        if self.flipped:
            import cv2
            frame = cv2.flip(frame,-1)
        im = pv.Image(self.resize(frame))
        im.orig_frame = pv.Image(frame)
        im.capture_time = time.time()
        return im
    
    def grab(self):
        return self.cv_capture.grab()
    
    def retrieve(self):
        '''
        The returned image also include a field named orig_frame which returns 
        the original image returned before rescaling.
        
        @returns: the frame rescaled to a given size.
        '''
        retval,frame = self.cv_capture.retrieve()
        im = pv.Image(self.resize(frame))
        im.orig_frame = pv.Image(frame)
        return im

      
class Video(VideoInterface):
    def __init__(self,filename,size=None):
        '''
        The basic video class that is used to play back a movie file.
        @param filename: The full path name of the video file including extension. Also, with
        current versions of OpenCV, this can be a url to a network IP camera, but you will need
        to consult your IP camera manufacturer's documentation as url formats vary.
        @note: The following is an example of using the Video class with an IP camera.
        The rtsp url is for a linksys WVC54GCA IP camera. The ip address will need to be changed
        as appropriate for your local network. Other model cameras use different urls. It can take
        a few seconds for the feed to be established.
        cam_url = "rtsp://192.168.2.55/img/video.sav"  
        vid = Video(cam_url) 
        vid.play()
        '''
        import cv2
        self.filename = filename
        self.cv_capture = cv2.VideoCapture( filename );
        self._numframes = self.cv_capture.get(cv2.CAP_PROP_FRAME_COUNT)
        self.size = size
        self.current_frame = 0

    def query(self):
        import cv2
        if self.current_frame > 0 and self.cv_capture.get(cv2.CAP_PROP_FRAME_COUNT) == 1.0:
            return None
        retval,frame = self.cv_capture.read()
        if frame is None:
            raise StopIteration("End of video sequence")
        self.current_frame += 1
        frame = frame.copy();
        return pv.Image(self.resize(frame))
    
    def setFrame(self,n):
        import cv2
        assert n >= 0 and n <= 1
        self.cv_capture.set(cv2.CAP_PROP_POS_AVI_RATIO, float(n))
        
    
    def __iter__(self):
        ''' Return an iterator for this video '''
        return Video(self.filename,self.size)
    
    def __len__(self):
        return self._numframes
        


class VideoFromFileList(VideoInterface):
    '''
    Given a sorted list of filenames (including full path), this will
    treat the list as a video sequence.
    '''
    def __init__(self, filelist, size=None):
        '''
        @param filelist: a list of full file paths to the images that comprise the video.
        They must be files capable of being loaded into a pv.Image() object, and should
        be in sorted order for playback.
        @param size: Optional tuple to indicate the desired playback window size.
        '''
        self.filelist = filelist
        self.idx = 0
        self.size = size
        
    def grab(self):
        pass
            
    def query(self):
        if self.idx >= len(self.filelist): return None
        f = self.filelist[self.idx]
        frame = pv.Image(f).asOpenCV()
        self.idx += 1
        return pv.Image(self.resize(frame))
        
    def __iter__(self):
        ''' Return an iterator for this video '''
        return VideoFromFileList(self.filelist) 
 
        
class VideoFromDirectory(VideoInterface):
    '''
    This class allows the user to treat a directory of images as a video. 
    
    This class will recursively search the directories and will load 
    and return any image with an image extension: JPG,JPEG,PNG,TIF,TIFF,GIF,BMP,PPM,PGM
    '''
    
    def __init__(self,dirname,order='ascending',limit=None,size=None,followlinks=True):
        '''
        Recursively scans a directory for images and returns all images that
        could be loaded. 

        Example:
            images = pv.VideoFromDirectory(dirname)
            for im in images:
                do something
        
        
        @param dirname: directory where the images comprising the video exist 
        @type dirname: str
        @param order: return the images in a random order using the randam.shuffle function.
        @type order: 'random' | 'ascending'
        @param limit: limit the number of images returned.
        @type limit: int
        @param size: resize all images to this size.
        @type: (int,int)
        '''
        self._dirname = dirname
        self._order = order
        self._limit = limit
        self._size = size
        self._counter = 0
        
        self._followlinks = followlinks

        self._image_paths = []
                
        self._scanImageDir()
        
        if self._order == 'ascending':
            self._image_paths.sort()
        elif self._order == 'random':
            random.shuffle(self._image_paths)
        else:
            raise ValueError("unknown ordering type: %s"%(self._order,))    
      
    def _checkExtension(self,filename):
        '''
        Check the extension on a filename to see if it is in the list.
        '''
        parts = filename.split('.')
        if len(parts) > 0:
            ext = parts[-1].upper()
        return ext in ("JPG",'JPEG',"PNG","TIF","TIFF","GIF","BMP","PPM","PGM")
    
    
    def _scanImageDir(self):
        '''
        Scan the directory and populate image_paths.
        '''
        for dirpath,_,filenames in os.walk(self._dirname,followlinks=self._followlinks):
            for filename in filenames:
                if self._checkExtension(filename):
                    path = os.path.join(dirpath,filename)
                    self._image_paths.append(path)

    
    def query(self):      
        while True:
            im_path = None
            try:
                if self._counter >= len(self._image_paths) or (self._limit != None and self._counter >= self._limit):
                    return None
                im_path = self._image_paths[self._counter]
                self._counter += 1
                im = pv.Image(im_path)
                if self._size != None:
                    im = im.resize(self.size)
                return im
            except:
                print("Warning: could not process image:",im_path)
                
    def __iter__(self):
        ''' Return an iterator for this video '''
        return VideoFromDirectory(self._dirname, self._order, self._limit, self._size) 
    
    def __len__(self):
        return len(self._image_paths)
        
class VideoFromImages(VideoInterface):
    '''
    This class allows the user to treat a directory of images as a video. It is assumed that
    the files in the directory are named as follows:
    {prefix}{num}.{ext}
    where
    prefix is any string that is constant for all the files,
    ext is the file extension/type like jpg, png, etc.
    num is a zero-padded number like 0001, 0002, ...
         
    note: the amount of padded zeros is the minimum required based on the length
    (num frames) in the video, unless a specific padding is specified. So if you only had
    120 frames, then it would be 001, 002,...120.
    
    We assume the frames are sequential with no gaps, and start at number startnum (with 
    appropriate padding).
    '''
    def __init__(self,dirname,numframes,prefix="frame",ext="jpg", pad=None, startnum=1, size=None):
        '''
        The file names are of the format {prefix}{zero-padded num}.{ext}, the amount of
        zero-padding is determined automatically based on numframes. If there is additional
        zero-padding required, put it in the prefix.
        Example: a directory with images: vid_t1_s1_f001.jpg, ..., vid_t1_s1_f999.jpg
        would have prefix="vid_t1_s1_f", startnum=1, numframes=999, ext="jpg"

        @param dirname: directory where the images comprising the video exist 
        @param numframes: the number of frames in the video...0 to numframes will be read.
        specify None to read all images in directory, in which case you must specify
        a value for the pad parameter.
        @param prefix: a string which remains as a constant prefix to all frames in video
        @param ext: the extension of the images, like jpg, png, etc. Do not include the dot.
        @param pad: the padding (like string.zfill(x)) used on the sequential numbering of
        the input files. Specify None, and the padding will be determined based on length
        of numframes. (So if numframes = 1234, then pad=4, 0001,0002,...1234) 
        @param startnum: the starting number of the first frame, defaults to 1
        @param size: the optional width,height to resize the input frames
        '''
        self.dirname = dirname
        if numframes == None:
            #user wants to read all frames, so padding must be specified
            assert(pad != None and pad>0)
        
        if pad == None:
            pad = len(str(numframes))
            
        self.pad = pad                        
        self.maxframes = numframes
        self.prefix = prefix
        self.ext = ext
        self.size = size  #the optional width,height to resize the input frames
        self.startnum = startnum
        self.current_frame = startnum  #we start at frame 1 by default
        
        #check that directory exists
        if not os.path.exists(dirname):
            print("Error. Directory: %s does not exist."%dirname)
            raise IOError
        
    def query(self):      
        numstr = str(self.current_frame).zfill(self.pad)
        filename = self.prefix + numstr + "." + self.ext
        f = os.path.join(self.dirname, filename)
        
        if (self.maxframes == None) or (self.current_frame <= self.maxframes):
            #then we query the next in the sequence until file not exists
            if os.path.exists(f):
                frame = pv.Image(f).asOpenCV()
                self.current_frame += 1
                return( pv.Image(self.resize(frame)) )
            else:
                print("Image file %s does not exist. Stopping VideoFromImages."%f)
        
        return None
        
    def __iter__(self):
        ''' Return an iterator for this video '''
        return VideoFromImages(self.dirname, self.maxframes, self.prefix, self.ext, self.pad, self.startnum, self.size) 
        
class VideoFromImageStack(VideoInterface):
    '''
    This class allows the user to treat a stack of grayscale images in a 3D numpy array as a video.
	We assume that the dimensions of the array are ordered as (frame number, width, height).
    '''
    def __init__(self, imageStack, size=None):
        '''
	    imageStack is the numpy ndarray that represents the image stack. Should be of dimensions (frames,width,height).
	    Optionally, this can be any object, such as faro.pyvision.ImageBuffer, that implements asStackBW() method that returns
	    the grayscale image stack.
        size is the optional width,height to resize the input frames.
        '''
        if str( type(imageStack) ) == "<type 'instance'>":
            self.imageStack = imageStack.asStackBW()
        else:
            self.imageStack = imageStack
        
        (f,_,_) = self.imageStack.shape
        self.numFrames = f
        self.current_frame = 0
        self.size = size

    def query(self):
        if self.current_frame < self.numFrames:
            frame = pv.Image( self.imageStack[self.current_frame,:,:])
            self.current_frame += 1
            return( pv.Image(self.resize(frame.asOpenCV()))) 
        return None     
                        
    def __iter__(self):
        ''' Return an iterator for this video '''
        return VideoFromImageStack(self.imageStack, self.size) 
                
        
