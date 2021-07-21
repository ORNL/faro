import os
import faro.pyvision as pv
import cv2
import time
import traceback
import faro
import csv
import faro.proto.proto_types as pt
import faro.proto.proto_types as pt



DETECTIONS_FILE = None
DETECTIONS_CSV = None
ATTRIBUTES_FILE = None
ATTRIBUTES_CSV = None

ENROLL_FILE = None
ENROLL_CSV = None

SEARCH_CSV = None
SEARCH_FILE = None

FACE_COUNT = 0

def collect_files(args, options, extension=None):
    if options.verbose:
        if extension is None:
            print('Scanning for videos and images...')
        else:
            print('Scanning for ', extension, ' files')
    image_list = []
    video_list = []
    csv_list = []
    for each in args:
        if os.path.isdir(each):
            for path, dirs, files in os.walk(each):
                for filename in files:
                    if pv.isImage(filename):
                        image_list.append(os.path.join(path, filename))
                    elif pv.isVideo(filename):
                        video_list.append(os.path.join(path, filename))
                    elif extension is not None and filename.endswith(extension):
                        csv_list.append(os.path.join(path, filename))

        elif os.path.isfile(each):
            if pv.isImage(each):
                image_list.append(each)
            elif pv.isVideo(each):
                video_list.append(each)
            elif extension is not None and each.endswith(extension):
                csv_list.append(each)
            else:
                raise ValueError("The file <%s> is not in a supported image or video type." % (each))
        else:
            raise ValueError("The path <%s> is not found." % (each))

    if options.verbose:
        if extension is None:
            print("    Found %d images." % (len(image_list)))
            print("    Found %d videos." % (len(video_list)))
        else:
            print("    Found %d files." % (len(csv_list)))

    if extension is None:
        return image_list, video_list
    else:
        return csv_list

def preprocessImage(im, options):
    # Reduce the size if the image is too large
    scale = 1.0
    while max(*im.shape[:2]) > options.max_size:
        if max(*im.shape[:2]) > 2 * options.max_size:
            im = cv2.pyrDown(im)
            scale *= 0.5
        else:
            h, w = im.shape[:2]
            s = options.max_size / max(w, h)
            scale *= s
            w = int(s * w)
            h = int(s * h)
            im = cv2.resize(im, (w, h))
    return im

def process_image_dir(img_dir, dir_type, fc, options):
    if options.verbose:
        print("Scanning {} directory for images and videos".format(dir_type))

    image_list, video_list = collect_files([img_dir], options)
    if options.verbose:
        print("Processing Images")

    image_count = 0
    detect_queue = []
    for filename in image_list:
        im = cv2.imread(filename)
        im = im[:, :, ::-1]
        im = preprocessImage(im, options)
        results = fc.detectExtract(im, best=options.best, threshold=options.detect_thresh,
                                   min_size=options.min_size, run_async=True, source=filename, frame=-1)

        detect_queue.append([filename, results])

        image_count += 1
        if options.max_images is not None and image_count >= options.max_images:
            break

    templates = []
    while len(detect_queue):
        fname, res = detect_queue[0]
        if res.done():
            try:
                recs = res.result().face_records
                for each_record in recs:
                    templates.append(each_record)
            except Exception as e:
                print("could not get future for file ", fname, ": ", e)
            detect_queue.pop(0)
        time.sleep(0.05)
    if len(video_list) > 0:
        print("WARNING: Video Processing Is Not Implemented. %d videos skipped." % (video_list,))

    return templates

def processAttributeFilter(face, options):
    if options.attribute_filter is None:
        return True

    # Parse the filter
    terms = options.attribute_filter.split(',')
    new_terms = []
    for each in terms:
        try:
            parts = each.split('>')
            parts = parts[0], '>', float(parts[1])
            assert len(parts) == 3
        except:
            try:
                parts = each.split('<')
                # print (parts)
                parts = parts[0], '<', float(parts[1])
                assert len(parts) == 3
            except:
                raise ValueError("Could not parse term '%s'." % each)

        new_terms.append(parts)

    satisfied = 0

    attributes = list(face.attributes)
    attributes.sort(key=lambda x: x.key)

    for attribute in attributes:
        key = attribute.key
        value = attribute.fvalue
        for tkey, tcmp, tval in new_terms:
            if tkey == key and value > tval and tcmp == '>':
                satisfied += 1
            if tkey == key and value < tval and tcmp == '<':
                satisfied += 1

    # assert satisfied <= len(terms) # Make sure we get an expected answer

    return satisfied == len(terms)

def processDetections(each):
    face_source, im, results, options = each
    if results.done():
        try: # TODO: A potential error point that may need to be addressed for corrupted images or filenames.
            recs = results.result().face_records  #possible error
        except:
            print("Error processing detections for:",face_source)
            traceback.print_exc()
            return

        i = 0

        dimg = None
        for idx, face in enumerate(recs):
            global FACE_COUNT
            FACE_COUNT += 1
            # Filter faces based on min size
            size = min(face.detection.location.width, face.detection.location.height)
            if size < options.min_size:
                continue

            # Filter faces based on attributes
            if not processAttributeFilter(face, options):
                continue

            # Process Detections
            if options.detections_csv is not None:
                global DETECTIONS_CSV
                global DETECTIONS_FILE
                import csv
                if DETECTIONS_CSV == None:
                    DETECTIONS_FILE = open(options.detections_csv, 'w')
                    DETECTIONS_CSV = csv.writer(DETECTIONS_FILE)
                    csv_header = ['source', 'frame', 'detect_id', 'type', 'score', 'x', 'y', 'w', 'h']
                    if len(face.landmarks) > 0:
                        for each_lpt in face.landmarks:
                            pt_id_label = each_lpt.landmark_id
                            xpt_label = pt_id_label + '_x'
                            ypt_label = pt_id_label + '_y'
                            csv_header.append(pt_id_label)
                            csv_header.append(xpt_label)
                            csv_header.append(ypt_label)

                    DETECTIONS_CSV.writerow(csv_header)

                csv_eachline = [face.source,
                                face.frame,
                                i,
                                face.detection.detection_class,
                                face.detection.score,
                                face.detection.location.x,
                                face.detection.location.y,
                                face.detection.location.width,
                                face.detection.location.height]

                if len(face.landmarks) > 0:
                    for each_lpt in face.landmarks:
                        pt_id_label = each_lpt.landmark_id
                        xpt_label = each_lpt.location.x
                        ypt_label = each_lpt.location.y
                        csv_eachline.append(pt_id_label)
                        csv_eachline.append(xpt_label)
                        csv_eachline.append(ypt_label)
                DETECTIONS_CSV.writerow(csv_eachline)

                DETECTIONS_FILE.flush()

            # Process Detections
            if options.attributes_csv is not None:
                global ATTRIBUTES_CSV
                global ATTRIBUTES_FILE
                import csv

                if ATTRIBUTES_CSV == None:
                    ATTRIBUTES_FILE = open(options.attributes_csv, 'w')
                    ATTRIBUTES_CSV = csv.writer(ATTRIBUTES_FILE)
                    csv_header = ['source', 'frame', 'detect_id', 'type', 'score', 'x', 'y',
                                  'w', 'h', 'attribute', 'value']
                    if len(face.landmarks) > 0:
                        for each_lpt in face.landmarks:
                            pt_id_label = each_lpt.landmark_id
                            xpt_label = pt_id_label + '_x'
                            ypt_label = pt_id_label + '_y'
                            csv_header.append(pt_id_label)
                            csv_header.append(xpt_label)
                            csv_header.append(ypt_label)
                    ATTRIBUTES_CSV.writerow(csv_header)

                attributes = list(face.attributes)
                attributes.sort(key=lambda x: x.key)
                for attribute in attributes:
                    key = attribute.key
                    value = attribute.text
                    csv_eachline = [face.source,
                                    face.frame,
                                    i,
                                    face.detection.detection_class,
                                    face.detection.score,
                                    face.detection.location.x,
                                    face.detection.location.y,
                                    face.detection.location.width,
                                    face.detection.location.height,
                                    key,
                                    value]
                    if len(face.landmarks) > 0:
                        for each_lpt in face.landmarks:
                            pt_id_label = each_lpt.landmark_id
                            xpt_label = each_lpt.location.x
                            ypt_label = each_lpt.location.y
                            csv_eachline.append(pt_id_label)
                            csv_eachline.append(xpt_label)
                            csv_eachline.append(ypt_label)
                    ATTRIBUTES_CSV.writerow(csv_eachline)
                ATTRIBUTES_FILE.flush()

            # Save Images with Detections

            if options.detect_log:
                if not os.path.exists(options.detect_log):
                    os.makedirs(options.detect_log, exist_ok=True)
                rect = pt.rect_proto2pv(face.detection.location)
                if dimg is None:
                    dimg = pv.Image(im[:, :, ::-1])
                dimg.annotateThickRect(rect)
                dimg.annotateLabel(pv.Point(rect.x + 5, rect.y + 5), face.detection.detection_class)
                dimg.annotateLabel(pv.Point(rect.x + 5, rect.y + 20),
                                   "Score: %0.4f" % (face.detection.score,), color='yellow')
                if len(face.landmarks) > 0:
                    for each_lmark in face.landmarks:
                        dimg.annotateCircle(pv.Point(each_lmark.location.x, each_lmark.location.y),
                                            radius=3, color='green', fill='green')

            if options.face_log:
                if not os.path.exists(options.face_log):
                    os.makedirs(options.face_log, exist_ok=True)
                # print(face.detection.location)

                rect = pt.rect_proto2pv(face.detection.location)
                rect = rect.rescale(1.5)
                affine = pv.AffineFromRect(rect, (128, 128))
                try:
                    pvim = pv.Image(im[:, :, ::-1])
                    view = affine(pvim)
                    # print('Face',rect)
                    # print(view)
                    base_name, ext = os.path.splitext(os.path.basename(face.source))
                    out_path = os.path.join(options.face_log,
                                            os.path.basename(base_name) + '_face_%03d' % (
                                            face.detection.detection_id,) + ext)

                    view.save(out_path)
                    print('Saving face:', out_path)
                except:
                    print("WARNING: Image not processed correctly:", face_source)
                    traceback.print_exc()

                out_path = os.path.join(options.face_log, os.path.basename(base_name) + '_orig' + ext)

                if not os.path.lexists(out_path):
                    os.symlink(os.path.abspath(face.source), out_path)
            i += 1
        if options.detect_log and dimg is not None:
            dimg.asAnnotated().save(os.path.join(options.detect_log, os.path.basename(base_name) + ext))
        return False
    return True

def processEnrollments(each):
    im, results, options = each

    if results.done():
        recs = results.result().face_records
        i = 0
        for face in recs:
            # Filter faces based on min size
            size = min(face.detection.location.width, face.detection.location.height)
            if size < options.min_size:
                continue

            # Filter faces based on attributes
            if not processAttributeFilter(face, options):
                continue

            # Process Detections
            if options.enroll_csv is not None:
                global ENROLL_CSV
                global ENROLL_FILE
                import csv
                if ENROLL_CSV == None:
                    ENROLL_FILE = open(options.enroll_csv, 'w')
                    ENROLL_CSV = csv.writer(ENROLL_FILE)
                    ENROLL_CSV.writerow(['gallery_key', 'source', 'frame', 'detect_id',
                                         'type', 'score', 'x', 'y', 'w', 'h'])

                ENROLL_CSV.writerow([face.gallery_key, face.source,
                                     face.frame,
                                     i,
                                     face.detection.detection_class,
                                     face.detection.score,
                                     face.detection.location.x,
                                     face.detection.location.y,
                                     face.detection.location.width,
                                     face.detection.location.height
                                     ]),
                ENROLL_FILE.flush()

            i += 1
        return False
    return True


def processSearchResults(each):
    face_source, im, results, options = each
    im = pv.Image(im[:, :, ::-1])  # RGB to BGR

    if results.done():
        recs = results.result().face_records

        i = 0

        if options.search_log is not None:
            try:
                os.makedirs(options.search_log)
            except:
                pass

        if options.search_index is not None:
            try:
                os.makedirs(options.search_index)
            except:
                pass

        if options.search_log is not None:
            im.annotateLabel(pv.Point(10, 10), "Detections: %d" % (len(recs),), font=16, color='yellow')

        for face in recs:
            # Filter faces based on min size
            size = min(face.detection.location.width, face.detection.location.height)
            if size < options.min_size:
                continue

            # Filter faces based on attributes
            if not processAttributeFilter(face, options):
                continue

            face_source = face.source
            face_detect_id = face.detection.detection_id
            face_detect_rect = pt.rect_proto2pv(face.detection.location)

            # Process Detections
            if options.search_csv is not None:
                global SEARCH_CSV
                global SEARCH_FILE
                import csv
                if SEARCH_CSV == None:
                    # if options.verbose:
                    SEARCH_FILE = open(options.search_csv, 'w')
                    SEARCH_CSV = csv.writer(SEARCH_FILE)
                    SEARCH_CSV.writerow(['face_source', 'face_detect_id',
                                         'gal_sub_id', 'gal_name', 'gal_source',
                                         'gal_score', 'gal_key', 'x', 'y', 'w', 'h'])

            if options.search_log is not None:

                if len(face.search_results.face_records) > 0:
                    gal = face.search_results.face_records[0]
                    gal_name = gal.name
                    gal_sub_id = gal.subject_id
                    gal_source = gal.source
                    gal_score = gal.score
                    gal_key = gal.gallery_key

                    # face.search_results.face_records
                    # string subject_id = 1;
                    # string name = 5;
                    # string source = 4;
                    # int64 frame = 14;
                    # string notes = 6;
                    # string gallery_key = 15;

                    SEARCH_CSV.writerow([face_source, face_detect_id,
                                         gal_sub_id, gal_name, gal_source, gal_score, gal_key, face_detect_rect.x,
                                         face_detect_rect.y, face_detect_rect.w, face_detect_rect.h
                                         ]),

                    im.annotateThickRect(face_detect_rect, width=3, color='yellow')
                    im.annotateLabel(pv.Point(face_detect_rect.x, face_detect_rect.y + face_detect_rect.h + 5),
                                     "%s - %s" % (gal_sub_id, gal_name), font=16, color='yellow')
                else:
                    im.annotateThickRect(face_detect_rect, color='white', width=2)

                SEARCH_FILE.flush()

            i += 1

            if options.search_index is not None:

                if len(face.search_results.face_records) > 0:
                    gal = face.search_results.face_records[0]
                    gal_name = gal.name
                    gal_sub_id = gal.subject_id
                    gal_source = gal.source
                    gal_score = gal.score
                    gal_key = gal.gallery_key

                    dir_name = os.path.join(options.search_index, gal_sub_id + '-' + "_".join(gal_name.split()))
                    link_name = os.path.join(dir_name, os.path.basename(face_source))

                    try:
                        os.makedirs(dir_name)
                    except:
                        pass

                    try:
                        os.remove(link_name)
                    except:
                        pass

                    os.symlink(os.path.abspath(face_source), link_name)

        if options.search_log is not None:
            try:  # TODO: A potential error point that may need to be addressed for corrupted images or filenames.
                out_name = os.path.join(options.search_log, os.path.basename(face_source))
                im.asAnnotated().save(out_name)
            except:
                print("Error processing:", face_source)
                traceback.print_exc()
                return False

        return False
    return True

VIDEO_HEADER_FILE = None

def process_video_detections(each):
    global VIDEO_HEADER_FILE
    im, results, options, file_identifier = each
    if results.done():
        recs = results.result().face_records
        i = 0
        detect_log_dir = None
        frame_id = None
        dimg = None
        for idx, face in enumerate(recs):
            base_name, ext = os.path.splitext(os.path.basename(face.source))
            # Filter faces based on min size
            size = min(face.detection.location.width, face.detection.location.height)
            if size < options.min_size:
                continue

            if (options.detections_csv is not None):
                if VIDEO_HEADER_FILE:
                    csv_header = ['source', 'frame', 'detect_id', 'type', 'score', 'x', 'y', 'w', 'h']
                    if len(face.landmarks) > 0:
                        for each_lpt in face.landmarks:
                            pt_id_label = each_lpt.landmark_id
                            xpt_label = pt_id_label + '_x'
                            ypt_label = pt_id_label + '_y'
                            csv_header.append(pt_id_label)
                            csv_header.append(xpt_label)
                            csv_header.append(ypt_label)
                    file_identifier.writerow(csv_header)
                    VIDEO_HEADER_FILE = False

                csv_eachline = [face.source,
                                face.frame,
                                i,
                                face.detection.detection_class,
                                face.detection.score,
                                face.detection.location.x,
                                face.detection.location.y,
                                face.detection.location.width,
                                face.detection.location.height]

                if len(face.landmarks) > 0:
                    for each_lpt in face.landmarks:
                        pt_id_label = each_lpt.landmark_id
                        xpt_label = each_lpt.location.x
                        ypt_label = each_lpt.location.y
                        csv_eachline.append(pt_id_label)
                        csv_eachline.append(xpt_label)
                        csv_eachline.append(ypt_label)

                file_identifier.writerow(csv_eachline)

            if options.detect_log:
                detect_log_dir = os.path.join(os.path.join(options.detect_log, base_name))
                frame_id = face.frame
                if not os.path.exists(detect_log_dir):
                    os.makedirs(detect_log_dir, exist_ok=True)

                rect = pt.rect_proto2pv(face.detection.location)
                if dimg is None:
                    dimg = pv.Image(im[:, :, ::-1])
                dimg.annotateThickRect(rect)
                dimg.annotateLabel(pv.Point(rect.x + 5, rect.y + 5), face.detection.detection_class)
                dimg.annotateLabel(pv.Point(rect.x + 5, rect.y + 20),
                                   "Score: %0.4f" % (face.detection.score,), color='yellow')
                if len(face.landmarks) > 0:
                    for each_lmark in face.landmarks:
                        dimg.annotateCircle(pv.Point(each_lmark.location.x, each_lmark.location.y),
                                            radius=3, color='green', fill='green')

            if options.face_log:
                face_log_dir = os.path.join(options.face_log, base_name)
                if not os.path.exists(face_log_dir):
                    os.makedirs(face_log_dir, exist_ok=True)

                rect = pt.rect_proto2pv(face.detection.location)
                rect = rect.rescale(1.5)
                affine = pv.AffineFromRect(rect, (128, 128))
                try:
                    pvim = pv.Image(im[:, :, ::-1])
                    view = affine(pvim)
                    out_path = os.path.join(face_log_dir, os.path.basename(base_name) +
                                            '_Frame_%09d' % face.frame +
                                            '_face_%03d' % (face.detection.detection_id,) + '.jpg')
                    if len(face.landmarks) > 0:
                        for each_lmark in face.landmarks:
                            transformed_lmarks = affine(pv.Point(each_lmark.location.x, each_lmark.location.y))
                            view.annotateCircle(transformed_lmarks, radius=3, color='green', fill='green')
                    view.asAnnotated().save(out_path)
                    # print('Saving face:', out_path)
                except:
                    print("WARNING: Image not processed correctly:", face.source)
            i += 1

        if options.detect_log and detect_log_dir is not None:
            dimg.asAnnotated().save(os.path.join(detect_log_dir,
                                                 os.path.basename(base_name) + '_Frame_%09d' % frame_id + '.jpg'))
        return False
    return True


def process_single_videos(each_video, face_client, options):
    global VIDEO_HEADER_FILE
    VIDEO_HEADER_FILE = True
    detect_queue = []
    # Read Video
    video = pv.Video(each_video)
    video_name, ext = os.path.splitext(os.path.basename(each_video))

    if options.detections_csv:
        _, tmp_ext = os.path.splitext(os.path.basename(options.detections_csv))
        if tmp_ext:
            save_video_csvfile_dir = os.path.dirname(options.detections_csv)
            if len(save_video_csvfile_dir) == 0:
                save_video_csvfile_dir = os.getcwd()
        else:
            save_video_csvfile_dir = options.detections_csv
        if not os.path.isdir(save_video_csvfile_dir):
            os.makedirs(save_video_csvfile_dir)
        fid = open(os.path.join(save_video_csvfile_dir, video_name + '.csv'), 'w')
        video_detections_csv = csv.writer(fid)
    else:
        video_detections_csv = None

    start_time = time.time()
    for frame_id, each_frame in enumerate(video):

        each_frame = each_frame.asOpenCV2()[:, :, ::-1]  # convert to opencv and then bgrtorgb
        if options.max_size is not None:
            each_frame = faro.proc.preprocessImage(each_frame, options)
        results = face_client.detect(each_frame, best=options.best,
                                     threshold=options.detect_thresh,
                                     min_size=options.min_size,
                                     run_async=True,
                                     source=each_video,
                                     frame=frame_id + 1)
        detect_queue.append([each_frame, results, options, video_detections_csv])
        detect_queue = list(filter(process_video_detections, detect_queue))

    while len(detect_queue):
        detect_queue = list(filter(process_video_detections, detect_queue))
        time.sleep(0.05)

    end_time = time.time()
    print("Processed %d frames in %0.3f seconds: %f images/second" % (frame_id + 1, end_time - start_time,
                                                                      (frame_id + 1) / (end_time - start_time)))

    if options.detections_csv:
        fid.close()


def process_videos(vlist, face_client, options):
    if options.verbose:
        print("Processing videos")

    for each_video in vlist:
        print('Processing Video: ', each_video)
        process_single_videos(each_video, face_client, options)


def process_images(ilist, face_client, options):
    if options.verbose:
        print("Processing images.")

    image_count = 0
    detect_queue = []

    start = time.time()
    for filename in ilist:
        print("Processing:", filename)
        im = cv2.imread(filename)

        if im is None:
            continue

        im = im[:, :, ::-1]  # BGR to RGB

        im = faro.proc.preprocessImage(im, options)

        results = face_client.detect(im, best=options.best, threshold=options.detect_thresh, min_size=options.min_size,
                                     run_async=True, source=filename, frame=-1)

        detect_queue.append([filename, im, results, options])
        detect_queue = list(filter(processDetections, detect_queue))
        image_count += 1
        if options.max_images is not None and image_count >= options.max_images:
            break

    while len(detect_queue):
        detect_queue = list(filter(processDetections, detect_queue))
        time.sleep(0.05)

    end = time.time()
    print("Processed %d images in %0.3f seconds: %f images/second" % (
        image_count, end - start, image_count / (end - start)))
    print(
        "Processed %d faces in %0.3f seconds: %f faces/second" % (FACE_COUNT, end - start, FACE_COUNT / (end - start)))