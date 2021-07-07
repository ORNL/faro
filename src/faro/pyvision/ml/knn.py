# faro.pyvision License (http://pyvision.sourceforge.net)
#
# Copyright (c) 2006-2008 David S. Bolme
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

import numpy as np
import unittest
import copy
import faro.pyvision as pv
import time

class PNorm:
    def __init__(self,p):
        self.p = float(p)
    
    def __call__(self, points, data):
        _,c = data.shape
        
        dist_mat = []
        if self.p == np.inf:
            for pt in points:
                pt = pt.reshape(1,c)
                row =  np.amax(np.abs(data - pt),axis=-1)
                dist_mat.append(row)
        else:
            for pt in points:
                pt = pt.reshape(1,c)
                row = np.sum(np.abs(data - pt)**self.p,axis=1)**(1.0/self.p)
                dist_mat.append(row)
        
        return np.array(dist_mat)
    
class RobustPNorm:
    def __init__(self,p,scale=1.0):
        '''
        Distances along axes are transformed by a sigmoid such that they 
        are locally linear but not allowed to grow too large in the case 
        of a large distance.
        
        @param scale: adjust the size of the robust bins
        '''
        
        self.p = float(p)
        self.scale = scale
    
    def __call__(self, points, data):
        _,c = data.shape
        
        dist_mat = []
        if self.p == np.inf:
            for pt in points:
                pt = pt.reshape(1,c)
                raw_dist = self.scale*(data - pt)
                robust_dist = raw_dist/np.sqrt(1+raw_dist**2) # sigmoid - locally linear
                row =  np.amax(np.abs(robust_dist),axis=-1)
                dist_mat.append(row)
        else:
            for pt in points:
                pt = pt.reshape(1,c)
                raw_dist = self.scale*(data - pt)
                robust_dist = raw_dist/np.sqrt(1+raw_dist**2) # sigmoid - locally linear
                row = np.sum(np.abs(robust_dist)**self.p,axis=1)**(1.0/self.p)
                dist_mat.append(row)
        
        return np.array(dist_mat)
    
def chisquared(points, data):
    '''
    Compute the chi squared statistic between histograms
    '''
    # all values in the histogram must be positive
    assert points.min() >= 0.0
    assert data.min() >= 0.0
    
    _,c = data.shape
    
    
    dist_mat = []
    for pt in points:
        pt = pt.reshape(1,c)
        tmp1 = (data - pt)**2
        tmp2 = data + pt
        mask = tmp2 < 0.000001
        tmp3 = (tmp1 * ~mask) /(tmp2 + 1.0*mask) # prevent divide by zero
        
        row = np.sum(tmp3,axis=1)
        dist_mat.append(row)
    
    return np.array(dist_mat)

def bhattacharyya(points,data):
    '''
    Compute bhattacharyya distance for histograms.
    '''
    raise NotImplementedError()
    # all values in the historgams must be positive
    assert points.min() >= 0.0
    assert data.min() >= 0.0
        
        
def correlation(points,data,reg=0.00001):
    '''
    Compute the correlation between points and data where 
    points are stored as rows.
    '''
    pr,_ = points.shape
    dr,_ = data.shape
    
    points = points - points.mean(axis=1).reshape(pr,1)
    data = data - data.mean(axis=1).reshape(dr,1)
    
    ps = 1.0/np.sqrt((points*points).sum(axis=1)+reg).reshape(pr,1)
    ds = 1.0/np.sqrt((data*data).sum(axis=1)+reg).reshape(dr,1)
 
    points = points * ps
    data = data * ds
    
    corr = np.dot(points,data.transpose())
    return corr
    

class KNearestNeighbors:
    """
    Basic k nearest neighbors algorithm.

    Based on the scipy.spatial.kdtree interface written by Anne M. Archibald 2008.
    
    This class performs a search over a set of D dimensional points and returns
    the k points that are nearest to a given point. 
    
    This class supports by default Minkowski p-norm distance measures and also
    cosine angle, and correlation similarity measures.  The class also supports
    the uses of user defined distance and similarity measures.
    """

    def __init__(self, points, p=2, is_distance=True):
        """
        Construct a nearest neighbor algorithm.

        @param data : array of n points with dimensionality d, shape (n,d).
            The data points to be indexed. This array is not copied, and
            so modifying this data will result in bogus results.
        @param p : float, 1<=p<=infinity
            Which Minkowski p-norm to use. 
            1 is the sum-of-absolute-values "Manhattan" distance
            2 is the usual Euclidean distance
            infinity is the maximum-coordinate-difference distance
            Also accepts the keywords "Manhattan", "Euclidean", and 
            "Correlation", or p can also be a user defined function with will 
            compute a distance matrix between two sets of points. 
        @param is_distance: True or False.  Determines if a user defined function is
            treated as a distance (smaller is better) or a similarity (larger
            values are better).
        """
        # Some basic tests to make sure data is of the correct type.
        if isinstance(p,int): 
            assert p > 0
        elif isinstance(p,str):
            assert p in ("Manhattan","Euclidean","Correlation")
        else:
            pass # Assume that p is a user specified function of proper type
            
        self.data = copy.deepcopy(points)
        self.p = p
        self.is_distance = is_distance
        
        
    def query(self, x, k=1, p=None, is_distance=True):
        """
        Query the instance for nearest neighbors

        @param x : array-like, last dimension self.k
            An array of points to query.
        @param k : integer
            The number of nearest neighbors to return.
        @param p : float, 1<=p<=infinity
            Which Minkowski p-norm to use. 
            1 is the sum-of-absolute-values "Manhattan" distance
            2 is the usual Euclidean distance
            infinity is the maximum-coordinate-difference distance
            Also accepts the keywords "Manhattan", "Euclidean", and 
            "Correlation", or p can also be a user defined function with will 
            compute a distance matrix between two sets of points. 

        @returns: a tuple (distances, indexes) 
        """
        if not isinstance(x, np.ndarray) or x.shape != (1,self.data.shape[1]):
            x = np.array(x).reshape(1,self.data.shape[1])
        # check the input
        #assert x.shape[1] == self.data.shape[1]
        #assert isinstance(k,int) and k > 0
        
        #if len(x.shape) == 1:
        #    x = x.reshape(1,)
            
        if p == None:
            p = self.p
            is_distance = self.is_distance
            
        # compute the distances between the input points and output points
        if p==np.inf or (isinstance(p,float) or isinstance(p,int)) and p >= 1.0:
            is_distance = True
            dist = PNorm(self.p)
        elif p == "Correlation":
            is_distance = False
            dist = correlation()
        elif p == "Euclidean":
            is_distance = True
            dist = PNorm(2)
        elif p == "Manhattan":
            is_distance = True
            dist = PNorm(1)
        else:
            dist = p #assume p is a user defined function
            
            
        # find the distance matrix between points
        dist_mat = dist(x,self.data).flatten()
        
        # set the index matrix
        dist_sort = np.argsort(dist_mat)
        if not is_distance:
            dist_sort = np.fliplr(dist_sort)
            
        dist_mat  = dist_mat[dist_sort] 

        if isinstance(k, int):
            dist_sort = dist_sort[:k]
            dist_mat = dist_mat[:k]
        else:
            i = dist_mat.searchsorted(k, side='right')
            dist_sort = dist_sort[:i]
            dist_mat = dist_mat[:i]
            
        return dist_mat,dist_sort
    
        
        
FLANN_IMPORTED = False

try:
    import pyflann
    
    class FLANNTree:
        def __init__(self,points,**kwargs):
            self.dtype = points.dtype
            #data = np.array(points,np.float64).copy()
            data = points
            self.n = data.shape[1]
            self.flann = pyflann.FLANN()
            start = time.time()
            self.index = self.flann.build_index(data,log_level='info')
            stop = time.time()
            self.indexing_time = stop-start
            
        def query(self, x, k=1,**kwargs):
            x = np.array(x)
            if x.shape == (0,):
                return [],[]  
            results,dists = self.flann.nn_index(x,num_neighbors=k,**kwargs)
            return np.sqrt(dists.flatten()),results.flatten()
                
    FLANN_IMPORTED = True
    
except:
    def FLANNTree(*args,**kwargs):
        print("WARNING: The pyflann library was not imported.  Using pv.KNearestNeighbors instead.")
        return pv.KNearestNeighbors(*args,**kwargs)

        
class AKNNTest(unittest.TestCase):
    
    def testLargeTree(self):
        '''Tests using a large tree.'''
        timer = pv.Timer()
        #N = 300
        #K = 5
        points = TEST_POINTS_5D
        
        timer.mark("Tree Build Start")
        kdtree = FLANNTree(points)
        timer.mark("Tree Build Time")
        knn = KNearestNeighbors(points)
        timer.mark("Linear Build Time")

        timer.mark("Query Start")
        fdist,_ = kdtree.query([.05,.3,.9,.6,.2],k=4)
        timer.mark("KDTree Query")

        timer.mark("Query Start")
        _,_ = knn.query([.05,.3,.9,.6,.2],k=fdist[-1])
        timer.mark("Brute Force Query")
        
        #print "\nRatio %d/%d = %f"%(len(fdist),len(bdist),float(len(fdist))/len(bdist))
        #print timer
        
    def testReallyLargeTree(self):
        '''Tests using a really large tree.'''
        timer = pv.Timer()
        N = 100000
        K = 5
        points = np.random.uniform(size=(N,K))
        
        timer.mark("Tree Build Start")
        kdtree = FLANNTree(points)
        timer.mark("Tree Build Time")
        knn = KNearestNeighbors(points)
        timer.mark("Linear Build Time")

        timer.mark("Query Start")
        fdist,_ = kdtree.query([.05,.3,.9,.6,.2],k=4)
        timer.mark("KDTree Query")

        timer.mark("Query Start")
        _,_ = knn.query([.05,.3,.9,.6,.2],k=fdist[-1])
        timer.mark("Brute Force Query")
        
        #print "\nRatio %d/%d = %f"%(len(fdist),len(bdist),float(len(fdist))/len(bdist))
        #print timer
        
    def testHighDim(self):
        '''test using high dimensions'''
        timer = pv.Timer()
        N = 100000
        K = 25
        points = np.random.uniform(size=(N,K))
        query = np.random.uniform(size=K)
        
        timer.mark("Tree Build Start")
        kdtree = FLANNTree(points)
        timer.mark("Tree Build Time")
        knn = KNearestNeighbors(points)
        timer.mark("Linear Build Time")

        timer.mark("Query Start")
        fdist,_ = kdtree.query(query,k=4,max_bins=100)
        timer.mark("KDTree Query")

        timer.mark("Query Start")
        _,_ = knn.query(query,k=fdist[-1])
        timer.mark("Brute Force Query")
        
        #print "\nRatio %d/%d = %f"%(len(fdist),len(bdist),float(len(fdist))/len(bdist))
        #print timer
        
            
            
    def testReallyHighDim(self):
        '''test using really high dimensions'''
        timer = pv.Timer()
        N = 1000
        K = 300
        points = np.random.uniform(size=(N,K))
        query = np.random.uniform(size=K)
        
        timer.mark("Tree Build Start")
        kdtree = FLANNTree(points)
        timer.mark("Tree Build Time")
        knn = KNearestNeighbors(points)
        timer.mark("Linear Build Time")

        timer.mark("Query Start")
        fdist,_ = kdtree.query(query,k=4,max_bins=100)
        timer.mark("KDTree Query")

        timer.mark("Query Start")
        _,_ = knn.query(query,k=fdist[-1])
        timer.mark("Brute Force Query")
        
        #print "\nRatio %d/%d = %f"%(len(fdist),len(bdist),float(len(fdist))/len(bdist))
        #print timer
        
            
            
TEST_POINTS_5D = np.array([[ 0.0927362947256, 0.863287852134, 0.827594225115, 0.063584486716, 0.696469104481, ],
[ 0.389212424081, 0.271960446851, 0.475318367898, 0.817676229636, 0.00304827195904, ],
[ 0.672444110392, 0.0158280396895, 0.148778847347, 0.639291398183, 0.644538534162, ],
[ 0.0916636652987, 0.351954938174, 0.574553430374, 0.288928168658, 0.78969352642, ],
[ 0.162269540706, 0.801590479688, 0.0811751837797, 0.581894157384, 0.671049941315, ],
[ 0.31781032373, 0.972737097753, 0.728113875496, 0.0352827009938, 0.436278903642, ],
[ 0.668665349139, 0.00869431735481, 0.0323020884506, 0.33204470022, 0.568487031887, ],
[ 0.554977019305, 0.404432014245, 0.448318790349, 0.090267021367, 0.801855198562, ],
[ 0.0426612471314, 0.821578220129, 0.590570236925, 0.942249465201, 0.0302523579783, ],
[ 0.761909737853, 0.32146029302, 0.839004185707, 0.462722613188, 0.539596120326, ],
[ 0.709501733964, 0.219788360337, 0.101400442883, 0.732893271973, 0.926611424005, ],
[ 0.0809400463112, 0.191982297666, 0.97370503065, 0.832543973631, 0.0478046269427, ],
[ 0.380337868256, 0.217302781186, 0.026326177554, 0.394898886382, 0.178055320195, ],
[ 0.585340778377, 0.897346639096, 0.688116012192, 0.0882641468119, 0.315376292507, ],
[ 0.847799169355, 0.494822709534, 0.9119358525, 0.913914687739, 0.758832257706, ],
[ 0.598829230281, 0.884220870752, 0.745880856431, 0.628961075144, 0.126208944967, ],
[ 0.538833285123, 0.678784395603, 0.377870137995, 0.784964320541, 0.457867661737, ],
[ 0.080521745984, 0.229840483568, 0.0499803363724, 0.0888950063361, 0.660528284769, ],
[ 0.739283572054, 0.826756268146, 0.264052850202, 0.357831012002, 0.412806228776, ],
[ 0.927767446867, 0.949291110779, 0.810525859158, 0.881019558964, 0.54684076154, ],
[ 0.450033122461, 0.508917827656, 0.178702446988, 0.993929793893, 0.414416923738, ],
[ 0.819621442166, 0.450342663617, 0.780300157518, 0.716759757424, 0.998183663211, ],
[ 0.067969651558, 0.863372774311, 0.636836741911, 0.409476164096, 0.192344312996, ],
[ 0.642922585529, 0.803937977964, 0.626923201367, 0.693585061364, 0.353756656086, ],
[ 0.634818777241, 0.149120965144, 0.481901389615, 0.941517733692, 0.339222789278, ],
[ 0.954704133567, 0.58862557958, 0.679649959654, 0.0165961047495, 0.787400354221, ],
[ 0.438949169444, 0.516071120846, 0.0592077102052, 0.978664661202, 0.925371619379, ],
[ 0.833149663342, 0.656388019222, 0.0882320466662, 0.964634067929, 0.566429796154, ],
[ 0.505057774233, 0.519850953282, 0.211266682662, 0.165183983177, 0.368512949226, ],
[ 0.605170174396, 0.830341564497, 0.225766364397, 0.0853992969972, 0.151470908653, ],
[ 0.145383700288, 0.278955847297, 0.103403017478, 0.45406188093, 0.303920542447, ],
[ 0.432683445278, 0.793847139887, 0.390982818312, 0.851866462591, 0.422964080669, ],
[ 0.205731984935, 0.102749700882, 0.786742205904, 0.398976523222, 0.0484067010483, ],
[ 0.0700390912143, 0.964015598953, 0.590372828676, 0.384804532681, 0.950909485267, ],
[ 0.472961335272, 0.312617438843, 0.0742518620549, 0.19359285018, 0.63914899342, ],
[ 0.802926693457, 0.414549107112, 0.939430844844, 0.983355566557, 0.062693470259, ],
[ 0.428306414402, 0.508243037384, 0.896642181542, 0.87205773333, 0.918910951515, ],
[ 0.376631627046, 0.493803381771, 0.753509407279, 0.481477002476, 0.926816150232, ],
[ 0.863636453108, 0.15831048815, 0.443755892517, 0.931767761921, 0.326280765236, ],
[ 0.566022293861, 0.428714279373, 0.572949602624, 0.664819118331, 0.0617970537683, ],
[ 0.830945080466, 0.0179186765183, 0.214406507913, 0.188537307583, 0.339064456629, ],
[ 0.608536965895, 0.961945983867, 0.143891313809, 0.22327042712, 0.302584907604, ],
[ 0.59477043091, 0.336792188989, 0.512297449572, 0.620989090245, 0.526365447555, ],
[ 0.500014605477, 0.488360343649, 0.845469883101, 0.437097474437, 0.292405558141, ],
[ 0.612332570018, 0.0652619027343, 0.370279882563, 0.0905855504143, 0.532651001832, ],
[ 0.520557451669, 0.453233435363, 0.849123340498, 0.0158698925421, 0.857237451492, ],
[ 0.748959109359, 0.153065700495, 0.806023020092, 0.10584427275, 0.351627545425, ],
[ 0.52491464714, 0.521598202489, 0.12909900013, 0.0859214095429, 0.368894569298, ],
[ 0.556654967907, 0.866168631509, 0.636822495867, 0.275389610284, 0.713589879255, ],
[ 0.881250685496, 0.532762716313, 0.351550119246, 0.351140183234, 0.484405543308, ],
[ 0.795438795822, 0.309596088009, 0.449334636782, 0.0150018400107, 0.295268547452, ],
[ 0.705678239054, 0.193681528445, 0.933153621094, 0.883763710874, 0.25279047558, ],
[ 0.986186284441, 0.694496650202, 0.629227674266, 0.576039881225, 0.819811019581, ],
[ 0.16542696173, 0.78089116713, 0.25140931855, 0.237433063211, 0.502516919218, ],
[ 0.423851630697, 0.743098974915, 0.263162988359, 0.950991645749, 0.366129775165, ],
[ 0.333807118952, 0.831106673815, 0.200872350703, 0.367006945241, 0.920319241957, ],
[ 0.503315006767, 0.797536433366, 0.646414416938, 0.0797766878495, 0.108232140675, ],
[ 0.643197529639, 0.421022926355, 0.264676139616, 0.321157409093, 0.0198318318113, ],
[ 0.529898829565, 0.954556982177, 0.0340020456139, 0.629484475933, 0.57854236117, ],
[ 0.635724175177, 0.461653800109, 0.692667103458, 0.455623949377, 0.439243563203, ],
[ 0.85483693196, 0.33260642413, 0.123883927144, 0.229090452944, 0.418735917079, ],
[ 0.91530280912, 0.550129982731, 0.491534806754, 0.777110292563, 0.736479237786, ],
[ 0.916424001522, 0.763421667967, 0.82106008195, 0.7033194726, 0.98484844128, ],
[ 0.427386534303, 0.573902609891, 0.434751173235, 0.916543709798, 0.0820037139868, ],
[ 0.634867743938, 0.413278279146, 0.910420049388, 0.609851902732, 0.439108923697, ],
[ 0.381980332894, 0.841285293548, 0.479264016959, 0.993794384356, 0.659770820295, ],
[ 0.386335862142, 0.542273654106, 0.0658716867539, 0.796827344613, 0.162246500003, ],
[ 0.961544557884, 0.596836561921, 0.633161520019, 0.294190256893, 0.010357532869, ],
[ 0.582826240909, 0.475217465864, 0.827578378278, 0.754114252136, 0.322810737757, ],
[ 0.90920558862, 0.57846254606, 0.75090039657, 0.703782073146, 0.0559242709879, ],
[ 0.00896179539354, 0.570614008967, 0.102823660034, 0.341973431533, 0.0350097591585, ],
[ 0.25430773991, 0.29675840817, 0.280038489358, 0.326535679048, 0.739148699296, ],
[ 0.132030703391, 0.0126655735067, 0.159765514897, 0.53410610653, 0.363588168778, ],
[ 0.768072089291, 0.263809613007, 0.285393759671, 0.88981743064, 0.536496117492, ],
[ 0.107810374218, 0.846960847733, 0.804233864684, 0.228925748827, 0.0299730417971, ],
[ 0.38822159315, 0.773771947951, 0.254354096512, 0.371017341028, 0.353325753965, ],
[ 0.17987950576, 0.639963546722, 0.628360668675, 0.750955979287, 0.0980571454951, ],
[ 0.328874491623, 0.036128661302, 0.858191934337, 0.508888327573, 0.0747610593483, ],
[ 0.324653207018, 0.822983821155, 0.987296812761, 0.808077390026, 0.320484168134, ],
[ 0.996459619758, 0.772338957883, 0.825612835536, 0.690603222941, 0.712543787595, ],
[ 0.246269957961, 0.926609536195, 0.790016192191, 0.508222845727, 0.330419634186, ],
[ 0.101183581538, 0.1309558164, 0.0359029585992, 0.701375821198, 0.0994872193255, ],
[ 0.227569554547, 0.558555166321, 0.18403772015, 0.202898843466, 0.6585290066, ],
[ 0.75210276461, 0.996505347686, 0.710120751219, 0.273711489848, 0.190296146033, ],
[ 0.0465756892356, 0.663813011507, 0.22389099851, 0.550738030528, 0.386926861473, ],
[ 0.957088907437, 0.42633096563, 0.866209431917, 0.171814079495, 0.866958043272, ],
[ 0.621371716382, 0.631461731645, 0.706995678733, 0.70147240529, 0.0456065233832, ],
[ 0.405301776191, 0.281245575007, 0.175520165097, 0.71243605014, 0.544869784686, ],
[ 0.276387150177, 0.874327645379, 0.782242803618, 0.86372114901, 0.442188001903, ],
[ 0.510899887312, 0.402891807459, 0.26723877352, 0.373368674397, 0.723381542368, ],
[ 0.918653465346, 0.967970107382, 0.0279812064827, 0.648904250121, 0.323449579131, ],
[ 0.29807355724, 0.872884941896, 0.826354907945, 0.711657210379, 0.250789352549, ],
[ 0.425982498451, 0.623521965663, 0.349198310726, 0.199953250118, 0.743847020727, ],
[ 0.410641857392, 0.688140095138, 0.832715190045, 0.960196456438, 0.695385704489, ],
[ 0.248760604152, 0.228566393287, 0.564709968098, 0.618499036462, 0.679907496946, ],
[ 0.907113889654, 0.843002369743, 0.746779665264, 0.225575316905, 0.462194858254, ],
[ 0.341802499121, 0.324809534648, 0.880408092175, 0.817807051959, 0.462104836574, ],
[ 0.480323879445, 0.459780887453, 0.645407745761, 0.665984984543, 0.504629371952, ],
[ 0.214930703747, 0.593106385247, 0.119989540941, 0.809374532463, 0.495372605848, ],
[ 0.431929564269, 0.644081428709, 0.126087889944, 0.334776617134, 0.221215198111, ],
[ 0.339150686676, 0.348389925001, 0.953091959749, 0.144107649435, 0.384686041093, ],
[ 0.501007624893, 0.514135362764, 0.147718896513, 0.300220160857, 0.121605585819, ],
[ 0.759584581771, 0.0883706566495, 0.0132800691016, 0.0838215045838, 0.0456875310833, ],
[ 0.635421833596, 0.0239928554369, 0.192480946424, 0.867999906082, 0.693572956176, ],
[ 0.0831028192209, 0.121132172322, 0.111637930089, 0.274699368942, 0.619549355338, ],
[ 0.507075029809, 0.76665053158, 0.03656132279, 0.309512753837, 0.935053620068, ],
[ 0.229937771055, 0.145875527689, 0.399610807251, 0.580266106732, 0.842256307345, ],
[ 0.361320122427, 0.409945148733, 0.35939394402, 0.552750578595, 0.0752344622836, ],
[ 0.105307011457, 0.887809841335, 0.848075063361, 0.100857687188, 0.709048908465, ],
[ 0.961449034214, 0.312006700587, 0.754886777936, 0.641444096606, 0.979193302399, ],
[ 0.517783139197, 0.926649253665, 0.177582087249, 0.247924780581, 0.628851660414, ],
[ 0.616338938067, 0.968069430525, 0.0368240829729, 0.0408474658086, 0.781544964214, ],
[ 0.414850863308, 0.00183643753064, 0.100487424499, 0.275884600178, 0.682589697979, ],
[ 0.110381534671, 0.519152691785, 0.826267923423, 0.340356719737, 0.606765568617, ],
[ 0.125550453432, 0.460607631408, 0.619576197056, 0.265003443978, 0.362511450009, ],
[ 0.551880577353, 0.444318449222, 0.374042361044, 0.912389004425, 0.164647089301, ],
[ 0.36255491043, 0.00301921237918, 0.741465515394, 0.741810797979, 0.266022870255, ],
[ 0.556736862831, 0.928896032853, 0.790912204319, 0.549326800043, 0.868537529651, ],
[ 0.456827553437, 0.511647495674, 0.607069480904, 0.441829505273, 0.293320446894, ],
[ 0.468391748591, 0.179174087327, 0.297655243942, 0.134443365772, 0.376131446952, ],
[ 0.36349651867, 0.51676686956, 0.697027819159, 0.878379159185, 0.448847280951, ],
[ 0.495579789689, 0.306165895141, 0.871786658628, 0.280476127939, 0.160878028563, ],
[ 0.55051871482, 0.173175997739, 0.0714950379756, 0.725558609579, 0.931835315245, ],
[ 0.993826643263, 0.171015978399, 0.857824632823, 0.0751405509171, 0.782018060628, ],
[ 0.563982407394, 0.688433676051, 0.730742164119, 0.714271132825, 0.39058600381, ],
[ 0.725999074361, 0.91286240957, 0.560939879381, 0.852628112742, 0.951825376107, ],
[ 0.621413625643, 0.149847412101, 0.217565396618, 0.621707835802, 0.13684805135, ],
[ 0.2969082778, 0.999079161245, 0.759328327398, 0.548751114449, 0.722625768842, ],
[ 0.968985939609, 0.496390457376, 0.827779021154, 0.319756420081, 0.985248410562, ],
[ 0.49037309144, 0.405126808747, 0.387792461904, 0.677767688643, 0.72331258346, ],
[ 0.831841038801, 0.063143708289, 0.778124423265, 0.0861773648417, 0.347530115514, ],
[ 0.85300962091, 0.459516719464, 0.303162098327, 0.0100085225189, 0.227995771788, ],
[ 0.935320104812, 0.181807297809, 0.792250682104, 0.161847646423, 0.395905878168, ],
[ 0.875205996076, 0.0962176078567, 0.735802990176, 0.586586683778, 0.187117866099, ],
[ 0.740566116219, 0.48094725507, 0.181890319662, 0.0286042459402, 0.183190923572, ],
[ 0.925612777607, 0.79680132467, 0.00835280526357, 0.969181006288, 0.14098615151, ],
[ 0.0240714490827, 0.525551532235, 0.880134887386, 0.934231767789, 0.670000637256, ],
[ 0.0181746299783, 0.574799320251, 0.672280857494, 0.341441064932, 0.801098526422, ],
[ 0.946484910309, 0.614876986563, 0.625035040819, 0.39227347036, 0.26163134575, ],
[ 0.402755272303, 0.961884003202, 0.53518863995, 0.960897224195, 0.486263188024, ],
[ 0.423855897577, 0.313041156076, 0.120615016724, 0.358772993293, 0.784169291004, ],
[ 0.755847898831, 0.491287040874, 0.353057569014, 0.616459057429, 0.38356282687, ],
[ 0.650176059076, 0.441015405163, 0.914168755226, 0.446778560532, 0.199464788292, ],
[ 0.714875095786, 0.973942601072, 0.636039102542, 0.272573658404, 0.875376752744, ],
[ 0.545315429387, 0.725190320533, 0.201843451258, 0.517514251598, 0.504950800713, ],
[ 0.482184041636, 0.094986046278, 0.359677520852, 0.117960376171, 0.608862139167, ],
[ 0.39329597724, 0.989673679416, 0.694688998517, 0.787769000767, 0.292054652219, ],
[ 0.37165580809, 0.371971489206, 0.839515132199, 0.898665044459, 0.135420015315, ],
[ 0.331688281266, 0.758100832865, 0.618037495654, 0.330038638163, 0.904220369609, ],
[ 0.709889296869, 0.711333077241, 0.523617933426, 0.444347476816, 0.327344688234, ],
[ 0.463963283177, 0.526911355433, 0.847971765809, 0.926891874077, 0.585978836436, ],
[ 0.655788424581, 0.387171054011, 0.182208906396, 0.209447400033, 0.704446320124, ],
[ 0.77301504054, 0.177093060138, 0.239697564734, 0.582170135584, 0.889617829638, ],
[ 0.0246550293311, 0.463784888839, 0.1294449748, 0.234775447112, 0.423783292753, ],
[ 0.542179547264, 0.204772562555, 0.0557148242831, 0.112397421472, 0.974487043962, ],
[ 0.595899512401, 0.691019530496, 0.760430803257, 0.95787770812, 0.162508767855, ],
[ 0.25268758039, 0.814228501862, 0.361588455356, 0.657044546421, 0.363314078985, ],
[ 0.970583975497, 0.101302292606, 0.92227986079, 0.816820632057, 0.925446886267, ],
[ 0.830724232766, 0.802276652066, 0.090352964891, 0.586347175165, 0.575297000789, ],
[ 0.633967138312, 0.157311320315, 0.382611156384, 0.754026916328, 0.844798101686, ],
[ 0.88008499734, 0.0554365208186, 0.772368607791, 0.244980860155, 0.623245486291, ],
[ 0.697090830005, 0.0435447975421, 0.608134752209, 0.620625153616, 0.494296642811, ],
[ 0.753713680088, 0.259465276847, 0.0635118708352, 0.476102500805, 0.143909610068, ],
[ 0.825402936838, 0.863844146013, 0.0563336571217, 0.679926041908, 0.575422445949, ],
[ 0.0515064600012, 0.763057741051, 0.18047627399, 0.506383782828, 0.460944822076, ],
[ 0.807195007503, 0.371250327067, 0.880211849114, 0.0771826627142, 0.0294468671302, ],
[ 0.994975141742, 0.611008576853, 0.55152425164, 0.466752816049, 0.0219002913715, ],
[ 0.838380629281, 0.702928822748, 0.895415088929, 0.175574747927, 0.0628996788059, ],
[ 0.61157651189, 0.451699327695, 0.812964675443, 0.337712930762, 0.136819291516, ],
[ 0.83631341855, 0.588556673425, 0.99844877287, 0.77235343568, 0.469242943583, ],
[ 0.670146297263, 0.850805178258, 0.644628744667, 0.187894247882, 0.645950979532, ],
[ 0.564321963024, 0.180162071511, 0.188000385459, 0.470875115889, 0.0627754832286, ],
[ 0.872345258971, 0.88350256947, 0.612014662236, 0.0740112010814, 0.963044765528, ],
[ 0.183314681328, 0.133523699803, 0.186339475709, 0.70777726641, 0.797799586525, ],
[ 0.387592738505, 0.897054953942, 0.663821456785, 0.762610078718, 0.919694519647, ],
[ 0.549264751508, 0.376902696353, 0.172603935307, 0.404601657731, 0.317475429779, ],
[ 0.18892608643, 0.26391961452, 0.202211277689, 0.977133684289, 0.94969189209, ],
[ 0.622624703135, 0.876007468382, 0.073903020827, 0.107906008359, 0.0989968274197, ],
[ 0.550913778465, 0.105336256604, 0.923739881586, 0.340524256022, 0.762191530824, ],
[ 0.816531050865, 0.189600632169, 0.530365651435, 0.687376286733, 0.0723437514617, ],
[ 0.27793168643, 0.132321877489, 0.142967852855, 0.988242868115, 0.584675750238, ],
[ 0.0818458972375, 0.0426173938908, 0.254098151626, 0.762976503817, 0.598404106216, ],
[ 0.217702281522, 0.868277590329, 0.333507197691, 0.0448683380706, 0.0494121898063, ],
[ 0.89809048022, 0.605180920361, 0.871545146656, 0.971111090163, 0.716234223694, ],
[ 0.580976210321, 0.750062800185, 0.312524912237, 0.105561156831, 0.495798041296, ],
[ 0.525709325384, 0.397829050087, 0.685815891556, 0.483512345228, 0.0464130510249, ],
[ 0.717619265984, 0.375664985863, 0.0636742467106, 0.153916930873, 0.983934529433, ],
[ 0.949916008535, 0.27595683092, 0.97844998592, 0.577015974481, 0.117714428705, ],
[ 0.551014130103, 0.636384750905, 0.348501224976, 0.676898904079, 0.387896282478, ],
[ 0.623653709467, 0.14138569337, 0.939388369824, 0.328196080415, 0.85734154963, ],
[ 0.0148526781387, 0.51658991201, 0.369263401688, 0.00660283653342, 0.909564240392, ],
[ 0.678019312415, 0.29030945944, 0.484533635654, 0.628332804932, 0.412282547391, ],
[ 0.01030632693, 0.43087391709, 0.97755510403, 0.169696953367, 0.298532486852, ],
[ 0.934020686247, 0.128037187033, 0.348059648835, 0.850385387302, 0.991458538806, ],
[ 0.490820048261, 0.136442027719, 0.722287538405, 0.182304810474, 0.527406959885, ],
[ 0.82386874877, 0.519128670292, 0.0414059070416, 0.945426346692, 0.625613911176, ],
[ 0.0311133066343, 0.441503902663, 0.375920841461, 0.897105904691, 0.541202606675, ],
[ 0.563197969175, 0.759175059294, 0.205298865317, 0.909108356464, 0.148544658178, ],
[ 0.73130327803, 0.247041364454, 0.806957402361, 0.69909562392, 0.888700767166, ],
[ 0.0496096989413, 0.628698266456, 0.152326756316, 0.296076379609, 0.269789640987, ],
[ 0.0495419605003, 0.361605722655, 0.985918157788, 0.528229573654, 0.882700340363, ],
[ 0.0399222723152, 0.985118081922, 0.139968651954, 0.532392267278, 0.0914442602876, ],
[ 0.944920922226, 0.738959769477, 0.996559394676, 0.459856457071, 0.957527421625, ],
[ 0.561969390662, 0.41673507473, 0.824319205619, 0.5298455412, 0.530002206583, ],
[ 0.428394305708, 0.424915765316, 0.0549202149483, 0.0807408367942, 0.572927686686, ],
[ 0.825890357887, 0.154230364401, 0.0578841074242, 0.846961024769, 0.101402912405, ],
[ 0.282035505852, 0.173654721423, 0.719302803058, 0.450877627819, 0.786849378662, ],
[ 0.154376510867, 0.382877072042, 0.826728239339, 0.869068644655, 0.561230396783, ],
[ 0.286533378413, 0.546921237326, 0.309187222683, 0.792688717174, 0.447815450863, ],
[ 0.0289871231502, 0.968440697457, 0.306616689383, 0.436936365406, 0.446708160331, ],
[ 0.177674989967, 0.785385163859, 0.0252278887912, 0.74767137612, 0.368543883185, ],
[ 0.792658111874, 0.121810464007, 0.81504944869, 0.0182663395301, 0.839440268692, ],
[ 0.511891222833, 0.57493101508, 0.651435201701, 0.0702756274324, 0.903286785126, ],
[ 0.215574495964, 0.766893833005, 0.356985434897, 0.50448827254, 0.19828616731, ],
[ 0.511495117938, 0.586954300681, 0.0866689144206, 0.092127333886, 0.562061201616, ],
[ 0.632810572411, 0.782552398629, 0.684289275958, 0.096288558666, 0.542753766234, ],
[ 0.25767346928, 0.760469359775, 0.616788489967, 0.995284108518, 0.181553087072, ],
[ 0.925440510942, 0.505476753363, 0.310177615305, 0.757581033492, 0.670368882599, ],
[ 0.313783398217, 0.656739683053, 0.995048227272, 0.191855760191, 0.255712791187, ],
[ 0.27672567734, 0.289307835761, 0.512713909429, 0.68578789937, 0.80689919094, ],
[ 0.528035844174, 0.204351948475, 0.67139121589, 0.594251519106, 0.524827157896, ],
[ 0.131979560086, 0.364520596935, 0.118996516877, 0.562434225944, 0.635568973312, ],
[ 0.432114285422, 0.445851169614, 0.651276145019, 0.84166575738, 0.507821582835, ],
[ 0.470165629159, 0.891142088726, 0.185857827717, 0.0141436707482, 0.71611965094, ],
[ 0.934294110777, 0.348657657959, 0.95798592453, 0.538466556428, 0.488677620719, ],
[ 0.82069915627, 0.52576335004, 0.766075720258, 0.861483959118, 0.354516856109, ],
[ 0.075622405181, 0.92465225395, 0.328498783503, 0.667176786233, 0.925196686945, ],
[ 0.542662655945, 0.950719237404, 0.96625066574, 0.603987827683, 0.988557076692, ],
[ 0.811131795287, 0.261005436556, 0.740817723459, 0.502287209341, 0.279508368305, ],
[ 0.496904047311, 0.196573581326, 0.760719060479, 0.14945669731, 0.374312383674, ],
[ 0.597301251995, 0.906894599748, 0.532070828256, 0.478898639199, 0.909910999593, ],
[ 0.169327237814, 0.157371129413, 0.0838259255463, 0.690923808532, 0.0668661102322, ],
[ 0.386254239048, 0.371789420155, 0.812661257547, 0.214502241094, 0.486407324372, ],
[ 0.934093909223, 0.22042072823, 0.214969521253, 0.661311979567, 0.379615984777, ],
[ 0.0253147437493, 0.836737318506, 0.87155226507, 0.472801653726, 0.645152775508, ],
[ 0.795589470149, 0.444292386464, 0.308207913507, 0.354225210586, 0.0250780816618, ],
[ 0.910184643674, 0.810055856414, 0.334606882852, 0.987814752048, 0.576538748819, ],
[ 0.917977581965, 0.196751690169, 0.794584005179, 0.161681456235, 0.602215964691, ],
[ 0.531722774016, 0.0572397743157, 0.666982620526, 0.599279406282, 0.934128475539, ],
[ 0.274517288696, 0.102036760307, 0.377389206995, 0.379482664656, 0.433076028282, ],
[ 0.0930947896689, 0.248730240573, 0.550007351929, 0.594148414938, 0.97800066392, ],
[ 0.676010870035, 0.993823412279, 0.687255291573, 0.952375385935, 0.488739768653, ],
[ 0.903064027068, 0.773691537207, 0.696497470037, 0.0521292064275, 0.0811685968696, ],
[ 0.905309911627, 0.888027818689, 0.724570913357, 0.319235347431, 0.83004944828, ],
[ 0.212319964224, 0.0415596758339, 0.957962651499, 0.143446618911, 0.630728452613, ],
[ 0.24655064964, 0.168929955034, 0.575234849494, 0.812780033822, 0.859116804114, ],
[ 0.61197693027, 0.404214748382, 0.583006654485, 0.783985820043, 0.112162938217, ],
[ 0.437946190715, 0.909847873901, 0.822722912199, 0.552508837987, 0.539607554392, ],
[ 0.411276651729, 0.293749349311, 0.0255371070901, 0.931717390318, 0.528603254674, ],
[ 0.740337747158, 0.0268455535856, 0.500233216764, 0.44639611196, 0.374421486395, ],
[ 0.833609020442, 0.419284080708, 0.75484316172, 0.3842353931, 0.681644641281, ],
[ 0.47230692374, 0.0675444954248, 0.609414267664, 0.431604797117, 0.648095536047, ],
[ 0.821030020183, 0.849220740556, 0.493818696078, 0.984864173521, 0.692374864186, ],
[ 0.330810461985, 0.762522427678, 0.931285702919, 0.601467875898, 0.75360872135, ],
[ 0.703311877861, 0.0628630922753, 0.902276484019, 0.312411553779, 0.302180416166, ],
[ 0.527086667958, 0.871687632493, 0.407655937149, 0.626428718315, 0.980717974987, ],
[ 0.795627409213, 0.00991918229415, 0.825360777209, 0.025007303119, 0.865366145392, ],
[ 0.474921627625, 0.803356099066, 0.881314052985, 0.497226291105, 0.976410660473, ],
[ 0.337104759634, 0.755151820533, 0.234116154735, 0.642747451879, 0.28252022253, ],
[ 0.959933746478, 0.0748788544196, 0.853807699427, 0.830407066977, 0.915947826252, ],
[ 0.53770833156, 0.529917102756, 0.647497199733, 0.155984372465, 0.316204794161, ],
[ 0.811399264163, 0.526138758994, 0.276552288603, 0.2342170157, 0.414695277228, ],
[ 0.470542178889, 0.370421629948, 0.547432799041, 0.565777809244, 0.629235848659, ],
[ 0.0570512941297, 0.863401220808, 0.438805812943, 0.879999686801, 0.604015107847, ],
[ 0.488317756546, 0.659977566397, 0.746531092908, 0.774674647844, 0.25992701782, ],
[ 0.781234196283, 0.627572675031, 0.624902566528, 0.39390816581, 0.890845814234, ],
[ 0.317700956445, 0.402262272525, 0.550427946922, 0.406907037713, 0.051822861917, ],
[ 0.494151210695, 0.522071448618, 0.543478091642, 0.727156905495, 0.849529566326, ],
[ 0.653063773482, 0.940953670169, 0.0233529533453, 0.978413324351, 0.139590774176, ],
[ 0.474460342797, 0.362313841145, 0.0406308462435, 0.360662855811, 0.0507959701105, ],
[ 0.0710136351527, 0.486629965333, 0.875413873531, 0.405392740209, 0.165472168976, ],
[ 0.00589069536576, 0.944228109596, 0.713360024197, 0.0689139428592, 0.784213923963, ],
[ 0.591095360341, 0.119716088652, 0.739655586432, 0.846152565816, 0.449694450648, ],
[ 0.74836151201, 0.79426353285, 0.179993154193, 0.713099168281, 0.550125747716, ],
[ 0.491735927378, 0.292219775785, 0.0122174829458, 0.819383486544, 0.335238500669, ],
[ 0.342494181226, 0.136699786631, 0.571209721719, 0.0636974449037, 0.0431561384771, ],
[ 0.27581531686, 0.0136849412657, 0.572091152501, 0.941808184371, 0.611240568309, ],
[ 0.702428529494, 0.248755095048, 0.542504317623, 0.802784834226, 0.845331531194, ],
[ 0.00377749909234, 0.127646087254, 0.661088728786, 0.144358887083, 0.829566389206, ],
[ 0.48744303814, 0.701731211773, 0.979760197848, 0.984472161146, 0.3444595375, ],
[ 0.47621431965, 0.769290836391, 0.766603308368, 0.673462881333, 0.641037473396, ],
[ 0.426271340285, 0.414078266975, 0.010534994384, 0.581868199558, 0.00104456829485, ],
[ 0.62090818114, 0.480161678894, 0.886391732834, 0.0198674992995, 0.675298135127, ],
[ 0.00182250435232, 0.519400227906, 0.472514968874, 0.813106958508, 0.0958568312366, ],
[ 0.668309761093, 0.546114276519, 0.823944794168, 0.680896643321, 0.260147970427, ],
[ 0.0630745674698, 0.473768086254, 0.226284932677, 0.671212277501, 0.451555116525, ],
[ 0.554579306667, 0.384413383998, 0.90006769451, 0.730083456365, 0.340669181702, ],
[ 0.250670006893, 0.565414933522, 0.411680141089, 0.534730191973, 0.722610776317, ],
[ 0.0511074585216, 0.0544261721128, 0.89407515591, 0.542018734859, 0.784161892564, ],
[ 0.147580670964, 0.109046706282, 0.106247573372, 0.764543145227, 0.537221337128, ],
[ 0.866644440934, 0.0691537926189, 0.721613967656, 0.525645196681, 0.478800900502, ],
[ 0.255281144569, 0.24003123614, 0.359465333607, 0.674464398149, 0.261829600216, ],
[ 0.342155466853, 0.800794582938, 0.634758235245, 0.845344819706, 0.700849107157, ],
[ 0.109620796605, 0.729674448918, 0.684463000885, 0.886309292014, 0.25552349977, ],
[ 0.300287385474, 0.482564197858, 0.596039612163, 0.185892305409, 0.816971820497, ],
[ 0.408397713869, 0.352549518525, 0.215729557732, 0.207240399481, 0.820826180079, ],
[ 0.812287898966, 0.524480059471, 0.345920884379, 0.723567812019, 0.723939465976, ],
[ 0.85090480131, 0.166964438016, 0.401637719939, 0.346174041104, 0.824927548035, ],
[ 0.419685412259, 0.732811534966, 0.610319538745, 0.35727404665, 0.270207246386, ],
[ 0.567257469986, 0.397959285112, 0.584879162489, 0.686223906856, 0.390366787099, ],
])

        