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

def search(options,args):
    face_client = faro.command_line.connectToFaroClient(options)

    if options.verbose:
        print("Scanning directories for images and videos.")

    image_list, video_list = faro.proc.collect_files(args[1:], options)

    if options.verbose:
        print("Processing images.")

    image_count = 0
    detect_queue = []
    search_queue = []

    for filename in image_list:
        print("Processing:", filename)
        im = cv2.imread(filename)
        if im is None: # TODO: A potential error point that may need to be addressed for corrupted images or filenames.
            print("Warning: could not process ",filename)
            continue
        im = im[:, :, ::-1]  # BGR to RGB

        im = faro.proc.preprocessImage(im, options)

        results = face_client.detectExtractSearch(im, search_gallery=options.search_gallery, best=options.best,
                                                  threshold=options.detect_thresh, min_size=options.min_size,
                                                  run_async=True, source=filename, frame=-1,
                                                  search_threshold=options.search_threshold, max_results=options.max_results)

        detect_queue.append([filename,im, results, options])
        search_queue.append([filename,im, results, options])

        # Process results that are completed.
        detect_queue = list(filter(faro.proc.processDetections, detect_queue))
        search_queue = list(filter(faro.proc.processSearchResults, search_queue))

        image_count += 1
        if options.max_images is not None and image_count >= options.max_images:
            break

    import time

    # Finish processing.
    while len(detect_queue):
        detect_queue = list(filter(faro.proc.processDetections, detect_queue))
        time.sleep(0.05)

    while len(search_queue):
        search_queue = list(filter(faro.proc.processSearchResults, search_queue))
        time.sleep(0.05)

    if len(video_list) > 0:
        print("WARNING: Video Processing Is Not Implemented. %d videos skipped." % (video_list,))