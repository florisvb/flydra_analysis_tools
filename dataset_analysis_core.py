import flydra_analysis_dataset as fad
import trajectory_analysis_core as tac

###################################################################################################
# Commonly used, but specific, dataset functions
###################################################################################################

def cull_dataset_min_frames(dataset, min_length_frames=10):
    fad.iterate_calc_function(dataset, tac.mark_for_culling_based_on_min_frames, keys=None, min_length_frames=min_length_frames)
    return fad.make_dataset_with_attribute_filter(dataset, 'cull', False)

def cull_dataset_cartesian_volume(dataset, x_range, y_range, z_range):
    fad.iterate_calc_function(dataset, tac.mark_for_culling_based_on_cartesian_position, keys=None, ok_range=x_range, axis=0)
    fad.iterate_calc_function(dataset, tac.mark_for_culling_based_on_cartesian_position, keys=None, ok_range=y_range, axis=1)
    fad.iterate_calc_function(dataset, tac.mark_for_culling_based_on_cartesian_position, keys=None, ok_range=z_range, axis=2)
    return fad.make_dataset_with_attribute_filter(dataset, 'cull', False)
