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

def enroll(options,args):
    face_client = faro.command_line.connectToFaroClient(options)

    if options.verbose:
        print("Scanning directories for images and videos.")

    image_list, video_list = faro.proc.collect_files(args[1:], options)

    if options.verbose:
        print("Processing images.")

    image_count = 0
    detect_queue = []
    enroll_queue = []

    for filename in image_list:
        print("Processing:", filename)
        im = cv2.imread(filename)
        im = im[:, :, ::-1]  # BGR to RGB

        im = faro.proc.preprocessImage(im, options)

        results = face_client.detectExtractEnroll(im, enroll_gallery=options.enroll_gallery, best=options.best,
                                                  threshold=options.detect_thresh, min_size=options.min_size,
                                                  run_async=True, source=filename, frame=-1,
                                                  subject_name=options.subject_name, subject_id=options.subject_id)

        detect_queue.append([filename, im, results, options])
        enroll_queue.append([im, results, options])

        # Process results that are completed.
        detect_queue = list(filter(faro.proc.processDetections, detect_queue))
        enroll_queue = list(filter(faro.proc.processEnrollments, enroll_queue))

        image_count += 1
        if options.max_images is not None and image_count >= options.max_images:
            break

    import time

    # Finish processing.
    while len(detect_queue):
        detect_queue = list(filter(faro.proc.processDetections, detect_queue))
        time.sleep(0.05)

    while len(enroll_queue):
        enroll_queue = list(filter(faro.proc.processEnrollments, enroll_queue))
        time.sleep(0.05)

    if len(video_list) > 0:
        print("WARNING: Video Processing Is Not Implemented. %d videos skipped." % (video_list,))


def enroll_csv(options,args):
    import time

    start = time.time()

    face_client = faro.command_line.connectToFaroClient(options)

    # print( args )

    csv_filename = args[1]
    if options.verbose:
        print("Processing files in ", csv_filename)

    import csv

    csv_file = csv.DictReader(open(csv_filename, 'r'))

    # image_list, video_list = faro.proc.collect_files(args[1:], options)

    # if options.verbose:
    #    print("Processing images.")

    image_count = 0
    detect_queue = []
    enroll_queue = []

    for row in csv_file:
        print("Processing:", row)

        subject_id = row['subject_id']
        name = row['name']
        filename = row['filename']

        im = cv2.imread(filename)
        im = im[:, :, ::-1]  # BGR to RGB

        im = faro.proc.preprocessImage(im, options)

        results = face_client.detectExtractEnroll(im, enroll_gallery=options.enroll_gallery, best=options.best,
                                                  threshold=options.detect_thresh, min_size=options.min_size,
                                                  run_async=True, source=filename, frame=-1,
                                                  subject_name=name, subject_id=subject_id)

        detect_queue.append([filename, im, results, options])
        enroll_queue.append([im, results, options])

        # Process results that are completed.
        detect_queue = list(filter(faro.proc.processDetections, detect_queue))
        enroll_queue = list(filter(faro.proc.processEnrollments, enroll_queue))

        image_count += 1
        if options.max_images is not None and image_count >= options.max_images:
            break

        # Finish processing.
        while len(detect_queue):
            detect_queue = list(filter(faro.proc.processDetections, detect_queue))
            time.sleep(0.05)

        while len(enroll_queue):
            enroll_queue = list(filter(faro.proc.processEnrollments, enroll_queue))
            time.sleep(0.05)

        # if len(video_list) > 0:
        #    print("WARNING: Video Processing Is Not Implemented. %d videos skipped." % (video_list,))

        finish = time.time()
        print("Processed %d files in %0.2fsec.  %0.2f images/sec" % (
        image_count, finish - start, image_count / (finish - start)))