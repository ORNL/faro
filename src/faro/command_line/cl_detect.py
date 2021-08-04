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

import faro
import faro.proc
import faro.pyvision as pv
import time
import faro.proto.proto_types as pt

def detect(options,args):
    face_client = faro.command_line.connectToFaroClient(options)

    if options.stream is not None:
        print("Starting Stream")
        start_stream(options,face_client)
    else:
        if options.verbose:
            print("Scanning directories for images and videos.")

        image_list, video_list = faro.proc.collect_files(args[1:], options)

        if len(image_list) != 0:
            faro.proc.process_images(image_list, face_client, options)

        if len(video_list) != 0:
            faro.proc.process_videos(video_list, face_client, options)

def start_stream(options,fc):
    import cv2
    print('starting cap')
    hasgstreamer = faro.util.getcv2info('gstreamer')
    if options.verbose:
        print('has gstreamer: ', hasgstreamer)
    # if "!" in options.stream and options.stream.endswith('appsink'):
    #     if not hasgstreamer:
    #         print('gstreamer is not integrated with opencv.  Please rebuild opencv with gstreamer')

    # cam = cv2.VideoCapture('udpsrc port=9078 caps = "application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, payload=(int)96" ! rtph264depay ! decodebin ! videoconvert ! appsink',cv2.CAP_GSTREAMER)
    faro.proc.process_stream(fc,options)
    sys.exit(1)
    input_val = options.stream
    if input_val.isnumeric():
        input_val = int(input_val)
    cam = cv2.VideoCapture(input_val)
    if cam.isOpened():
        if options.verbose:
            print('Stream opened')
    else:
        if options.verbose:
            print('Stream could not be opened')
        exit(1)
    while True:
        ret_val, img = cam.read()
        if img is not None:
            im = faro.proc.preprocessImage(img, options)

            res = fc.detect(im, best=options.best, threshold=options.detect_thresh,
                                        min_size=options.min_size, run_async=False, frame=-1)
            # try:
            recs = res.face_records
            pvim = pv.Image(im)
            for r in recs:
                rect = pt.rect_proto2pv(r.detection.location)

                pvim.annotateThickRect(rect)
            if pvim.show(window="camera",delay=30) == 27:
                break
            # cv2.imshow("camera", cvim)

            # except Exception as e:
            #     print("could not get future for frame byeeeeeeee",e)
            #     time.sleep(0.05)

            # if cv2.waitKey(1) == 27:
            #     break  # esc to quit
