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

import faro
import faro.proc
import cv2
import time
from faro.proto.face_service_pb2 import FaceRecordList
import csv

FACE_COUNT = 0

def detectExtract(options,args):
    face_client = faro.connectToFaroClient(options)

    if options.verbose:
        print("Scanning directories for images and videos.")

    image_list, video_list = faro.proc.collect_files(args[1:], options)

    if options.verbose:
        print("Processing images.")

    image_count = 0
    detect_queue = []
    start = time.time()
    for filename in image_list:
        print("Processing:", filename)
        im = cv2.imread(filename)
        im = im[:, :, ::-1]  # BGR to RGB

        im = faro.proc.preprocessImage(im, options)

        results = face_client.detectExtract(im, best=options.best, threshold=options.detect_thresh,
                                            min_size=options.min_size, run_async=True, source=filename, frame=-1)

        detect_queue.append([filename, im, results, options])
        detect_queue = list(filter(faro.proc.processDetections, detect_queue))

        image_count += 1
        if options.max_images is not None and image_count >= options.max_images:
            break

    end = time.time()

    while len(detect_queue):
        detect_queue = list(filter(faro.proc.processDetections, detect_queue))
        time.sleep(0.05)

    if len(video_list) > 0:
        print("WARNING: Video Processing Is Not Implemented. %d videos skipped." % (video_list,))

    print("Processed %d images in %0.3f seconds: %f images/second" % (
    image_count, end - start, image_count / (end - start)))
    print(
        "Processed %d faces in %0.3f seconds: %f faces/second" % (FACE_COUNT, end - start, FACE_COUNT / (end - start)))


def extractOnly(options,args):
    face_client = faro.command_line.connectToFaroClient(options)

    if options.verbose:
        print("Scanning directories for images and videos.")

    f = open(args[1], 'r')
    csv_f = csv.DictReader(f)

    process_queue = []
    current_file = None
    for row in csv_f:
        if current_file == None or current_file != row['source']:
            current_file = row['source']
            detections = FaceRecordList()
            process_queue.append([current_file, detections])

        face = detections.face_records.add()
        face.source = row['source']
        face.frame = int(row['frame'])
        face.detection.detection_id = int(row['detect_id'])
        face.detection.score = float(row['score'])
        face.detection.detection_class = row['type']
        face.detection.location.x = float(row['x'])
        face.detection.location.y = float(row['y'])
        face.detection.location.width = float(row['w'])
        face.detection.location.height = float(row['h'])

    # image_list, video_list = faro.proc.collect_files(args[1:],options)

    if options.verbose:
        print("Processing images.")

    image_count = 0
    detect_queue = []
    start = time.time()
    for filename, detections in process_queue:
        # print("Processing:",filename)
        im = cv2.imread(filename)
        im = im[:, :, ::-1]  # BGR to RGB

        im = faro.proc.preprocessImage(im, options)

        results = face_client.extract(im, detections, run_async=True)

        detect_queue.append([filename, im, results, options])
        detect_queue = list(filter(faro.proc.processDetections, detect_queue))

        image_count += 1
        if options.max_images is not None and image_count >= options.max_images:
            break
    end = time.time()

    while len(detect_queue):
        detect_queue = list(filter(faro.proc.processDetections, detect_queue))
        time.sleep(0.05)

    # if len(video_list) > 0:
    #    print("WARNING: Video Processing Is Not Implemented. %d videos skipped."%(video_list,))

    print("Processed %d images in %0.3f seconds: %f images/second" % (
          image_count, end - start, image_count / (end - start)))
    print(
        "Processed %d faces in %0.3f seconds: %f faces/second" % (FACE_COUNT, end - start, FACE_COUNT / (end - start)))
