# class based wrapper for .h5 files from Flydra
# written by Floris van Breugel

# depends on flydra.analysis and flydra.a2 -- if these are not installed, point to the appropriate path

# once you have this dataset class, the data no longer depends on flydra, and therefore, matplotlib 0.99

try:
    import flydra.a2.core_analysis as core_analysis
    import flydra.analysis.result_utils as result_utils
except:
    print('Need to install flydra, sorry!')
    
import numpy as np
import pickle
import sys


class Dataset:

    def __init__(self):
        self.trajecs = {}
	
    def load_data(self, filename, kalman_smoothing=False, dynamic_model=None, fps=None, info={}, save_covariance=False):
        # use info to pass information to trajectory instances as a dictionary. 
        # eg. info={"post_type": "black"}
        # save_covariance: set to True if you need access to the covariance data. Keep as False if this is not important for analysis (takes up lots of space)

        # set up analyzer
        ca = core_analysis.get_global_CachingAnalyzer()
        (obj_ids, use_obj_ids, is_mat_file, data_file, extra) = ca.initial_file_load(filename)

        # data set defaults
        if fps is None:
            fps = result_utils.get_fps(data_file)
        if dynamic_model is None:
            try:
	        dyn_model = extra['dynamic_model_name']
            except:
	        print 'cannot find dynamic model'
        if dynamic_model is not None:
            dyn_model = dynamic_model

        # if kalman smoothing is on, then we cannot use the EKF model - remove that from the model name
        print '** Kalman Smoothing is: ', kalman_smoothing, ' **'
        if kalman_smoothing is True:
            dyn_model = dyn_model[4:]
        print 'using dynamic model: ', dyn_model
        print 'framerate: ', fps
        print 'loading data.... '
        
        # load object id's and save as Trajectory instances
        for obj_id in use_obj_ids:
            print 'processing: ', obj_id
            try: 
                print obj_id
                kalman_rows = ca.load_data( obj_id, data_file,
                                 dynamic_model_name = dyn_model,
                                 use_kalman_smoothing= kalman_smoothing,
                                 frames_per_second= fps)
            except:
                print 'object id failed to load (probably no data): ', obj_id
                continue

            # couple object ID dictionary with trajectory objects
            trajec_id = str(obj_id) # this is not necessarily redundant with the obj_id, it allows for making a unique trajectory id when merging multiple datasets
            self.trajecs.setdefault(trajec_id, Trajectory(trajec_id, kalman_rows, info=info, fps=fps, save_covariance=save_covariance))
        return
        
    def del_trajec(self, key):
        del (self.trajecs[key])
    
    def get_trajec(self, n=0):
        key = self.trajecs.keys()[n]
        return self.trajecs[key]

class Trajectory:
    def __init__(self, trajec_id, kalman_rows, info={}, fps=None, save_covariance=False):
        self.key = trajec_id
        self.info = info
        self.fps = fps
        
        """
        kalman rows =   [0] = obj_id
                        [1] = frame
                        [2] = timestamp
                        [3:6] = positions
                        [6:9] = velocities
                        [9:12] = P00-P02
                        [12:18] = P11,P12,P22,P33,P44,P55
                        [18:21] = rawdir_pos
                        [21:24] = dir_pos
                        
                        dtype=[('obj_id', '<u4'), ('frame', '<i8'), ('timestamp', '<f8'), ('x', '<f8'), ('y', '<f8'), ('z', '<f8'), ('xvel', '<f8'), ('yvel', '<f8'), ('zvel', '<f8'), ('P00', '<f8'), ('P01', '<f8'), ('P02', '<f8'), ('P11', '<f8'), ('P12', '<f8'), ('P22', '<f8'), ('P33', '<f8'), ('P44', '<f8'), ('P55', '<f8'), ('rawdir_x', '<f4'), ('rawdir_y', '<f4'), ('rawdir_z', '<f4'), ('dir_x', '<f4'), ('dir_y', '<f4'), ('dir_z', '<f4')])
                        
        Covariance Matrix (P):

          [ xx  xy  xz
            xy  yy  yz
            xz  yz  zz ]
            
            full covariance for trajectories as velc as well
                        
        """

        self.obj_id = kalman_rows[0][0]
        self.first_frame = int(kalman_rows[0][1])
        self.fps = float(fps)
        self.length = len(kalman_rows)
		
        try:
            self.timestamp = time.strftime( '%Y%m%d_%H%M%S', time.localtime(extra['time_model'].framestamp2timestamp(kalman_rows[0][1])) )
        except:
            pass
            self.timestamp = None
        self.time_fly = np.arange(0,self.length,1/self.fps) 

        self.positions = np.zeros([self.length, 3])
        self.velocities = np.zeros([self.length, 3])
        self.speed = np.zeros([self.length])
        self.speed_xy = np.zeros([self.length])
        self.length = len(self.speed)

        for i in range(len(kalman_rows)):
            for j in range(3):
                self.positions[i][j] = kalman_rows[i][j+3]
                self.velocities[i][j] = kalman_rows[i][j+6]
            self.speed[i] = np.sqrt(kalman_rows[i][6]**2+kalman_rows[i][7]**2+kalman_rows[i][8]**2)
            self.speed_xy[i] = np.sqrt(kalman_rows[i][6]**2+kalman_rows[i][7]**2)
            
        if save_covariance:
            self.covariance_position = [np.zeros([3,3]) for i in range(self.length)]
            self.covariance_velocity = [np.zeros([3]) for i in range(self.length)]
            for i in range(self.length):
                self.covariance_position[i][0,0] = kalman_rows[i]['P00']
                self.covariance_position[i][0,1] = kalman_rows[i]['P01']
                self.covariance_position[i][0,2] = kalman_rows[i]['P02']
                self.covariance_position[i][1,1] = kalman_rows[i]['P11']
                self.covariance_position[i][1,2] = kalman_rows[i]['P12']
                self.covariance_position[i][2,2] = kalman_rows[i]['P22']
                self.covariance_velocity[i][0] = kalman_rows[i]['P33']
                self.covariance_velocity[i][1] = kalman_rows[i]['P44']
                self.covariance_velocity[i][2] = kalman_rows[i]['P55']
		
###################################################################################################
# General use dataset functions
###################################################################################################

# recommended function naming scheme:
    # calc_foo(trajec): will save values to trajec.foo (use sparingly on large datasets)
    # get_foo(trajec): will return values
    # use iterate_calc_function(dataset, function) to run functions on all the trajectories in a dataset
    
def save(dataset, filename):
    print 'saving dataset to file: ', filename
    fname = (filename)  
    fd = open( fname, mode='w' )
    pickle.dump(dataset, fd)
    fd.close()
    return 1
    
def load(filename):
    fname = (filename)
    fd = open( fname, mode='r')
    print 'loading data... '
    dataset = pickle.load(fd)
    fd.close()
    return dataset
    
# this function lets you write functions that operate on the trajectory class, but then easily apply that function to all the trajectories within a dataset class. It makes debugging new functions easier/faster if you write to operate on a trajectory. 
def iterate_calc_function(dataset, function, keys=None, *args, **kwargs):
    # keys allows you to provide a list of keys to perform the function on, default is all the keys
    if keys is None:
        keys = dataset.trajecs.keys()
    for key in keys:
        trajec = dataset.trajecs[key]
        function(trajec, *args, **kwargs)
        
def merge_datasets(dataset_list):
    # dataset_list should be a dataset
    dataset = Dataset()
    n = 0
    for d in dataset_list:
        for k, trajec in d.trajecs.iteritems():
            new_trajec_id = str(n) + '_' + k # make sure we use unique identifier
            trajec.key = new_trajec_id
            dataset.set_default(new_trajec_id, trajec)
    return dataset
    
    

###################################################################################################
# Example usage
###################################################################################################

def example_load_single_h5_file(filename):
    # filename should be a .h5 file
    info = {'post_type': 'black', 'post_position': np.zeros([3]), 'post_radius': 0.0965}
    dataset = Dataset()
    dataset.load_data(filename, kalman_smoothing=True, save_covariance=False, info=info)
    print 'saving dataset...'
    save(dataset, 'example_load_single_h5_file_pickled_dataset')

    for k, trajec in dataset.trajecs.iteritems():
        print 'key: ', k, 'trajectory length: ', trajec.length, 'speed at end of trajec: ', trajec.speed[-1]

if __name__ == "__main__":
    pass
    
