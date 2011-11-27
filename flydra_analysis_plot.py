import floris_plot_lib as fpl
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import patches

def example_xy_spagetti(dataset):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_ylim(-.15,.15)
    ax.set_xlim(-.25, .25)
    ax.set_autoscale_on(False)
    
    xy_spagetti(ax, dataset, keys=None, nkeys=300, show_saccades=False, keys_to_highlight=[], colormap=None, color='gray')
    fig.savefig('example_xy_spagetti_plot.pdf', format='pdf')

def xy_spagetti(ax, dataset, keys=None, nkeys=300, start_key=0, show_saccades=False, keys_to_highlight=[], colormap=None, color='gray'):
    if keys is None:
        keys = dataset.trajecs.keys()
    if nkeys < len(keys):
        last_key = np.min([len(keys), start_key+nkeys])
        keys = keys[start_key:last_key]
        keys.extend(keys_to_highlight)
            
    for key in keys:
        trajec = dataset.trajecs[key]    
        
        if key in keys_to_highlight:
            alpha = 1
            linewidth = 1
            color = 'black'
            zorder = 500
            ax.plot(trajec.positions[:,0], trajec.positions[:,1], '-', color='black', alpha=1, linewidth=linewidth, zorder=zorder)
        else:
            linewidth = 0.5
            zorder = 100
            ax.plot(trajec.positions[:,0], trajec.positions[:,1], '-', color=color, alpha=1, linewidth=linewidth, zorder=zorder)
            
        if show_saccades:
            if len(trajec.sac_ranges) > 0:
                for sac_range in trajec.sac_ranges:
                    if sac_range[0] < trajec.frame_nearest_to_post:
                    #if 1:
                        ax.plot(trajec.positions[sac_range,0], trajec.positions[sac_range,1], '-', color='red', alpha=alpha2, linewidth=linewidth, zorder=zorder+1)
                        sac = patches.Circle( (trajec.positions[sac_range[0],0], trajec.positions[sac_range[0],1]), radius=0.001, facecolor='red', edgecolor='none', alpha=alpha2, zorder=zorder+1)
                        ax.add_artist(sac)
            
    
    
    
    
    post = patches.Circle( (0, 0), radius=0.009565, facecolor='black', edgecolor='none', alpha=1)
    ax.add_artist(post)
    #ax.text(0,0,'post\ntop view', horizontalalignment='center', verticalalignment='center')
    
    
    #post = patches.Circle( (0, 0), radius=0.028, facecolor='none', edgecolor='red', alpha=1, linewidth=0.15, linestyle='dashed')
    #ax.add_artist(post)
    
