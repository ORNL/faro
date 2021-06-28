import os
import faro
import csv
from collections import defaultdict
import numpy as np
tqdm = faro.util.safe_tqdm()

def fuse(options,args):
    """
    Run a recognition test and compute a distance matrix and optionally other results.
    """


    method = options.method
    print("got args:", list(args))
    score_file_dir = args[1]
    csv_files = faro.proc.collect_files(args[1:], options, extension='.csv')
    line_len = -1
    filenames = [os.path.basename(f) for f in csv_files]

    #     sorting the file names will ensure score matrices are built in the correct order
    filenames.sort()

    score_dict = defaultdict(dict)
    if options.verbose:
        print('collecting scores')
    for f in csv_files:
        fname = os.path.basename(f)
        with open(f, 'r') as fp:
            lines = fp.readlines()
            if line_len < 0: line_len = len(lines)
            if not len(lines) == line_len:
                assert False, "Error: file " + f + " is of length " + str(
                    len(lines)) + " while the previous file was of length " + str(line_len)
            else:
                line_len = len(lines)
            for l in tqdm(lines[1:]):
                parts = l.split(',')
                if len(parts) >= 5:
                    p1 = parts[1].strip().rstrip()
                    p2 = parts[3].strip().rstrip()
                    score = parts[4]
                    pair = (p1, p2)
                    score_dict[pair][fname] = float(score)
    fusion_matrix = []
    allpairs = list(score_dict.keys())
    allpairs.sort()
    if options.verbose:
        print('stacking matrices...')
    for pair in tqdm(allpairs):
        alg_scores = score_dict[pair]
        scores = []
        # prevsize =
        for alg in filenames:

            if alg in alg_scores:
                scores.append(alg_scores[alg])
            else:
                print('match ', pair, ' does not have a score for algorithm ', alg)
                scores.append(.5)
        if len(fusion_matrix) > 1:  # check to make sure each match pair has the same amount of scores associated with it
            if len(scores) == len(fusion_matrix[-1]):
                pass
            else:
                print('algorithm length mismatch for ', list(pair), ' only has ', len(scores),
                      'score results, and should have ', len(fusion_matrix[-1]))
                assert False, 'algorithm length mismatch for ' + str(list(pair)) + ' only has ' + len(
                    scores) + ' score results, and should have ' + len(fusion_matrix[-1])
        fusion_matrix.append(scores)
    # the fusion matrix in the format of one algorithm per column, with a shape NxM, where N is the number of match pairs and M is the number of algorithms
    fusion_matrix = np.vstack(fusion_matrix)
    if options.verbose:
        print('performing fusion...')
    if method == "minmax":
        # first, normalize all values to between 0 and 1 on a per-algorithm basis
        minvals = fusion_matrix.min(axis=0)
        maxvals = fusion_matrix.max(axis=0)
        fusion_matrix = (fusion_matrix - minvals) / (maxvals - minvals)

        # next, average the results across the algorithm axis
        fusion_matrix = fusion_matrix.mean(axis=1).flatten()
    else:
        print('fusion method ', method, ' not implemented')
    csv_output = []
    scores_csv_file = open(options.distance_matrix, 'w')
    scores_csv = csv.writer(scores_csv_file)
    for pair, score in zip(allpairs, fusion_matrix):
        l = ['0', str(pair[0]), '2', str(pair[1]), str(score)]
        if scores_csv is not None:
            scores_csv.writerow(l)
            scores_csv_file.flush()
    scores_csv_file.close()
    if options.verbose:
        print('done!')
