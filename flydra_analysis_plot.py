import floris_plot_lib as fpl
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import patches
import trajectory_analysis_specific as tas

def example_xy_spagetti(dataset):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_ylim(-.15,.15)
    ax.set_xlim(-.25, .25)
    ax.set_autoscale_on(False)
    
    xy_spagetti(ax, dataset, keys=None, nkeys=300, show_saccades=False, keys_to_highlight=[], colormap=None, color='gray')
    prep_xy_spagetti_for_saving(ax)
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
        
        
        frame1 = tas.get_frame_at_distance(trajec, 0.2)
        if trajec.frame_nearest_to_post <= frame1 or trajec.frame_nearest_to_post is None: 
            continue
        print key, trajec.xy_distance_to_post[frame1], trajec.xy_distance_to_post[trajec.frame_nearest_to_post]
        frames = np.arange(trajec.framerange[0], trajec.framerange[1])
        
        if key in keys_to_highlight:
            alpha = 1
            linewidth = 1
            color = 'black'
            zorder = 500
            ax.plot(trajec.positions[frames,0], trajec.positions[frames,1], '-', color='black', alpha=1, linewidth=linewidth, zorder=zorder)
        else:
            linewidth = 0.5
            zorder = 100
            ax.plot(trajec.positions[frames,0], trajec.positions[frames,1], '-', color=color, alpha=1, linewidth=linewidth, zorder=zorder)
            
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
    
    
def prep_xy_spagetti_for_saving(ax):
    
    rect = patches.Rectangle( [-.25, -.15], .5, .3, facecolor='none', edgecolor='gray', clip_on=False, linewidth=0.2)
    ax.add_artist(rect)
    
    offset = 0.00
    dxy = 0.05
    #xarrow = patches.FancyArrowPatch(posA=(-.25+offset, -.15+offset), posB=(-.25+offset+dxy, -.15+offset), arrowstyle='simple') 
    #patches.Arrow( -.25+offset, -.15+offset, dxy, 0, color='black', width=0.002)
    xarrow = patches.FancyArrowPatch((-.25+offset, -.15+offset), (-.25+offset+dxy, -.15+offset), arrowstyle="-|>", mutation_scale=10, color='gray', shrinkA=0, clip_on=False)
    ax.add_patch(xarrow)
    yarrow = patches.FancyArrowPatch((-.25+offset, -.15+offset), (-.25+offset, -.15+offset+dxy), arrowstyle="-|>", mutation_scale=10, color='gray', shrinkA=0, clip_on=False)
    ax.add_artist(yarrow)
    text_offset = -.011
    ax.text(-.25+offset+dxy+text_offset, -.15+offset+.005, 'x', verticalalignment='bottom', horizontalalignment='left', color='gray', weight='bold')
    ax.text(-.25+offset+.005, -.15+offset+dxy+text_offset, 'y', verticalalignment='bottom', horizontalalignment='left', color='gray', weight='bold')
    
    scale_bar_offset = 0.01
    ax.hlines(-0.15+scale_bar_offset, 0.25-scale_bar_offset-.1, 0.25-scale_bar_offset, linewidth=1, color='gray')
    ax.text(0.25-scale_bar_offset-.1/2., -0.15+scale_bar_offset+.002, '10cm', horizontalalignment='center', verticalalignment='bottom', color='gray')
    
    ax.set_aspect('equal')
    
    scaling = .5/.75
    margin = 0.04
    aspect_ratio = 3/5. # height/width
    
    fig_width = 7.204*scaling
    plt_width = fig_width - 2*margin*(1-aspect_ratio)
    fig_height = plt_width*aspect_ratio + 2*margin
    
    fig = ax.figure
    
    fig.set_size_inches(fig_width,fig_height)
    fig.subplots_adjust(bottom=margin, top=1-margin, right=1, left=0)
    ax.set_axis_off()
    
