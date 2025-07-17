# Import and configure the necessary modules.

from numpy import *

import h5py

from scipy.optimize import curve_fit

import matplotlib
import matplotlib.pyplot
import pandas as pd
matplotlib.rcParams['text.latex.preamble'] = r'\usepackage{starfont} \usepackage{amsmath}'

#-------------------------------------------------------------------------------
# Define the model functions for fitting.
#-------------------------------------------------------------------------------

# Define the model function for a power law.

def mod_power( x, c, a ) :

	return c * ( x**a )

# Define the model function for a singly broken power law.

def mod_broken( x, c, x0, a1, a2, force=0 ):

	y = [ ]

	for xx in x :

		if ( ( ( force == 0 ) and ( xx <= x0 ) ) or
		       ( force == 1 )                       ) :
			y.append( c * xx**a1 )
		else :
			y.append( c * ( x0**( a1 - a2 ) ) * ( xx**a2 ) )

	return y

# Define the model function for a doubly broken power law.

def mod_broken2( x, c, xa, xb, a1, a2, a3, force=0 ):

	y = [ ]

	for xx in x :

		if ( ( ( force == 0 ) and ( xx <= xa ) ) or
		       ( force == 1 )                       ) :
			y.append( c * xx**a1 )
		elif ( ( ( force == 0 ) and ( xx <= xb ) ) or
		         ( force == 2 )                       ) :
			y.append( c * ( xa**( a1 - a2 ) ) * ( xx**a2 ) )
		else :
			y.append( c * ( xa**( a1 - a2 ) ) * ( xb**( a2 - a3 ) ) * ( xx**a3 ) )

	return y

#-------------------------------------------------------------------------------
# Define the function for generating a plot.
#-------------------------------------------------------------------------------

# Arguments:
#	key: A string indicating the parameter to plotted
# Keywords:
#	scaled: A boolean indicating whether the composite plot should show the
#	        the scaled or unscaled (i.e., dimensional) parameter values.

# Output: A plot like this
#	+---------------------+
#	|                     |
#	|     Histogram       |
#	|                     |
#	+---------------------+
#	|                     |
#	|                     |
#	|                     |
#	|                     |
#	|   Individual Plot   |
#	|                     |
#	| +-----+             |
#	| | Key |             |
#	| +-----+             |
#	+---------------------+
#	|                     |
#	|                     |
#	|                     |
#	|                     |
#	|   Composite Plot    |
#	|                     |
#	| +-----+             |
#	| | Fit |             |
#	| +-----+             |
#	+---------------------+

def plot_msc( key, scaled=True ) :

	# Define the location of the plot within the figure as well as the size of each.

	inch_plot_x      = 5.00
	inch_plot_y      = 3.00

	inch_hist_x      = inch_plot_x
	inch_hist_y      = 1.00

	inch_mrgn_left   = 0.65
	inch_mrgn_right  = 0.05
	inch_mrgn_bottom = 0.45
	inch_mrgn_top    = 0.20

	inch_fig_x = ( inch_mrgn_left   + inch_plot_x + inch_mrgn_right )
	inch_fig_y = ( inch_mrgn_bottom + 2. * inch_plot_y
	                                +      inch_hist_y + inch_mrgn_top   )

	figsize = [ inch_fig_x, inch_fig_y ]

	pos_comp = [ inch_mrgn_left   / inch_fig_x,
	             inch_mrgn_bottom / inch_fig_y,
	             inch_plot_x      / inch_fig_x,
	             inch_plot_y      / inch_fig_y  ]

	pos_indiv = [ inch_mrgn_left                     / inch_fig_x,
	              ( inch_mrgn_bottom + inch_plot_y ) / inch_fig_y,
	              inch_plot_x                        / inch_fig_x,
	              inch_plot_y                        / inch_fig_y  ]

	pos_hist = [ inch_mrgn_left                          / inch_fig_x,
	             ( inch_mrgn_bottom + 2. * inch_plot_y ) / inch_fig_y,
	             inch_hist_x                             / inch_fig_x,
	             inch_hist_y                             / inch_fig_y  ]

	# Generate the plot settings specific for the user-provided "key".

	# dkey:           String name of the parameter in the data file
	# lab_name:       LaTeX text name of parameter (used to generate axis lables)
	# lab_sym:        LaTeX symbol of parameter (used to generate axis lables)
	# lab_eqn:        LaTeX equation for parameter (used to generate axis lables)
	# lab_unit:       LaTeX unit of parameter (used to generate axis lables)
	# corner:         Quadrant (1, 2, 3, or 4) for keys
	# corner_fit_var: Boolean to override placement of key with fit results
	# yscale:         Scale ('linear' or 'log') used for vertical axes (other than histogram)
	# ylim_scaled:    Range of scaled parameter axis
	# ylim_scaled:    Range of unscaled parameter axis
	# unit: scaling   factor to adjust units in data file

	if ( key == 'b' ) :
		dkey = 'bm'
		lab_name = r'Magnetic Field Strength'
		lab_sym  = r'B'
		lab_eqn  = r'= \lvert {\bf B} \rvert'
		lab_unit = r'{\rm nT}'
		corner = 3
		corner_fit_var = False
		yscale = 'log'
		ylim_scaled = [ 0.003, 150. ]
		ylim_unscaled = [ 0.008, 1050. ]
		unit = 1.
	elif ( key == 'np' ) :
		dkey = 'np'
		lab_name = r'Proton Density'
		lab_sym  = r'n_{\rm p}'
		lab_eqn  = r''
		lab_unit = r'{\rm cm}^{-3}'
		corner = 3
		corner_fit_var = False
		yscale = 'log'
		ylim_scaled = [ 0.00008, 300. ]
		ylim_unscaled = [ 0.0005, 1500. ]
		unit = 1.
	elif ( key == 'vp' ) :
		dkey = 'vp_m'
		lab_name = r'Proton Speed'
		lab_sym  = r'v_{\rm p}'
		lab_eqn  = r'= \lvert {\bf v}_{\rm p} \rvert'
		lab_unit = r'{\rm km}/{\rm s}'
		corner = 3
		corner_fit_var = False
		yscale = 'linear'
		ylim_scaled = [ 0.0, 1.7 ]
		ylim_unscaled = [ 1., 750. ]
		unit = 1.
	elif ( key == 'vpr' ) :
		dkey = 'vp_r'
		lab_name = r'Proton Radial Speed'
		lab_sym  = r'v_{{\rm p}r}'
		lab_eqn  = r''
		lab_unit = r'{\rm km}/{\rm s}'
		corner = 3
		corner_fit_var = False
		yscale = 'linear'
		ylim_scaled = [ 0.0, 1.7 ]
		ylim_unscaled = [ 1., 750. ]
		unit = 1.
	elif ( key == 'tp' ) :
		dkey = 'Tp'
		lab_name = r'Proton Temperature'
		lab_sym  = r'T_{\rm p}'
		lab_eqn  = r''
		lab_unit = r'{\rm K}'
		corner = 1
		corner_fit_var = False
		yscale = 'log'
		ylim_scaled = [ 0.01, 20. ]
		ylim_unscaled = [ 8.E2, 2.E6 ]
		unit = 1.
	elif ( key == 'va' ) :
		dkey = 'vA'
		lab_name = r'Alfv\'en Speed'
		lab_sym  = r'v_{\rm A}'
		lab_eqn  = r'= B/\sqrt{\mu_0\,m_{\rm p}\,n_{\rm p}}'
		lab_unit = r'{\rm km}/{\rm s}'
		corner = 3
		corner_fit_var = False
		yscale = 'log'
		ylim_scaled = [ 0.07, 8. ]
		ylim_unscaled = [ 8., 200. ]
		unit = 1.E-3
	elif ( key == 'na' ) :
		dkey = 'alfven_ratio'
		lab_name = r'Alfv\'en Number'
		lab_sym  = r'N_{\rm A}'
		lab_eqn  = r'= v_{\rm p}/v_{\rm A}'
		lab_unit = None
		corner = 4
		corner_fit_var = True
		yscale = 'log'
		ylim_scaled = [ 0.12, 6.0 ]
		ylim_unscaled = [ 0.9, 40. ]
		unit = 1.
	elif ( key == 'ang' ) :
		dkey = 'parker_angle'
		lab_name = r'Parker Angle'
		lab_sym  = r'\arccos\lvert\hat{\bf B}\cdot\hat{\bf r}\rvert'
		lab_eqn  = r''
		lab_unit = r'{\rm deg}'
		corner = 4
		corner_fit_var = False
		yscale = 'linear'
		ylim_scaled = [ 0., 2. ]
		ylim_unscaled = [ 0, 90. ]
		unit = 180. / pi
	elif ( key == 'loss' ) :
		dkey = 'particle_flux'
		lab_name = r'Proton Loss Rate'
		lab_sym  = r'4 \pi r^2 n_{\rm p} v_{\rm p}'
		lab_eqn  = r''
		lab_unit = r'10^{36}/{\rm s}'
		corner = 2
		corner_fit_var = False
		yscale = 'linear'
		ylim_scaled = [ 0., 3.9 ]
		ylim_unscaled = [ 0., 2. ]
		unit = 4. * pi / 1.E36
	elif ( key == 'lat' ) :
		dkey = 'heliographicLatitude'
		lab_name = r'Heliographic Latitude'
		lab_sym  = r'\lambda'
		lab_eqn  = r''
		lab_unit = r'{\rm deg}'
		corner = 3
		corner_fit_var = False
		yscale = 'linear'
		ylim_scaled = [-45.,45.]
		ylim_unscaled = [-45.,45.] 
		unit = 1.
	elif ( key == 'long' ) :
		dkey = 'heliographicLongitude'
		lab_name = r'Heliographic Longitude'
		lab_sym  = r'\lambda'
		lab_eqn  = r''
		lab_unit = r'{\rm deg}'
		corner = 3
		corner_fit_var = False
		yscale = 'linear'
		ylim_scaled = [-180.,540.]
		ylim_unscaled = [-180.,540.]
		unit = 1.
	elif ( key == 'betap' ) :
		dkey = 'proton_beta'
		lab_name = r'Proton Beta'
		lab_sym  = r'\beta_{\rm p}'
		lab_eqn  = r'= 2\,\mu_0\,n_{\rm p}\,k_{\rm B}\,T_{\rm p} / B^2'
		lab_unit = None
		corner = 3
		corner_fit_var = False
		yscale = 'log'
		ylim_scaled = [ 0.01, 8.0 ]
		ylim_unscaled = [ 0.008, 4.0 ]
		unit = 1.

	# Generate the y-axis label for the individual plot.

	ylabel_indiv = r'\rm '

	if ( lab_unit == None) :
		ylabel_indiv += ( lab_name + r', $' + lab_sym + lab_eqn + '$' )
	else :
		ylabel_indiv += ( lab_name + r', $'  + lab_sym + lab_eqn
				                     + r'$ [$' + lab_unit + r'$]' )

	# Generate the y-axis label for the composite plot.

	ylabel_comp  = r'\rm '

	if ( scaled ) :
		ylabel_comp += ( r'Scaled ' + lab_name + r', $'
		                            + lab_sym + r'/\langle '
		                            + lab_sym + r'\rangle_{\oplus}$' )
	else :
		if ( lab_unit is None ) :
			ylabel_comp += ( lab_name + r', $' + lab_sym + '$' )
		else :
			ylabel_comp += ( lab_name + r', $'  + lab_sym
			                          + r'$ [$' + lab_unit + r'$]' )

	# Generate the limits on all plot axes.

	xlim   = [ 0.04 , 120. ]
	xscale = 'log'
	xlabel = r'\rm Distance from Sun, $r$ [au]'

	hlim   = [ 10.**1.1, 10.**4.2 ]
	hscale = 'log'
	hlabel = r'\rm Intervals'

	ylim_indiv =                            ylim_unscaled
	ylim_comp  = ylim_scaled if scaled else ylim_unscaled

	# Initialize the figure.

	fig  = matplotlib.pyplot.figure( figsize=figsize )

	matplotlib.rc( 'text', usetex=True )

	# Initialize the histogram.

	fig_hist = fig.add_axes( pos_hist )

	fig_hist.set_xlim( xlim )
	fig_hist.set_ylim( hlim )

	fig_hist.set_xscale( xscale )
	fig_hist.set_yscale( hscale )

	fig_hist.set_ylabel( hlabel, size='small' )

	fig_hist.set_xticklabels( [] )

	# Initialize the individual plot.

	fig_indiv = fig.add_axes( pos_indiv )

	fig_indiv.set_xlim( xlim )
	fig_indiv.set_ylim( ylim_indiv )

	fig_indiv.set_xscale( xscale )
	fig_indiv.set_yscale( yscale )

	fig_indiv.set_ylabel( ylabel_indiv, size='small' )

	fig_indiv.set_xticklabels( [] )

	# Initialize the composite plot.

	fig_comp = fig.add_axes( pos_comp )

	fig_comp.set_xlim( xlim )
	fig_comp.set_ylim( ylim_comp )

	fig_comp.set_xscale( xscale )
	fig_comp.set_yscale( yscale )

	fig_comp.set_xlabel( xlabel     , size='small' )
	fig_comp.set_ylabel( ylabel_comp, size='small' )

	# Initialize the key for individual plot (set position and create axes).

	if   ( corner == 1 ) :
		pos_key = [ 0.33, 0.77, 0.65, 0.06 ]
	elif ( corner == 2 ) :
		pos_key = [ 0.13, 0.77, 0.65, 0.06 ]
	elif ( corner == 3 ) :
		pos_key = [ 0.13, 0.46, 0.65, 0.06 ]
	elif ( corner == 4 ) :
		pos_key = [ 0.33, 0.46, 0.65, 0.06 ]
	else :
		pos_key = [ 0.13, 0.46, 0.65, 0.06 ]

	fig_key = fig.add_axes( pos_key )

	fig_key.set_xlim( [ 0., 5. ] ) ### Changed from 5. for solar orbiter
	fig_key.set_ylim( [ 0., 3. ] )

	fig_key.set_xticks( [ ] )
	fig_key.set_yticks( [ ] )

	# Generate the solar-system object markers.  Markers and vertical lines are
    # placed at the semi-major axes of the orbits of the planets and dwarf
    # planets.

    # Note: Symbol is Eris is hacked together from a rotated and shifted
    #        version of the symbol for Mars.

	d_mercury =  0.3871   # Semi-major axes of the orbits [au]
	d_venus   =  0.7233
	d_earth   =  1.000
	d_mars    =  1.524
	d_ceres   =  2.767
	d_jupiter =  5.204
	d_saturn  =  9.583
	d_uranus  = 19.22
	d_neptune = 30.11
	d_pluto   = 39.48
	d_eris    = 67.781

	lst_d = [ d_mercury, d_venus, d_earth, d_mars, d_ceres,
	          d_jupiter, d_saturn, d_uranus, d_neptune, d_pluto, d_eris ]

	lst_lab = [ r'\starfontserif \Mercury', r'\starfontserif \Venus'  ,
	            r'\starfontserif \Terra'  , r'\starfontserif \Mars'   ,
	            r'\starfontserif \Ceres'  , r'\starfontserif \Jupiter',
	            r'\starfontserif \Saturn' , r'\starfontserif \Uranus' ,
	            r'\starfontserif \Neptune', r'\starfontserif \Pluto'  ,
	            r'\starfontserif \Mars'                                 ]

	y = ( ( inch_mrgn_bottom + 2. * inch_plot_y + inch_hist_y ) / inch_fig_y ) + 0.005

	for i in range( len( lst_d ) ) :   # For each planet or dwarf planet . . .

        # Load the semi-major axis.

		d = lst_d[i]
        
        # Set the color: black for a planet, gray for a dwarf planet.

		if ( ( d == d_ceres ) or ( d == d_pluto ) or ( d == d_eris ) ) :
			c = 'gray'
		else :
			c = 'black'

        # For Eris, apply a rotation and shift to the LaTeX symbol.

		if ( d == d_eris ) :
			shift_x  =  -1.3
			shift_y  =  0.003
			rotation = 221
		else :
			shift_x  = 0
			shift_y  = 0
			rotation = 0

        # Add in the LaTeX symbol.

		fig_hist.annotate( lst_lab[i],
		                   ( d + shift_x, y + shift_y ),
		                   xycoords=( 'data', 'figure fraction' ),
		                   color=c, size='medium',
        		           horizontalalignment='center',
		                   verticalalignment='bottom',
		                   rotation=rotation                       )

        # Add in vertical lines to the plot axes.

		fig_hist.plot(  ( d, d ), hlim      , color=c, linewidth=0.5, linestyle=':' )
		fig_indiv.plot( ( d, d ), ylim_indiv, color=c, linewidth=0.5, linestyle=':' )
		fig_comp.plot(  ( d, d ), ylim_comp , color=c, linewidth=0.5, linestyle=':' )

	# If relevant, add the unit-scale axis.

	if ( scaled ) :

		fig_comp.plot( xlim, [ 1., 1. ],
		               color='k', linewidth=0.5, linestyle=':' )

	# Load data for and populate the individual plot and histogram.

	n_sc = 12

	sc_name = [ r'$\rm PSP$'         , r'$\rm Solar~Orbiter$', r'$\rm Helios~1$'  , 
            	r'$\rm Helios~2$'    , r'$\rm Ulysses$'     , 
             	r'$\rm Mariner~10$'  , r'$\rm Cassini$'     , r'$\rm Pioneer~10$', 
              	r'$\rm Pioneer~11$'  , r'$\rm New~Horizons$', r'$\rm Voyager~1$' , 
             	r'$\rm Voyager~2$'   ]

	sc_color = [ 'tab:brown', 'g'       , 'tab:orange', 
           		 'tab:olive', 'w'       ,
                 'tab:gray' ,'tab:green', 'tab:purple', 
                 'tab:pink' ,'tab:red'  , 'tab:blue'  , 
              	 'tab:cyan'    ]

	sc_marker = [ 'd', '8', '^', 
              	  'v', 'o',  
                  'X', 'p', '<',
                  '>', '*', 's', 
                  'D'  ]

	sc_markeredgewidth = [ 0, 0  , 0,
                       	   0, 0.5,
                           0, 0  , 0,
                           0, 0  , 0, 
                           0  ]

	sc_markersize = [ 3, 3, 3, 
	                  3, 2, 
	                  3, 3, 3,
	                  3, 3, 3,
                      3]

	sc_markeredgecolor = [ None, None, None,
	                       None, 'k' , 
	                       None, None, None,
	                       None, None, None,
                           None]
	#Importing individual Data for histogram and individual plots
	p1 = 'Data_Processed/Individual/'
	p2 = 'fast_binned.hf'
	p3a = '_v2025.03.hf'
	p3b = '_v2025.03.hf'

	sc_fl = [ p1 + 'psp/psp_'              + p2 ,
              p1 + 'solo/solo_'            + p2 ,
	          p1 + 'helios1/helios1_'      + p2 ,
	          p1 + 'helios2/helios2_'      + p2 ,
	          p1 + 'ulysses/ulysses_'      + p2 ,

	          p1 + 'mariner10/mariner10_'  + p2 ,
	          p1 + 'cassini/cassini_'      + p2 ,
	          p1 + 'pioneer10/pioneer10_'  + p2 ,
	          p1 + 'pioneer11/pioneer11_'  + p2 ,
	          p1 + 'newhorizons/newhorizons_' + p2 ,
	          p1 + 'voyager1/voyager1_'     + p2 ,
	          p1 + 'voyager2/voyager2_'     + p2   ]

	for sc in range( n_sc ) :   # For each spacecraft . . .

		# Load and select the data.

		#dat = h5py.File( sc_fl[sc], 'r' )
		dat = pd.read_hdf(sc_fl[sc])
		#print(list(dat.keys()))
		dat_r = array( dat['sc_r_med'] )
		dat_k = array( dat[dkey+'_med'] )
		dat_n = array( dat[dkey+'_num']    )

		#Filter NaNs and np.infs from data
  
		tk_pre = where( ( isfinite( dat_r ) ) &
		                ( isfinite( dat_k ) ) &
		                ( isfinite( dat_n ) ) )[0]

		pre_r =        dat_r[tk_pre]
		pre_k = unit * dat_k[tk_pre]
		pre_n =        dat_n[tk_pre]
  
		#Filter for only bins with >= 25 data points
  
		tk_sel = where( pre_n >= 25 )[0]

		sel_r = pre_r[tk_sel]
		sel_k = pre_k[tk_sel]
		sel_n = pre_n[tk_sel]
		# print(sc_name[sc] + "min latitude = " + str(min(sel_k)))
		# print(sc_name[sc] + " max latitude = " + str(max(sel_k)))
		
		# Populate the individual plot.

		fig_indiv.plot( sel_r, sel_k,
		                linestyle='', color=sc_color[sc],
		                marker=sc_marker[sc],
		                markersize=sc_markersize[sc],
		                markeredgewidth=sc_markeredgewidth[sc],
		                markeredgecolor=sc_markeredgecolor[sc]  )

		# Populate the histogram.

		fig_hist.plot( sel_r, sel_n,
		               linestyle='', color=sc_color[sc],
		               marker=sc_marker[sc],
		               markersize=sc_markersize[sc],
		               markeredgewidth=sc_markeredgewidth[sc],
		               markeredgecolor=sc_markeredgecolor[sc]  )

		# Populate the key.

		x_sc = sc // 3
		y_sc = 2 - ( sc % 3 )

		opt_sc = 0. if ( x_sc == 0 ) else .1

		fig_key.plot( [ x_sc + 0.1 + opt_sc ], [ y_sc + 0.5 ],
		              linestyle='', color=sc_color[sc],
		              marker=sc_marker[sc],
		              markersize=sc_markersize[sc],
		              markeredgewidth=sc_markeredgewidth[sc],
		              markeredgecolor=sc_markeredgecolor[sc]  )

		fig_key.annotate( sc_name[sc],
		                  ( x_sc + 0.175 + opt_sc, y_sc + 0.5 ),
		                  xycoords='data',
		                  color='k', size='x-small',
       			          horizontalalignment='left',
		                  verticalalignment='center'      )

	# Load data for and populate the composite.

	p = 'New_Fits/Data_v2025.03/all_data/'

	if ( scaled ) :
		dat = pd.read_hdf( 'Data_Processed/msc/msc_fast_binned.hf' ) 
        
	else :
		dat = pd.read_hdf( 'Data_Processed/msc/msc_fast_binned.hf' )  
	dat_r   = array( dat['sc_r_med']  )
	dat_25  = array( dat[dkey+'_high'] )
	dat_50  = array( dat[dkey+'_med'] )
	dat_75  = array( dat[dkey+'_low'] )
	dat_num = array( dat[dkey+'_num']    )
 
	#Filtering for NaNs and infs
 
	tk_pre = where( ( isfinite( dat_r   ) )  &
	                ( isfinite( dat_25  ) ) &
	                ( isfinite( dat_50  ) ) & ( isfinite( dat_75  ) )  & ( isfinite( dat_num ) )   ) [0]

	pre_r   = dat_r[tk_pre]
	pre_25  = dat_25[tk_pre]
	pre_50  = dat_50[tk_pre]
	pre_75  = dat_75[tk_pre]
	pre_num = dat_num[tk_pre]
 
	tk_sel = where( ( pre_num >= 25 ) & ( pre_r <  80. ) )[0]   # Selected (for fits)
	tk_tms = where( ( pre_num >= 25 ) & ( pre_r >= 80. ) )[0]   # After termination shock

	n_sel = len( tk_sel )
	n_tms = len( tk_tms )

	sel_r   = pre_r[tk_sel]
	sel_25  = pre_25[tk_sel]
	sel_50  = pre_50[tk_sel]
	sel_75  = pre_75[tk_sel]
	sel_num = pre_num[tk_sel]

	tms_r   = pre_r[tk_tms]
	tms_25  = pre_25[tk_tms]
	tms_50  = pre_50[tk_tms]
	tms_75  = pre_75[tk_tms]
	tms_num = pre_num[tk_tms]

	if ( not scaled ) :

		sel_25 = unit * sel_25
		sel_50 = unit * sel_50
		sel_75 = unit * sel_75

		tms_25 = unit * tms_25
		tms_50 = unit * tms_50
		tms_75 = unit * tms_75

	for i in range( n_sel ) :   # For each selected bin . . .

		if ( scaled ) :
			color = 'm'
		else :
			color = 'b'

		# Plot the 10th- to 90th-percentile range.

		# fig_comp.plot( [ sel_r[ i], sel_r[ i] ],
		#                [ sel_10[i], sel_90[i] ],
		#                color=color, linestyle='-',
		#                linewidth=0.5               )

		# Plot the 25th- to 75th-percentile range.

		fig_comp.plot( [ sel_r[ i], sel_r[ i] ],
		               [ sel_25[i], sel_75[i] ],
		               color=color, linestyle='-',
		               linewidth=1.0               )

		# Plot the median value in the bin.

		fig_comp.plot( sel_r[i], sel_50[i],
		               color=color, linestyle='', marker='o',
		               markersize=3.0, markeredgewidth=0      )

	for i in range( n_tms ) :   # For each bin after the termination shock . . .

		if ( scaled ) :
			color = 'b'
		else :
			color = 'm'

		# fig_comp.plot( [ tms_r[ i], tms_r[ i] ],
		#                [ tms_10[i], tms_90[i] ],
		#                color=color, linestyle='-',
		#                linewidth=0.5               )

		fig_comp.plot( [ tms_r[ i], tms_r[ i] ],
		               [ tms_25[i], tms_75[i] ],
		               color=color, linestyle='-',
		               linewidth=1.0               )

		fig_comp.plot( tms_r[i], tms_50[i],
		               color='w', linestyle='', marker='o',
		               markersize=3.0, markeredgewidth=1.0,
		               markeredgecolor=color                )

	# Analyze the composite data and add the analysis to the composite plot.

	# Note.  The analyses are grouped by which fit function is used.

	if ( key in [ 'loss' ] ) :   # Parameters fit with no breaks

		fit = curve_fit( mod_power, sel_r, sel_50,
		                 p0=( 1., 0. ),
		                 sigma=sel_50/sqrt(sel_num)   )

		crv_r = logspace( log10( xlim[0] ), log10( xlim[1] ), 300 )
		crv_k = mod_power( crv_r, fit[0][0], fit[0][1] )

		fig_comp.plot( crv_r, crv_k,
		               color='tab:blue',
		               linestyle='-', linewidth=1.0 )

		fig_fit = fig.add_axes( [ 0.13, 0.07, 0.25, 0.03 ] )

		fig_fit.set_xlim( [ 0. , 1.  ] )
		fig_fit.set_ylim( [ 0.5, 1.5 ] )

		fig_fit.set_xticks( [] )
		fig_fit.set_yticks( [] )

		txt = r'$\alpha_1 = {:.3f} \pm {:.3f}$'.format( fit[0][1], sqrt(fit[1][1][1]) )

		fig_fit.annotate( txt,
		                  ( 0.05, 1.0 ),
		                  xycoords='data',
		                  color='tab:blue',
		                  size='medium',
       			          horizontalalignment='left',
		                  verticalalignment='center'  )

		#val_01 = mod_power(  1., fit[0][0], fit[0][1] )
		#val_40 = mod_power( 40., fit[0][0], fit[0][1] )
		
		#print( '     @ r =  1 au  ==> ' + str( val_01 ) )
		#print( '     @ r = 40 au  ==> ' + str( val_40 ) )
		#print( '     ratio (40:1) ==> ' + str( val_40 / val_01 ) )

	elif ( key in [  'np', 'vp', 'tp', 'vpr', 'va' ] ) :   # Parameters fit with one break

		if ( key in [ 'np' ] and scaled ) :	
			p0 = [ 1., 4., -2., -2. ]
		if ( key in [ 'np' ] and not scaled ) :	
			p0 = [ 1000., .5, -2., -2. ]
		elif ( key in [ 'vp', 'vpr' ] and scaled ) :	
			p0 = [ 1., 0.5, 0., 0. ]
		elif ( key in [ 'vp', 'vpr' ] and not scaled) :	
			p0 = [ 1000., .8, .07, 0. ]
		elif ( key in [ 'va' ] ) :
			p0 = [ 1., 3.0, -0.6, 0. ]
		elif ( key in [ 'na' ] ) :	
			p0 = [ 1., 3.0, 0.6, 0.2 ]
		elif ( key in [ 'betap' ] ) :
			p0 = [ 1., 8., -0.4, -0.2 ]
		elif ( key in [ 'tp' ] and scaled) :
			p0 = [ 1., 5., -0.7, -0.2 ]
		elif ( key in [ 'tp' ] and not scaled ) :
			p0 = [ 1000., 5., -0.1, -0.7]
		else :
			p0 = [ 1., 4., 0., 0. ]
   
		#Performing curve fit and creating arrays to plot fit
  
		fit = curve_fit( mod_broken, sel_r, sel_50,
		                 p0=p0,
		                 sigma=sel_50/sqrt(sel_num)   )

		crv_r  = logspace( log10( xlim[0] ), log10( xlim[1] ), 300 )
		crv_k  = mod_broken( crv_r, fit[0][0], fit[0][1], fit[0][2], fit[0][3] )
		crv_k1 = mod_broken( crv_r, fit[0][0], fit[0][1], fit[0][2], fit[0][3], force=1 )
		crv_k2 = mod_broken( crv_r, fit[0][0], fit[0][1], fit[0][2], fit[0][3], force=2 )

		fig_comp.plot( crv_r, crv_k2,
		               color='tab:blue', linestyle=':', linewidth=1.0 )

		fig_comp.plot( crv_r, crv_k1,
		               color='tab:blue', linestyle=':', linewidth=1.0 )

		fig_comp.plot( crv_r, crv_k,
		               color='tab:blue', linestyle='-', linewidth=1.0 )

		fig_comp.plot( [ fit[0][1], fit[0][1] ], ylim_comp,
		               color='tab:blue', linestyle='--', linewidth=1.0 )

		#Create fit information on figure
  
		if ( corner_fit_var ) :
			fig_fit = fig.add_axes( [ 0.13, 0.35, 0.25, 0.09 ] )
		else:
			fig_fit = fig.add_axes( [ 0.13, 0.07, 0.25, 0.09 ] )

		fig_fit.set_xlim( [ 0. , 1.  ] )
		fig_fit.set_ylim( [ 0.5, 3.5 ] )

		fig_fit.set_xticks( [] )
		fig_fit.set_yticks( [] )

		txt_a1 = r'$\alpha_1={:.3f} \pm {:.3f}$'.format( fit[0][2], sqrt(fit[1][2][2]) )
		txt_a2 = r'$\alpha_2={:.3f} \pm {:.3f}$'.format( fit[0][3], sqrt(fit[1][3][3]) )

		txt_rc_a = r'$r_a=\left({:.2f}\pm {:.2f}'.format( fit[0][1], sqrt(fit[1][1][1]) )
		txt_rc_b = r'\right)\,{\rm au}$'

		arr_txt = [ txt_rc_a + txt_rc_b, txt_a2, txt_a1 ]

		for t in range( 3 ) :

			txt = arr_txt[t]

			fig_fit.annotate( txt,
			                  ( 0.05, 1.0 + t ),
			                  xycoords='data',
			                  color='tab:blue',
			                  size='medium',
       				          horizontalalignment='left',
			                  verticalalignment='center'  )

		#val_01 = mod_broken( [ 1.], fit[0][0], fit[0][1],
		#                            fit[0][2], fit[0][3]  )[0]
		#val_40 = mod_broken( [40.], fit[0][0], fit[0][1],
		#                            fit[0][2], fit[0][3]  )[0]

		#print( '     @ r =  1 au  ==> ' + str( val_01 ) )
		#print( '     @ r = 40 au  ==> ' + str( val_40 ) )
		#print( '     ratio (40:1) ==> ' + str( val_40 / val_01 ) )

	elif ( key in [ 'b','betap', "na" ] ) :      # Parameters fit with two breaks

		bounds = ( -inf, inf )

		if ( key in [ 'va' ] ) :
			p0 = [ 1., 0.6, 5.0, -0.8, -0.4, 0. ]
		elif ( key in [ 'na' ]and scaled ) :
			p0 = [ 1., 0.4, 5.0, 0.6, 0.4, 0. ]
			bounds = ( ( 0  , 0.2,  1., -inf, -inf, -inf ),
			           ( inf, 1. , 10.,  inf,  inf,  inf )  )
		elif ( key in [ 'na' ]and not scaled ) :
			p0 = [ 1000., 0.4, 5.0, 0.5, 0.5, 0. ]
			# bounds = ( ( 0  , 0.2,  1., -inf, -inf, -inf ),
			#            ( inf, 1. , 10.,  inf,  inf,  inf )  )
		elif ( key in [ 'tp' ] and scaled) :
			p0 = [ 1., 0.2, 5., 0.0, -0.7, -0.2 ]
		elif ( key in [ 'tp' ] and not scaled) :
			p0 = [ 100000., .3, 7., -0.1, -0.7, -0.5 ]
		elif ( key in [ 'betap' ] ) :
			p0 = [ 1., 0.3, 30., 1.0, -0.5, 1.0 ]
		else :
			p0 = [ 1., 0.3, 4., -2., -1., -0.5 ]
   
		#Performing curve fit and creating arrays to plot fit
  
		fit = curve_fit( mod_broken2, sel_r, sel_50,
		                 p0=p0, bounds=bounds,
		                 sigma=sel_50/sqrt(sel_num)   )

		#%if ( key == 'na' ) :
		#	print( '    Median Alfven point:', ( 1. / fit[0][0] )**( 1. / fit[0][3] ), 'au' )

		crv_r  = logspace( log10( xlim[0] ), log10( xlim[1] ), 300 )
		crv_k  = mod_broken2( crv_r, fit[0][0], fit[0][1], fit[0][2],
		                             fit[0][3], fit[0][4], fit[0][5]  )
		crv_k1 = mod_broken2( crv_r, fit[0][0], fit[0][1], fit[0][2],
		                             fit[0][3], fit[0][4], fit[0][5], force=1  )
		crv_k2 = mod_broken2( crv_r, fit[0][0], fit[0][1], fit[0][2],
		                             fit[0][3], fit[0][4], fit[0][5], force=2  )
		crv_k3 = mod_broken2( crv_r, fit[0][0], fit[0][1], fit[0][2],
		                             fit[0][3], fit[0][4], fit[0][5], force=3  )

		fig_comp.plot( crv_r, crv_k3,
		               color='tab:blue',
		               linestyle=':', linewidth=1.0 )
		fig_comp.plot( crv_r, crv_k2,
		               color='tab:blue',
		               linestyle=':', linewidth=1.0 )
		fig_comp.plot( crv_r, crv_k1,
		               color='tab:blue',
		               linestyle=':', linewidth=1.0 )
		fig_comp.plot( crv_r, crv_k,
		               color='tab:blue',
		               linestyle='-', linewidth=1.0 )

		for i in [ 1, 2 ] :
			fig_comp.plot( [ fit[0][i], fit[0][i] ], ylim_comp,
			               color='tab:blue', linestyle='--', linewidth=1.0 )
   
		#Generating fit information for figure
		if ( corner_fit_var ) :
			fig_fit = fig.add_axes( [ 0.13, 0.35, 0.25, 0.09 ] )
		else:
			fig_fit = fig.add_axes( [ 0.13, 0.07, 0.25, 0.09 ] )
		#fig_fit = fig.add_axes( [ 0.13, 0.07, 0.25, 0.15 ] )

		fig_fit.set_xlim( [ 0. , 1.  ] )
		fig_fit.set_ylim( [ 0.5, 5.5 ] )

		fig_fit.set_xticks( [] )
		fig_fit.set_yticks( [] )

		txt_a1 = r'$\alpha_1={:.3f} \pm {:.3f}$'.format( fit[0][3], sqrt(fit[1][3][3]) )
		txt_a2 = r'$\alpha_2={:.3f} \pm {:.3f}$'.format( fit[0][4], sqrt(fit[1][4][4]) )
		txt_a3 = r'$\alpha_3={:.3f} \pm {:.3f}$'.format( fit[0][5], sqrt(fit[1][5][5]) )

		txt_ra = r'$r_a=\left({:.2f}\pm {:.2f}'.format( fit[0][1], sqrt(fit[1][1][1]) )
		txt_rb = r'$r_b=\left({:.2f}\pm {:.2f}'.format( fit[0][2], sqrt(fit[1][2][2]) )

		txt_ra += r'\right)\,{\rm au}$'
		txt_rb += r'\right)\,{\rm au}$'

		arr_txt = [ txt_rb, txt_ra, txt_a3, txt_a2, txt_a1 ]

		for t in range( 5 ) :

			txt = arr_txt[t]

			fig_fit.annotate( txt,
			                  ( 0.05, 1.0 + t ),
			                  xycoords='data',
			                  color='tab:blue',
			                  size='medium',
			                  horizontalalignment='left',
			                  verticalalignment='center'  )

		#val_01 = mod_broken2( [ 1.], fit[0][0], fit[0][1], fit[0][2],
		#                             fit[0][3], fit[0][4], fit[0][5]  )[0]
		#val_40 = mod_broken2( [40.], fit[0][0], fit[0][1], fit[0][2],
		#                             fit[0][3], fit[0][4], fit[0][5]  )[0]

		#print( '     @ r =  1 au  ==> ' + str( val_01 ) )
		#print( '     @ r = 40 au  ==> ' + str( val_40 ) )
		#print( '     ratio (40:1) ==> ' + str( val_40 / val_01 ) )

	# Output the figure.

	if ( scaled ) :
		fname = 'Figures/Fast_Powerlaw_Figs/plot_scaled_' + key + '.pdf'
		#fname = 'eps/plot_scaled_' + key + '.eps'
	else :
		fname = 'Figures/Fast_Powerlaw_Figs/plot_unscaled_' + key + '.pdf'
		#fname = 'eps/plot_unscaled_' + key + '.eps'


	matplotlib.pyplot.savefig( fname )


# Generate the figures.

arr_key    = ['b', 'np', 'vp', 'tp']
# arr_key = ["vp"]
for key in arr_key :

	print( key )

	for scaled in [ False ] : 
		plot_msc( key, scaled=scaled )
#print("lat")
#plot_msc("lat", False)