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
import faro.proc
import importlib
import sys
from sortedcollections import SortedDict
import csv
from faro.command_line.cl_common import connectToFaroClient
tabulator = faro.util.safe_tabulator()
tqdm = faro.util.safe_tqdm()


def test(options,args):
    """
    Run a recognition test and compute a distance matrix and optionally other results.
    """
    face_client = connectToFaroClient(options)
    g_templates = None
    p_templates = None
    smat = None
    if len(args[1:]) == 1:
        gallery_dir = args[1]
        g_templates = faro.proc.process_image_dir(gallery_dir, "gallery", face_client, options)
        p_templates = g_templates.copy()
        smat = face_client.score(g_templates, p_templates)
    elif len(args[1:]) == 2:
        gallery_dir = args[1]
        g_templates = faro.proc.process_image_dir(gallery_dir, "gallery", face_client, options)
        probe_dir = args[2]
        p_templates = faro.proc.process_image_dir(probe_dir, "probe", face_client, options)
        smat = face_client.score(g_templates, p_templates)
    else:
        print("Something is wrong")

    if options.distance_matrix is not None:
        scores_csv_file = open(options.distance_matrix, 'w')
        scores_csv = csv.writer(scores_csv_file)
        scores_csv.writerow(['face_id1', 'filename1', 'face_id2', 'filename2', 'score'])
        scores_csv_file.flush()

        r, c = smat.shape
        for i in range(0, r):
            for j in range(0, c):
                filename1 = g_templates[i].source
                filename2 = p_templates[j].source
                if scores_csv is not None:
                    scores_csv.writerow([i, filename1, j, filename2, smat[i, j]])
                    scores_csv_file.flush()
        scores_csv_file.close()