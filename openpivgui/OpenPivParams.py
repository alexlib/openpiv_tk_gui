#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''A class for simple parameter handling.

This class is also used as a basis for automated widget creation
by OpenPivGui.
'''

__licence__ = '''
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

__email__= 'vennemann@fh-muenster.de'

mask = [[]]

settings = {}

example_user_function='''
filelistbox = self.get_filelistbox()
properties  = self.p
import pandas as pd

def textbox(title='Title', text='Hello!'):
    from tkinter.scrolledtext import ScrolledText
    from tkinter.constants import END
    frame = tk.Tk()
    frame.title(title)
    textarea = ScrolledText(frame, height=10, width=80)
    textarea.insert(END, text)
    textarea.pack(fill='x', side='left', expand=True)
    textarea.focus()
    frame.mainloop()

try:
    index = filelistbox.curselection()[0]
except IndexError:
    messagebox.showerror(
        title="No vector file selected.",
        message="Please select a vector file " +
                "in the file list and run again."
    )
else:
    f = properties['fnames'][index]
    names=('x','y','v_x','v_y','var')
    df = pd.read_csv(f, sep='\t', header=None, names=names)
    print(df.describe())
    textbox(title='Statistics of {}'.format(f),
            text=df.describe()
    )
'''

import json
import os


class OpenPivParams():
    '''A class for convenient parameter handling.

    Widgets are automatically created based on the content of the
    variables in the dictionary OpenPivParams.default.

    The entries in OpenPivParams.default are assumed to follow this
    pattern:

    (str) key:
        [(int) index, 
         (str) type, 
         value,
         (tuple) hints,
         (str) label,
         (str) help]

    The index is used for sorting and grouping, because Python 
    dictionaries below version 3.7 do not preserve their order. A 
    corresponding input widged ist chosen based on the type string:
    
        None:                    no widget, no variable, but a rider
        boolean:                 checkbox
        str[]:                   listbox
        text:                    text area
        other (float, int, str): entry (if hints not None: option menu)
    
    A label is placed next to each input widget. The help string is
    displayed as a tooltip.

    The parameter value is directly accessible via indexing the base
    variable name. For example, if your OpenPivParams object variable
    name is »my_settings«, you can access a value by typing:

    my_settings[key] 
    
    This is a shortcut for my_settings.param[key]. To access other 
    fields, use my_settings.label[key], my_settings.help[key] and so on.
    '''

    def __init__(self):
        # hard coded location of the parameter file in the home dir:
        self.params_fname = os.path.expanduser('~' + os.sep + \
                                               'open_piv_gui.json')
        # grouping and sorting based on an index:
        self.GENERAL    = 1000
        self.PREPROC    = 2000
        self.PIVPROC    = 3000
        self.VALIDATION = 6000
        self.POSTPROC   = 7000
        self.PLOTTING   = 8000
        self.LOGGING    = 9000
        self.USER       = 10000
        # remember the current file filter
        # (one of the comma separated values in ['navi_pattern']):
        self.navi_position = 0
        # these are the default parameters, basis for widget creation:
        self.default = {
            #########################################################
            # Place additional variables in the following sections. #
            # Widgets are created automatically. Don't care about   #
            # saving and restoring - new variables are included     #
            # automatically.                                        #
            #########################################################
            # general
            'general':
                [1000,
                 None,        # type None: This will create a rider.
                 None,
                 None,
                 'General',
                 None],
            
            'fnames':
                [1010,        # index, here: group GENERAL
                 'str[]',     # type
                 [],          # value
                 None,        # hint (used for option menu, if not None)
                 'filenames', # label
                 None],       # help (tooltip)
            
            'images':
                [1012, 'dummy', [], 
                 None,
                 None,
                 None],
            
            'img_preproc':
                [1013, 'dummy', settings, 
                 None,
                 None,
                 None],
            
            'general_frame':
                [1015, 'labelframe', None, 
                 None,
                 'General settings',
                 None],
            
            'warnings':
                [1020, 'bool', 'True', None,
                 'Enable popup warnings',
                 'Enable popup warning messages (recommended).'],
            
            'pop_up_info':
                [1025, 'bool', 'True', None,
                 'Enable popup info',
                 'Enable popup information messages.'],
            
            'multicore_frame':
                [1030, 'sub_labelframe', None, 
                 None,
                 'multicore settings',
                 None],
            
            'manual_select_cores':
                [1035, 'sub_bool', 'True', None,
                 'manually select cores',
                 'Mannualy select cores. If not seected, all available cores will be used.'],
            
            'cores':
                [1040, 'sub_int', 1, 
                 (1,2,3,4,5,6,7,8),
                 'number of cores',
                 'Select amount of cores to be used for PIV evaluations.'],
            
            'frequencing_sub_frame':
                [1045, 'sub_labelframe', None, 
                 None,
                 'image frequencing',
                 None],
            
            'sequence':
                [1050, 'sub', '(1+2),(2+3)', 
                 ('(1+2),(2+3)','(1+2),(3+4)'),
                 'sequence order',
                 'Select sequence order for evaluation.'],
            
            'skip':
                [1051, 'sub_int', 1, 
                 None,
                 'jump',
                 'Select sequence order jump for evaluation.' +
                 '\nEx: (1+(1+x)),(2+(2+x))'],
            
            'filters_sub_frame':
                [1100, 'sub_labelframe', None, 
                 None,
                 'listbox filters',
                 None],
            
            'navi_pattern':
                [1110, 'sub',
                 'png$, tif$, tiff$, TIF$, bmp$, pgm$, jpg$, jpeg$' +
                 'vec$, '
                 'DCC_[0-9]+\.vec$, ' +
                 'FFT_[0-9]+\.vec$, ' +
                 'subvel\.vec$, ' +
                 'sig2noise\.vec$, ' +
                 'std_thrhld\.vec$, ' +
                 'med_thrhld\.vec$, ' +
                 'glob_thrhld\.vec$, ' +
                 'repl\.vec$, ' +
                 'smthn\.vec$ ',
                 None,
                 'navigation pattern',
                 'Regular expression patterns for filtering the files ' +
                 'in the current directory. Use the back and forward ' +
                 'buttons to apply a different filter.'],
            
            'pandas_sub_frame':
                [1200, 'sub_labelframe', None, 
                 None,
                 'Pandas',
                 None],
            
            'load_settings':
                [1210, 'sub_bool', True, None,
                 'settings for using pandas',
                 'Individual settings ' +
                 'for loading files using pandas.'],
            
            'skiprows':
                [1211, 'sub', '0', None,
                 'skip rows', 
                 'Number of rows skipped at the beginning of the file.'],
            
            'decimal':
                [1212, 'sub', '.', None,
                 'decimal separator', 
                 'Decimal separator for floating point numbers.'],
            
            'sep':
                [1213, 'sub', 'tab', (',', 
                                      ';', 
                                      'space', 
                                      'tab'),
                 'column separator',
                 'Column separator.'],
            
            'header':
                [1214, 'sub_bool', False, None,
                 'read header', 
                 'Read header. ' + 
                 'If chosen, first line will be interpreted as the header'],
            
            'header_names':
                [1215, 'sub', 'x,y,vx,vy,mask,sig2noise', None,
                 'specify header names',
                 'Specify comma separated list of column names.' +
                 'Example: x,y,vx,vy,mask,sig2noise'],
            
            'save_sub_frame':
                [1300, 'sub_labelframe', None, 
                 None,
                 'PIV save settings',
                 None],
            
            'vec_fname':
                [1310, 'sub', 'vec', None,
                 'base output filename',
                 'Filename for vector output. A number and an acronym ' +
                 'that indicates the process history are added ' +
                 'automatically.'],
            
            'separator':
                [1320, 'sub', 'tab', (',',
                                      ';', 
                                      'space', 
                                      'tab'),
                 'delimiter',
                 'Delimiter.'],
            
            'image_plotting_sub_frame':
                [1500, 'sub_labelframe', None, 
                 None,
                 'image plotting',
                 None],
            
            'matplot_intensity':
                [1510, 'sub_int', 255, None,
                 'reference intensity',
                 'Define a reference intensity for the plotting of images.'],
            
            #'expand_figure': # failed test. Needs more testing.
            #    [1520, 'sub_bool', False, None,
            #     'expand figure',
            #     'Expand the image so that it fills more/most of the plotting canvas (requires restart to deactivate).'],
            
            
            
            # preprocessing
            'preproc':
                [2000, None, None, None,
                 'Preprocessing',
                 None],
            
            'exclusions_frame':
                [2005, 'labelframe', None, None,
                 'Exclusions',
                 None],
            
            'mask':
                [2007, 'dummy', mask, None,
                 'object masking',
                 None],
            
            'crop_ROI':
                [2010, 'bool', 'False', None,
                 'crop region of interest',
                 'Crop region of interest. Allows images with different sizes to ' +
                 'have a uniform size after cropping.'],
            
            'crop_roi-xminmax':
                [2011, 'str', '200,800', None,
                 'x min/max',
                 "Define left/right side of region of interest by 'min,max'."],
            
            'crop_roi-yminmax':
                [2012, 'str', '200,800', None,
                 'y min/max',
                 "Define top/bottom of region of interest by 'min,max.'"],
            
            'dynamic_mask_spacer':
                [2015, 'h-spacer', None, 
                 None,
                 None,
                 None],
            
            'dynamic_mask':
                [2020, 'bool', 'False', None,
                 'dynamic masking',
                 'Dynamic masking for masking of images. \n' +
                 'Warning: This is still in testing and is not recommended for use.'],
            
            'dynamic_mask_type':
                [2021, 'str', 'edge', 
                 ('edge', 'intensity'),
                 'mask type',
                 'Defining dynamic mask type.'],
            
            'dynamic_mask_threshold':
                [2022, 'float', 0.01, None,
                 'mask threshold',
                 'Defining threshold of dynamic mask.'],
            
            'dynamic_mask_size':
                [2023, 'int', 7, None,
                 'mask filter size',
                 'Defining size of the masks.'],
            
            'apply-spacer':
                [2025, 'h-spacer', None, 
                 None,
                 None,
                 None],
            
            'preproc-filtering':
                [2100, None, None, None,
                 'Filtering',
                 None],
            
            'preprocess_frame':
                [2105, 'labelframe', None, 
                 None,
                 'Filters',
                 None],
            
            'filter_process':
                [2110, 'label', None, None,
                 'All images are normalized to [0,1] float, \npreprocessed, and resized to user defined value.',
                 None],
            
            'Invert_spacer':
                [2115, 'h-spacer', None, 
                 None,
                 None,
                 None],
            
            'invert':
                [2120, 'bool', 'False', None,
                 'invert image',
                 'Invert image (see skimage invert()).'],
            
            'background_spacer':
                [2125, 'h-spacer', None, 
                 None,
                 None,
                 None],
            
            'background_subtract':
                [2130, 'bool', 'False', None,
                 'subtract background',
                 'Subtract background via local sliding windows.'],
            
            'background_type':
                [2131, 'str', 'global mean', ('global mean', 
                                              'min of A and B'),
                 'background algorithm',
                 'The algorithm used to generate the background which is subtracted from the piv images.'],
            
            'starting_frame':
                [2132, 'int', 0, None,
                 'starting image',
                 'Defining the starting image of the background subtraction.'],
            
            'ending_frame':
                [2133, 'int', 5, None,
                 'ending image',
                 'Defining the ending image of the background subtraction.'],
            
            'CLAHE_spacer':
                [2135, 'h-spacer', None, 
                 None,
                 None,
                 None],
            
            'CLAHE':
                [2140, 'bool', 'True', None,
                 'CLAHE filter',
                 'Contrast Limited Adaptive Histogram Equalization filter (see skimage adapthist()).'],
            
            'CLAHE_first':
                [2141, 'bool', 'False', None,
                 'perform CLAHE before high pass',
                 'Perform CLAHE filter before Gaussian high pass filters.'],
            
            'CLAHE_auto_kernel':
                [2142, 'bool', True, None,
                 'automatic kernel sizing',
                 'Have the kernel automatically sized to 1/8 width and height of the image.'],
            
            'CLAHE_kernel':
                [2143, 'int', 20, None,
                 'kernel size',
                 'Defining the size of the kernel for CLAHE.'],
            
            'CLAHE_clip':
                [2143, 'int', 1, None,
                 'contrast',
                 'The amount of contrast to be applied to the image with higher the number, the more contrast. ' +
                 '(ints 1-1000)'],
            
            'high_pass_filter_spacer':
                [2145, 'h-spacer', None, 
                 None,
                 None,
                 None],
            
            'high_pass_filter':
                [2150, 'bool', 'False', None,
                 'Gaussian high pass filter',
                 'A simple subtracted Gaussian high pass filter.'],
            
            'hp_sigma':
                [2151, 'int', 5, None,
                 'sigma',
                 'Defining the sigma size of the subtracted gaussian filter in the ' + 
                 'high pass filter (positive ints only).'],
            
            'hp_clip':
                [2152, 'bool', 'True', None,
                 'clip at zero',
                 'Set all values less than zero to zero.'],
            
            'intensity_threshold_spacer':
                [2165, 'h-spacer', None, 
                 None,
                 None,
                 None],
            
            'intensity_cap_filter':
                [2170, 'bool', 'False', None,
                 'intensity capping',
                 'Simple global intesity cap filter. Masked pixels are set to the mean pixel intensity.'],
            
            'ic_mult':
                [2171, 'float', 2, None,
                 'std multiplication',
                 'Multiply the standard deviation of the pixel intensities to get a higher cap value.'],
            
            'Gaussian_lp_spacer':
                [2175, 'h-spacer', None, 
                 None,
                 None,
                 None],
            
            'gaussian_filter':
                [2180, 'bool', 'False', None,
                 'Gaussian filter',
                 'Standard Gaussian blurring filter (see scipy gaussian_filter()).'],
            
            'gf_sigma':
                [2181, 'int', 10, None,
                 'sigma',
                 'Defining the sigma size for gaussian blur filter.'],
            
            'intensity_clip_spacer':
                [2185, 'h-spacer', None, 
                 None,
                 None,
                 None],
            
            'intensity_clip':
                [2190, 'bool', 'False', None,
                 'intensity clip',
                 'Any intensity less than the threshold is set to zero.'],
            
            'intensity_clip_min':
                [2191, 'int', 20, None,
                 'min intensity',
                 'Any intensity less than the threshold is set to zero with respect to ' +
                 'the resized image inntensities.'],
            
            'img_int_resize_spacer':
                [2195, 'h-spacer', None, 
                 None,
                 None,
                 None],
            
            'img_int_resize':
                [2197, 'int', 255, None,
                 'resize intensity',
                 'Resize the max image intensity to \na user defined value.'],
            
            'apply-spacer2':
                [2199, 'h-spacer', None, 
                 None,
                 None,
                 None],
            
            
            # processing
            'piv':
                [3000, None, None, None,
                 'PIV',
                 None],
            
            'piv_frame':
                [3005, 'labelframe', None, 
                 None,
                 'Algorithms/Calibration',
                 None],
            
            'evaluation_method':
                [3010, 'string', 'FFT WinDef',
                 ('Direct Correlation', 'FFT WinDef'),
                 'evaluation method',
                 'Direct Correlation: ' +
                 'Direct correlation with extended size of the ' +
                 'search area. \n' +
                 'FFT WinDef: ' +
                 'Fast Fourier Transforms with window deformation ' +
                 '(recommended). \n'
                 'Important: FFT WinDef evaluates images with origin at top left.' +
                 'Direct correlation evaluates images with origin at bottom left.'],
            
            'corr_method':
                [3020, 'str', 'circular', ('circular', 
                                           'linear'),
                 'correlation method',
                 'Correlation method. Circular is no padding and' + 
                 'linear is zero padding (applies to Windef).'],
            
            'subpixel_method':
                [3030, 'str', 'gaussian', ('centroid', 
                                           'gaussian', 
                                           'parabolic'),
                 'subpixel method',
                 'Fit function for determining the subpixel position ' +
                 'of the correlation peak.'],
            
            'sig2noise_method':
                [3040, 'string', 'peak2peak', ('peak2peak',
                                               'peak2mean'),
                 'signal2noise calc. method',
                 'Calculation method for the signal to noise ratio.'],
            
            'adv_s2n_mask':
                [3045, 'int', 2, None,
                 'signal to noise mask',
                 'the half size of the region around the first correlation peak to ignore for ' +
                 'finding the second peak. Only used if sig2noise method = \'peak2peak\' '],
            
            'adv_interpolation_order':
                [3050, 'int', 3, (0,1,2,3,4,5),
                 'interpolation order',
                 'Interpolation oder of the window deformation. \n' +
                 '»0« yields zero order nearest interpolation \n' +
                 '»1« yields first order linear interpolation \n'
                 '»2« yields second order quadratic interpolation \n'
                 'and so on...'],
            
            'calibration_spacer':
                [3055, 'h-spacer', None, 
                 None,
                 None,
                 None],
            
            'dt':
                [3060, 'float', 1.0, None,
                 'dt',
                 'Interframing time in seconds.'],
            
            'scale':
                [3070, 'float', 1.0, None,
                 'scale',
                 'Interframing scaling in pix/m \n' +
                 'Important: The scaling ratio is applied before dt, so when getting the proper scale, ' +
                 'set »dt« to 1'],
            
            'flip_spacer':
                [3075, 'h-spacer', None, 
                 None,
                 None,
                 None],
            
            'origin':
                [3080, 'str', 'top left', ('top left',
                                           'bottom left'),
                 'origin (0,0): ',
                 'Set the origin to either top or bottom left.'],
            
            'swap_files_spacer':
                [3085, 'h-spacer', None, 
                 None,
                 None,
                 None],
            
            'swap_files':
                [3090, 'bool', 'False', None,
                 'swap A/B files',
                 'Swap A/B files when analyzing.'],
            
            
            
            'windowing':
                [3100, None, None, None,
                 'Widnowing',
                 None],
            
            'window_frame':
                [3105, 'labelframe', None, 
                 None,
                 'Windowing',
                 None],
            
            'search_area':
                [3110, 'int', 64, (16,32,64,128,256),
                 'search area [px]',
                 'Size of square search area in pixel for ' +
                 'Single-pass DCC method.'], 
            
            'corr_window':
                [3120, 'int', 32, (8,16,32,64,128),
                 'interrogation window [px]',
                 'Size of the final interrogation windows in pixels.'],
            
            'overlap':
                [3130, 'int', 16, (4,8,16,32,64),
                 'overlap [px]',
                 'Size of the final overlap in pixels.'],
            
            'coarse_factor':
                [3140, 'int', 3, (1, 2, 3, 4, 5),
                 'number of passes',
                 'Example: A window size of 16 and a number of refinement steps ' +
                 'of 3 gives an window size of 64×64 in the first pass, 32×32 in ' +
                 'the second pass and 16×16 pixel in the final pass. (Applies ' +
                 'to FFT WinDef methods only.)'],
            
            'grid_refinement':
                [3150, 'str', 'all passes', ('all passes', 
                                             '2nd pass on', 
                                             'none'),
                 'grid refinement',
                 'Refine the interregationg grid every PIV pass when performing multipass FFT. \n' +
                 '»all passes« refines all passes. \n'
                 '»2nd pass on« refines second pass on.'],
            
            'sub_window_frame':
                [3200, 'sub_labelframe', None, 
                 None,
                 'custom windowing',
                 None],
            
            'custom_windowing':
                [3205, 'sub_bool', False, None,
                 'custom windowing',
                 'Enable custom windowing for more advanced techniques.'],
            
            'pass_1_spacer':
                [3210, 'sub_h-spacer', None, 
                 None,
                 None,
                 None],
            
            'corr_window_1':
                [3220, 'sub_int', 256, None,
                 'interrogation window [px]',
                 'Interrogation window for the first pass.'],
            
            'overlap_1':
                [3230, 'sub_int', 128, None,
                 'overlap [px]',
                 'Size of the overlap of the first pass in pixels. The overlap will then be ' +
                 'calculated for the following passes.'],
            
            'pass_2_spacer':
                [3235, 'sub_h-spacer', None, 
                 None,
                 None,
                 None],
            
            'pass_2':
                [3237, 'sub_bool', False, None,
                 'second pass',
                 'Enable a second pass in the FFT window deformation evaluation.'],
            
            'corr_window_2':
                [3240, 'sub_int', 128, None,
                 'interrogation window [px]',
                 'Interrogation window for the second pass.'],
            
            'pass_3_spacer':
                [3245, 'sub_h-spacer', None, 
                 None,
                 None,
                 None],
            
            'pass_3':
                [3247, 'sub_bool', False, None,
                 'third pass',
                 'Enable a third pass in the FFT window deformation evaluation.'],
            
            'corr_window_3':
                [3250, 'sub_int', 64, None,
                 'interrogation window [px]',
                 'Interrogation window for the third pass.'],
            
            'pass_4_spacer':
                [3255, 'sub_h-spacer', None, 
                 None,
                 None,
                 None],
            
            'pass_4':
                [3257, 'sub_bool', False, None,
                 'fourth pass',
                 'Enable a fourth pass in the FFT window deformation evaluation.'],
            
            'corr_window_4':
                [3260, 'sub_int', 32, None,
                 'interrogation window [px]',
                 'Interrogation window for the fourth pass.'],
            
            'pass_5_spacer':
                [3265, 'sub_h-spacer', None, 
                 None,
                 None,
                 None],
            
            'pass_5':
                [3267, 'sub_bool', False, None,
                 'fifth pass',
                 'Enable a fifth pass in the FFT window deformation evaluation.'],
            
            'corr_window_5':
                [3270, 'sub_int', 16, None,
                 'interrogation window [px]',
                 'Interrogation window for the fifth pass.'],
            
            'pass_6_spacer':
                [3275, 'sub_h-spacer', None, 
                 None,
                 None,
                 None],
            
            'pass_6':
                [3277, 'sub_bool', False, None,
                 'sixth pass',
                 'Enable a sixth pass in the FFT window deformation evaluation.'],
            
            'corr_window_6':
                [3280, 'sub_int', 16, None,
                 'interrogation window [px]',
                 'Interrogation window for the sixth pass.'],
            
            'pass_7_spacer':
                [3285, 'sub_h-spacer', None, 
                 None,
                 None,
                 None],
            
            'pass_7':
                [3287, 'sub_bool', False, None,
                 'seventh pass',
                 'Enable a seventh pass in the FFT window deformation evaluation.'],
            
            'corr_window_7':
                [3290, 'sub_int', 16, None,
                 'interrogation window [px]',
                 'Interrogation window for the seventh pass.'],
            
            # individual pass validations
            'validation':
                [3300, None, None, None,
                 'Validation',
                 None],
            
            'validation_frame':
                [3305, 'labelframe', None, 
                 None,
                 'Validation',
                 None],
            
            'validation_process':
                [3306, 'label', None, None,
                 'All results are processed before calibration, \nso the units entered will be pix/dt (unscaled).',
                 None],
            
            'piv_sub_frame1':
                [3307, 'sub_labelframe', None, 
                 None,
                 'first pass validation',
                 None],
            
            'fp_local_med':
                [3310, 'sub_float', 1.2, None,
                 'local median threshold',
                 'Discard vector, if the absolute difference with ' +
                 'the local median is greater than the threshold. '],
            
            'fp_local_med_size':
                [3311, 'sub_int', 1, None,
                 'local median kernel',
                 'Local median filter kernel size.'], 
            
            'globa_thr_spacer':
                [3325, 'sub_h-spacer', None, 
                 None,
                 None,
                 None],
            
            'fp_vld_global_threshold':
                [3330, 'sub_bool', False, None,
                 'global threshold validation',
                 'Validate first pass based on set global ' +
                 'thresholds.'],
            
            'fp_MinU':
                [3331, 'sub_float', -100.0, None,
                 'min u',
                 'Minimum U allowable component.'], 
            
            'fp_MaxU':
                [3332, 'sub_float', 100.0, None,
                 'max u',
                 'Maximum U allowable component.'],
            
            'fp_MinV':
                [3333, 'sub_float', -100.0, None,
                 'min v',
                 'Minimum V allowable component.'],
            
            'fp_MaxV':
                [3334, 'sub_float', 100.0, None,
                 'max v',
                 'Maximum V allowable component.'],
            
            'piv_sub_frame2':
                [3340, 'sub_labelframe', None, 
                 None,
                 'other pass validations',
                 None],
            
            'sp_local_med_threshold':
                [3350, 'sub_float', 1.2, None,
                 'local median threshold',
                 'Discard vector, if the absolute difference with ' +
                 'the local median is greater than the threshold. '], 
            
            'sp_local_med_size':
                [3351, 'sub_int', 1, None,
                 'local median kernel',
                 'Local median filter kernel size.'], 
            
            'glob_std_spacer':
                [3355, 'sub_h-spacer', None, 
                 None,
                 None,
                 None],
            
            'sp_global_std_threshold':
                [3360, 'sub_float', 8.0, None,
                 'std threshold',
                 'Remove vectors, if the the sum of the squared ' +
                 'vector components is larger than the threshold ' +
                 'times the standard deviation of the flow field.'],
            
            'glob_thr_spacer':
                [3365, 'sub_h-spacer', None, 
                 None,
                 None,
                 None],
            
            'sp_MinU':
                [3370, 'sub_float', -100.0, None,
                 'min u',
                 'Minimum U allowable component.'], 
            
            'sp_MaxU':
                [3371, 'sub_float', 100.0, None,
                 'max u',
                 'Maximum U allowable component.'],
            
            'sp_MinV':
                [3372, 'sub_float', -100.0, None,
                 'min v',
                 'Minimum V allowable component.'],
            
            'sp_MaxV':
                [3373, 'sub_float', 100.0, None,
                 'max v',
                 'Maximum V allowable component.'],
            
            'piv_sub_frame3':
                [3375, 'sub_labelframe', None, 
                 None,
                 'interpolation',
                 None],
            
            'adv_repl_method':
                [3380, 'sub', 'localmean', ('localmean',
                                            'disk', 
                                            'distance'),
                 'replacement method',
                 'Each NaN element is replaced by a weighed average' +
                 'of neighbours. Localmean uses a square kernel, ' +
                 'disk a uniform circular kernel, and distance a ' +
                 'kernel with a weight that is proportional to the ' +
                 'distance.'],
            
            'adv_repl_iter':
                [3381, 'sub_int', 10, None,
                 'number of iterations',
                 'If there are adjacent NaN elements, iterative ' +
                 'replacement is needed.'],
            
            'adv_repl_kernel':
                [3382, 'sub_int', 2, None,
                 'kernel size',
                 'Diameter of the NaN interpolation kernel.'],
            
            'piv_sub_frame4':
                [3385, 'sub_labelframe', None, 
                 None,
                 'Smoothen',
                 None],
            
            'smoothn_each_pass':
                [3390, 'sub_bool', True, None,
                 'smoothen each pass',
                 'Smoothen each pass using openpiv.smoothn.'],
            
            'smoothn_first_more':
                [3391, 'sub_bool', True, None,
                 'double first pass strength',
                 'Double the smoothing strength on the first pass.'],
            
            'robust1':
                [3392, 'sub_bool', False, None,
                 'smoothen robust',
                 'Activate robust in smoothen (minimizes influence of outlying data).'],
           
            'smoothn_val1':
                [3393, 'sub_float', 0.8, None,
                 'smoothing strength',
                 'Strength of smoothen script. Higher scalar number produces ' +
                  'more smoothed data.'],
            
            
            
            
            # validation/postprocessing
            'vld':
                [6000, None, None, None,
                 'PostProcessing',
                 None],
            
            'vld_frame':
                [6005, 'labelframe', None, 
                 None,
                 'Postprocess',
                 None],
            
            'sub_vel_background':
                [6010, 'bool', False, None,
                 'remove background velocity',
                 'Subtract the background velocity from the PIV data.'],
            
            'set_mean':
                [6011, 'bool', True, None,
                 'set to mean',
                 'Set the u and v variable to the mean for each result.'],
            
            'u-vel':
                [6012, 'float', 0, None,
                 'u velocity',
                 'The scalar to be subtracted from the u-component.'],
            
            'v-vel':
                [6013, 'float', 0, None,
                 'v velocity',
                 'The scalar to be subtracted from the v-component.'],
            
            's2n_spacer':
                [6015, 'h-spacer', None, 
                 None,
                 None,
                 None],
            
            'vld_sig2noise':
                [6020, 'bool', False, None,
                 'signal to noise ratio validation',
                 'Validate the data based on the signal to nose ratio '+
                 'of the cross correlation.'],
            
            'sig2noise_threshold':
                [6021, 'float', 1.5, None,
                 's2n threshold',
                 'Threshold for filtering based on signal to noise ' +
                 'ratio.'],
            
            'global_std_spacer':
                [6025, 'h-spacer', None, 
                 None,
                 None,
                 None],
            
            'vld_global_std':
                [6030, 'bool', True, None,
                 'standard deviation validation',
                 'Validate the data based on a multiple of the '+
                 'standard deviation.'],
            
            'global_std_threshold':
                [6031, 'float', 5.0, None,
                 'std threshold',
                 'Remove vectors, if the the sum of the squared ' +
                 'vector components is larger than the threshold ' +
                 'times the standard deviation of the flow field.'],
            
            'local_med_spacer':
                [6035, 'h-spacer', None, 
                 None,
                 None,
                 None],
            
            'vld_local_med':
                [6040, 'bool', True, None,
                 'local median validation',
                 'Validate the data based on a local median ' +
                 'threshold.'],
            
            'local_median_threshold':
                [6041, 'float', 1.2, None,
                 'local median threshold',
                 'Discard vector, if the absolute difference with ' +
                 'the local median is greater than the threshold. '], 
            
            'global_thrsh_spacer':
                [6045, 'h-spacer', None, 
                 None,
                 None,
                 None],
            
            'vld_global_thr':
                [6050, 'bool', False, None,
                 'global threshold validation',
                 'Validate the data based on set global ' +
                 'thresholds.'],
            
            'MinU':
                [6051, 'float', -30.0, None,
                 'min u',
                 'Minimum U allowable component.'], 
            
            'MaxU':
                [6052, 'float', 30.0, None,
                 'max u',
                 'Maximum U allowable component.'],
            
            'MinV':
                [6053, 'float', -30.0, None,
                 'min v',
                 'Minimum V allowable component.'],
            
            'MaxV':
                [6054, 'float', 30.0, None,
                 'max v',
                 'Maximum V allowable component.'],
            
            'repl_spacer':
                [6055, 'h-spacer', None, 
                 None,
                 None,
                 None],
            
            'repl':
                [7010, 'bool', True, None,
                 'replace outliers',
                 'Replace outliers.'],
            
            'repl_method':
                [7020, 'str', 'localmean', ('localmean', 
                                            'disk', 
                                            'distance'),
                 'replacement method',
                 'Each NaN element is replaced by a weighed average' +
                 'of neighbours. Localmean uses a square kernel, ' +
                 'disk a uniform circular kernel, and distance a ' +
                 'kernel with a weight that is proportional to the ' +
                 'distance.'],
            
            'repl_iter':
                [7030, 'int', 10, None,
                 'number of iterations',
                 'If there are adjacent NaN elements, iterative ' +
                 'replacement is needed.'],
            
            'repl_kernel':
                [7040, 'int', 2, None,
                 'kernel size',
                 'Diameter of the weighting kernel.'],
            
            'horizontal_spacer15':
                [7045, 'h-spacer', None, 
                 None,
                 None,
                 None],
            
            'smoothn':
                [7050, 'bool', False, None,
                 'smoothn results',
                 'Smoothn post processed results using openpiv.smoothn.'],
            
            'robust':
                [7070, 'bool', False, None,
                 'smoothn robust',
                 'Activate robust in smoothn (minimizes influence of outlying data).'],
            
            'smoothn_val':
                [7080, 'float', 1.0, None,
                 'smoothning strength',
                 'Strength of smoothn script. Higher scalar number produces ' +
                  'more smoothned data.'],
            
            'average_spacer':
                [7085, 'h-spacer', None, 
                 None,
                 None,
                 None],
            
            'average_results':
                [7090, 'bool', False, None,
                 'average results',
                 'Average all results in selected directory. Results in a single file with averaged results.'],
            
            'delimiter_spacer':
                [7095, 'h-spacer', None, 
                 None,
                 None,
                 None],
            
            'delimiter':
                [7100, 'str', 'tab', (',', 
                                      ';', 
                                      'space', 
                                      'tab'),
                 'delimiter',
                 'Delimiter.'],
            
            'postproc_spacer':
                [7105, 'h-spacer', None, 
                 None,
                 None,
                 None],
               
            
            
            # plotting
            'plt':
                [8000, None, None, None,
                 'Plot',
                 None],
            
            'plt_frame':
                [8005, 'labelframe', None, 
                 None,
                 'Plotting',
                 None],
            
            'plot_type':
                [8010, 'str', 'contour + vectors', ('vectors', 
                                          'contour', 
                                          'contour + vectors', 
                                          'streamlines', 
                                          'histogram', 
                                          'profiles', 
                                          'scatter', 
                                          'line',
                                          #'bar', Failed testing (for Windows 10), simply locks GUI.
                                          'density'),
                 'plot type',
                 'Select how to plot velocity data.'],
                
            'plot_title':
                [8020, 'str', 'Title', None, 
                 'diagram title', 
                 'diagram title.'],
                
            #plot_derivatives':
            #   [8075, 'str', 'None', ('None', 'Vorticity'),
            #   'plot derivatives',
            #   'Plot derivatives of the vector map (for vectors, countours, and streamlines only).'],
            
            'streamline_density':
                [8095, 'str', '0.5, 1', None, 
                 'streamline density',
                 'streamline density. Can be one value (e.g. 1) or a couple' +
                 ' of values for a range (e.g. 0.5, 1).'],
                
            'integrate_dir':
                [8097, 'str', 'both', ('both', 
                                       'forward',
                                       'backward'),
                 'streamline direction',
                 'Integrate the streamline in forward, backward or both ' +
                 'directions. default is both.'],
            
            
            'statistics_frame':
                [8105, 'labelframe', None, 
                 None,
                 'Statistics',
                 None],
            
            'u_data':
                [8110, 'str', 'vx', None, 
                 'column name for u-velocity component',
                 'column name for the u-velocity component.' +
                 ' If unknown watch labbook entry.'],
            
            'v_data':
                [8120, 'str', 'vy', None, 
                 'column name for v-veloctiy component',
                 'column name for v-velocity component.' +
                 ' If unknown watch labbook entry.' +
                 ' For histogram only the v-velocity component is needed.'],
                
            'plot_scaling': 
                [8130, 'str', 'None', ('None', 
                                       'logx', 
                                       'logy', 
                                       'loglog'),
                 'axis scaling', 'scales the axes. logarithm scaling x-axis' +
                 ' --> logx; logarithm scaling y-axis --> logy; ' +
                 'logarithm scaling both axes --> loglog.'],
            
            'histogram_type':
                [8140, 'str', 'bar', ('bar', 
                                      'barstacked', 
                                      'step',
                                      'stepfilled'), 
                 'histogram type', 
                 'Choose histogram type. Only available for histogram' + 
                 'plot.'],
            
            'histogram_quantity':
                [8150, 'str', 'v_x', ('v', 
                                      'v_x',
                                      'v_y'),
                 'histogram quantity',
                 'The absolute value of the velocity (v) or its x- ' +
                 'or y-component (v_x or v_y).'], 
            
            'histogram_bins':
                [8160, 'int', 20, None,
                 'histogram number of bins',
                 'Number of bins (bars) in the histogram.'],
            
            'profiles_orientation':
                [8170, 'str', 'vertical', ('vertical', 
                                           'horizontal'),
                 'profiles orientation',
                 'Plot v_y over x (horizontal) or v_x over y (vertical).'],
            
            'profiles_jump':
                [8180, 'int', 1, None, 
                 'profile density', 
                 'The amount of profile lines (minimum of 1).'],
            
            'plot_xlim':
                [8190, 'str', '', None, 
                 'limits for the x-axis', 
                 'For implementation use (lower_limit, upper_limit).'],
            
            'plot_ylim':
                [8200, 'str', '', None, 
                 'limits for the y-axis',
                 'For implementation use (lower_limit, upper_limit).'],
            
            
            
            'modify_plot_appearance':
                [8500, None, None, None,
                 'Plot',
                 None],
            
            'modify_plot_frame':
                [8505, 'labelframe', None, 
                 None,
                 'Modify Plot Appearance',
                 None],
            
            'vector_subframe':
                [8505, 'sub_labelframe', None, 
                 None,
                 'Vectors',
                 None],
            
            'vec_scale':
                [8510, 'sub_int', 100, None,
                 'vector scaling',
                 'Velocity as a fraction of the plot width, e.g.: ' +
                 'm/s per plot width. Large values result in shorter ' +
                 'vectors.'],
            
            'vec_width':
                [8520, 'sub_float', 0.0025, None,
                 'vector line width',
                 'Line width as a fraction of the plot width.'],
            
            'invalid_color':
                [8530, 'dummy', 'red', None,
                 None,
                 'Choose the color of the vectors'],
            
            'valid_color':
                [8540, 'dummy', 'black', None,
                 None,
                 'Choose the color of the vectors'],
            
            'invert_yaxis': # now applies to contours, so it is placed in the main labelframe
                [8550, 'bool', True, None,
                 'invert y-axis',
                 'Define the top left corner as the origin ' +
                 'of the vector plot coordinate sytem, ' +
                 'as it is common practice in image processing.'],
            
            'derived_subframe':
                [8555, 'sub_labelframe', None, 
                 None,
                 'Derived Parameters',
                 None],
            
            'color_map':
                [8560, 'sub', 'viridis', ('viridis',
                                          'jet',
                                          'short rainbow',
                                          'long rainbow',
                                          'seismic',
                                          'autumn',
                                          'binary'),
                 'Color map', 'Color map for streamline- and contour-plot.'],
            
            'extend_cbar':
                [8570, 'sub_bool', True, None,
                'extend colorbar',
                'Extend the top and bottom of the colorbar to accept out of range values.'],
            
            'velocity_color':
                [8575, 'sub', 'v', ('vx', 
                                    'vy', 
                                    'v'),
                 'set colorbar to: ',
                 'Set colorbar to velocity components.'],
            
            'color_levels':
                [8580, 'sub', '30', None, 'number of color levels',
                 'Select the number of color levels for contour plot.'],
            
            'vmin':
                [8590, 'sub', '', None, 
                 'min velocity for colormap',
                 'minimum velocity for colormap (contour plot).'],
            
            'vmax':
                [8595, 'sub', '', None, 
                 'max velocity for colormap',
                 'maximum velocity for colormap (contour plot).'],
            
            'statistics_subframe':
                [8600, 'sub_labelframe', None, 
                 None,
                 'Statistics',
                 None],
            
            'plot_grid':
                [8610, 'sub_bool', True, None, 
                 'grid', 
                 'adds a grid to the diagram.'],
                
            'plot_legend':
                [8620, 'sub_bool', True, None,
                 'legend', 
                 'adds a legend to the diagram.'],
            
            # lab-book
            'lab_book':
                [9000, None, None, None,
                 'Lab-Book',
                 None],
            
            'lab_book_frame':
                [9005, 'labelframe', None, 
                 None,
                 'Lab Book',
                 None],
            
            'lab_book_content':
                [9010, 'text',
                 '',
                 None,
                 None,
                 None],
            
            'data_information':
                [9020, 'bool', False, None, 
                 'log column information', 
                 'shows column names, if you choose a file at the ' + 
                 'right side.'],
            
            
            
            # user-function
            'user_func':
                [10000, None, None, None,
                 'User-Function',
                 None],
            
            'user_func_def':
                [10010, 'text',
                 example_user_function,
                 None,
                 None,
                 None]
        }
        
        
        # splitting the dictionary for more convenient access
        self.index = dict(zip(
            self.default.keys(),
            [val[0] for val in self.default.values()]))
        self.type = dict(zip(
            self.default.keys(),
            [val[1] for val in self.default.values()]))
        self.param = dict(zip(
            self.default.keys(),
            [val[2] for val in self.default.values()]))
        self.hint = dict(zip(
            self.default.keys(),
            [val[3] for val in self.default.values()]))
        self.label = dict(zip(
            self.default.keys(),
            [val[4] for val in self.default.values()]))
        self.help = dict(zip(
            self.default.keys(),
            [val[5] for val in self.default.values()]))

    def __getitem__(self, key):
        return(self.param[key])

    def __setitem__(self, key, value):
        self.param[key] = value

    def load_settings(self, fname):
        '''Read parameters from a JSON file.
        
        Args: 
            fname (str): Path of the settings file in JSON format.

        Reads only parameter values. Content of the fields index, 
        type, hint, label and help are always read from the default
        dictionary. The default dictionary may contain more entries
        than the JSON file (ensuring backwards compatibility).
        '''
        try:
            f = open(fname, 'r')
            p = json.load(f)
            f.close()
        except:
            print('File not found: ' + fname)
        else:
            for key in self.param:
                if key in p:
                    self.param[key] = p[key]

    def dump_settings(self, fname):
        '''Dump parameter values to a JSON file.

        Args:
            fname (str): A filename.
        
        Only the parameter values are saved. Other data like
        index, hint, label and help should only be defined in the
        default dictionary in this source code.'''
        try:
            f = open(fname, 'w')
            json.dump(self.param, f)
            f.close()
        except:
            print('Unable to save settings: ' + fname)



    def generate_parameter_documentation(self, group=None):
        '''Return parameter labels and help as reStructuredText def list.

        Parameters
        ----------
        group : int
            Parameter group.
            (e.g. OpenPivParams.PIVPROC)

        Returns
        -------
        str : A reStructuredText definition list for documentation.
        '''
        s = ''
        for key in self.default:
            if (group < self.index[key] < group+1000
                and self.type[key] not in [
                    'labelframe', 
                    'sub_labelframe', 
                    'h-spacer', 
                    'sub_h-spacer',
                    'dummy'
                    ]):
                s = s + str(self.label[key]) + '\n' + \
                '    ' + str.replace(str(self.help[key]), '\n', '\n    ') + '\n\n'
        return(s)
