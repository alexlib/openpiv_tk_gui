#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''Parallel Processing of PIV images.'''

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

import openpiv.tools as piv_tls
import openpiv.preprocess as piv_pre
import openpiv.pyprocess as piv_prc
import openpiv.windef as piv_wdf
import openpiv.validation as piv_vld
import openpiv.filters as piv_flt
import openpiv.scaling as piv_scl
import openpiv.smoothn as piv_smt

import math
import time
import numpy as np

from openpivgui.open_piv_gui_tools import create_save_vec_fname, _round
from openpivgui.PreProcessing import gen_background, process_images


class MultiProcessing(piv_tls.Multiprocesser):
    '''Parallel processing, based on the corrresponding OpenPIV class.

    Do not run from the interactive shell or within IDLE! Details at:
    https://docs.python.org/3.6/library/multiprocessing.html#using-a-pool-of-workers

    Parameters
    ----------
    params : OpenPivParams
        A parameter object.
    '''

    def __init__(self, params):
        '''Standard initialization method.

        For separating GUI and PIV code, the output filenames are
        generated here and not in OpenPivGui. In this way, this object
        might also be useful independently from OpenPivGui.
        '''
        self.p = params 
            
        # custom image sequence with (1+[1+x]), (2+[2+x]) and ((1+[1+x]), (3+[3+x]))
        if self.p['sequence'] == '(1+2),(2+3)':
            step = 1
        else: step = 2
            
        if self.p['skip'] < 1: # setting skip to 0 will cause a naughty error
            self.p['skip'] = 1
            
        self.files_a = self.p['fnames'][0::step]
        self.files_b = self.p['fnames'][self.p['skip']::step]
        
        self.settings_a = {}
        self.settings_b = {}
        #dummy_a = {} # for debugging purposes, can be removed
        #dummy_b = {}
        
        counter = 0
        for i in range(0, len(self.p['fnames']) - self.p['skip'], step):
            #dummy_a[i] = self.p['img_preproc']['{}'.format(i)]
            self.settings_a[counter] = self.p['img_preproc']['{}'.format(i)]
            counter += 1
        
        counter = 0
        for i in range(self.p['skip'], len(self.p['fnames']), step):
            #dummy_b[i] = self.p['img_preproc']['{}'.format(i)]
            self.settings_b[counter] = self.p['img_preproc']['{}'.format(i)]
            counter += 1
                    
        #print('settings a:') # debugging, can be removed
        #for key, value in dummy_a.items():
        #    print(key)
        #print('\nsettings b:')
        #for key, value in dummy_b.items():
        #    print(key)
        
        print('Number of settings for a files: ' + str(len(self.settings_a)))
        print('Number of settings for b files: ' + str(len(self.settings_b)))
        
        # making sure files_a is the same length as files_b
        diff = len(self.files_a)-len(self.files_b) 
        if diff != 0:
            for i in range (diff):
                self.files_a.pop(len(self.files_b))
                
        print('Number of a files: ' + str(len(self.files_a)))
        print('Number of b files: ' + str(len(self.files_b)))
        
        #print(self.files_a) # for debugging purposes, can be removed
        #print(self.files_b)
        
        if self.p['swap_files']:
            self.files_a, self.files_b = self.files_b, self.files_a
            self.settings_a, self.settings_b = self.settings_b, self.settings_a
        
        self.n_files = len(self.files_a)
        self.save_fnames = []
                                 
        if self.p['evaluation_method'] == 'Direct Correlation': # disassociate the GUI selection from
                                                                # the evaluation to remove white space
            evaluation_method = 'DCC'
        else:
            evaluation_method = 'FFT'
        
        postfix = '_piv_' + evaluation_method + '_'
        for n in range(self.n_files):
            self.save_fnames.append(
                create_save_vec_fname(path=self.files_a[n],
                                      basename=self.p['vec_fname'],
                                      postfix=postfix,
                                      count=n,
                                      max_count=self.n_files))
        
        # setup widgets so the user could still use the GUI when processing
        self.parameter = {}
        for key in self.p.param:
            key_type = self.p.type[key]
            if key_type not in ['labelframe', 
                                'sub_labelframe',
                                'h-spacer', 
                                'sub_h-spacer',
                                'dummy'
                               ]:
                if 1030 < self.p.index[key] < 4000:
                    self.parameter[key] = self.p[key]
        
        # generate background if needed
        if self.parameter['background_subtract'] == True and self.parameter['background_type'] != 'minA - minB':
            self.background = gen_background(self.parameter)
        else:
            self.background = None
    
    
    def get_save_fnames(self):
        '''Return a list of result filenames.

        Returns:
            str[]: List of filenames with resulting PIV data.
        '''
        return(self.save_fnames)
        
    
    
    def get_num_frames(self):
        '''Return the amount of image pairs that will be processed.
        
        Returns:
            int: The number of image pairs to be processed'''
        return(len(self.files_a))
    
        
        
    def process(self, args):
        '''Process chain as configured in the GUI.

        Parameters
        ----------
        args : tuple
            Tuple as expected by the inherited run method:
            file_a (str) -- image file a
            file_b (str) -- image file b
            counter (int) -- index pointing to an element of the filename list
        '''
        file_a, file_b, counter = args
        frame_a = piv_tls.imread(file_a)
        frame_b = piv_tls.imread(file_b)  
        
        # delimiters placed here for safety
        delimiter = self.parameter['separator']
        if delimiter == 'tab': delimiter = '\t' 
        if delimiter == 'space': delimiter = ' '
        
        # Smoothning script borrowed from openpiv.windef
        s = self.parameter['smoothn_val1']
        def smoothn(u, s): 
            s = s
            u,dummy_u1,dummy_u2,dummy_u3=piv_smt.smoothn(u,s=s, isrobust=self.parameter['robust1'])
            return(u) 
        
        '''preprocessing'''
        print('\nPre-pocessing image pair: {}'.format(counter+1))
        if self.parameter['background_subtract'] == True and self.parameter['background_type'] == 'minA - minB':
            self.background = gen_background(self.parameter, frame_a, frame_b)
        
        crop_ROI  = self.settings_a[counter][0][0] # making the ROI crop the same for 
        crop_roiX = self.settings_a[counter][0][1]    # A and B images to avoid image shape error
        crop_roiY = self.settings_a[counter][0][2]
        frame_a = frame_a.astype(np.int32); 
        frame_a = process_images(
                self.parameter, 
                frame_a, 
                background             = self.background,
                crop_ROI               = crop_ROI,
                crop_roiX              = crop_roiX,
                crop_roiY              = crop_roiY,
                dynamic_mask           = self.settings_a[counter][0][4],
                dynamic_mask_type      = self.settings_a[counter][0][5],
                dynamic_mask_threshold = self.settings_a[counter][0][6],
                dynamic_mask_size      = self.settings_a[counter][0][7],
                invert                 = self.settings_a[counter][1][0],
                CLAHE                  = self.settings_a[counter][1][1],
                CLAHE_first            = self.settings_a[counter][1][2],
                CLAHE_auto_kernel      = self.settings_a[counter][1][3],
                CLAHE_kernel           = self.settings_a[counter][1][4],
                CLAHE_clip             = self.settings_a[counter][1][5],
                high_pass              = self.settings_a[counter][1][6],
                hp_sigma               = self.settings_a[counter][1][7],
                hp_clip                = self.settings_a[counter][1][8],
                intensity_cap          = self.settings_a[counter][1][9],
                ic_mult                = self.settings_a[counter][1][10],
                gaussian_filt          = self.settings_a[counter][1][11],
                gf_sigma               = self.settings_a[counter][1][12],
                intensity_clip         = self.settings_a[counter][1][13],
                intensity_clip_min     = self.settings_a[counter][1][14]
        )
        
        frame_b = frame_b.astype(np.int32); 
        frame_b = process_images(
                self.parameter, 
                frame_b, 
                background             = self.background,
                crop_ROI               = crop_ROI,
                crop_roiX              = crop_roiX,
                crop_roiY              = crop_roiY,
                dynamic_mask           = self.settings_b[counter][0][4],
                dynamic_mask_type      = self.settings_b[counter][0][5],
                dynamic_mask_threshold = self.settings_b[counter][0][6],
                dynamic_mask_size      = self.settings_b[counter][0][7],
                invert                 = self.settings_b[counter][1][0],
                CLAHE                  = self.settings_b[counter][1][1],
                CLAHE_first            = self.settings_b[counter][1][2],
                CLAHE_auto_kernel      = self.settings_b[counter][1][3],
                CLAHE_kernel           = self.settings_b[counter][1][4],
                CLAHE_clip             = self.settings_b[counter][1][5],
                high_pass              = self.settings_b[counter][1][6],
                hp_sigma               = self.settings_b[counter][1][7],
                hp_clip                = self.settings_b[counter][1][8],
                intensity_cap          = self.settings_b[counter][1][9],
                ic_mult                = self.settings_b[counter][1][10],
                gaussian_filt          = self.settings_b[counter][1][11],
                gf_sigma               = self.settings_b[counter][1][12],
                intensity_clip         = self.settings_b[counter][1][13],
                intensity_clip_min     = self.settings_b[counter][1][14]
        )
        
        print('Evaluating image pair: {}'.format(counter + 1))
        '''evaluation'''
        start = time.time()
        '''if self.parameter['evaluation_method'] == 'Direct Correlation':
            u, v, sig2noise = piv_prc.extended_search_area_piv(
                frame_a.astype(np.int32), frame_b.astype(np.int32),
                window_size      = self.parameter['corr_window'],
                search_area_size = self.parameter['search_area'],
                subpixel_method  = self.parameter['subpixel_method'],
                overlap          = self.parameter['overlap'],
                dt               = 1,
                sig2noise_method = self.parameter['sig2noise_method'])
            
            x, y = piv_prc.get_coordinates(
                image_size       = frame_a.shape,
                window_size      = self.parameter['corr_window'],
                overlap          = self.parameter['overlap'])
            
            if self.parameter['smoothn_each_pass'] == True:
                u = smoothn(u, s); v = smoothn(v, s) 
                print('Finished smoothning results for image pair: {}.'.format(counter+1))
            print('Finished pass 1 for image pair: {}.'.format(counter+1))
            print("search area size: "   + str(self.parameter['search_area']))
            print("window size: "   + str(self.parameter['corr_window']))
            print('overlap: '       + str(self.parameter['overlap']), '\n')
            
            # make sure vectors are the same direction as FFT WinDef 
            v *= -1
            
            # needed for processing information
            overlap_percent = self.parameter['overlap'] / self.parameter['corr_window']

            # no masks were created, so create a filler
            mask = np.full_like(u, 0)
            
            sizeX = self.parameter['search_area']

            
        else:'''
        if 5 != 1:
            # evaluation first pass
            passes = 1
            if self.parameter['custom_windowing']: # setup custom windowing if selected
                corr_window_0   = self.parameter['corr_window_1']
                overlap_0       = self.parameter['overlap_1']
                for i in range(2, 8):
                    if self.parameter['pass_%1d' % i]:
                        passes += 1
                    else:
                        break;
                        
            else:
                passes = self.parameter['coarse_factor']
                if self.parameter['grid_refinement'] == 'all passes' and self.parameter['coarse_factor'] != 1: 
                    corr_window_0 = self.parameter['corr_window'] * 2**(self.parameter['coarse_factor'] - 1)
                    overlap_0     = self.parameter['overlap'] * 2**(self.parameter['coarse_factor'] - 1)

                # Refine all passes after first when there are more than 1 pass.    
                elif self.parameter['grid_refinement'] == '2nd pass on' and self.parameter['coarse_factor'] != 1: 
                    corr_window_0 = self.parameter['corr_window'] * 2**(self.parameter['coarse_factor'] - 2)
                    overlap_0     = self.parameter['overlap'] * 2**(self.parameter['coarse_factor'] - 2)

                # If >>none<< is selected or something goes wrong, the window size would remain the same.    
                else:
                    corr_window_0 = self.parameter['corr_window']
                    overlap_0     = self.parameter['overlap']
            overlap_percent = overlap_0 / corr_window_0 
            sizeX = corr_window_0
                
            x, y, u, v, sig2noise = piv_wdf.first_pass(
                frame_a.astype(np.int32), frame_b.astype(np.int32),
                corr_window_0,
                overlap_0,
                passes, # number of passes
                do_sig2noise       = True,
                #correlation_method = self.parameter['corr_method'], # 'circular' or 'linear'
                subpixel_method    = self.parameter['subpixel_method'])

            # validating first pass
            u, v, mask = piv_vld.local_median_val(
                u, v,
                u_threshold = self.parameter['fp_local_med'],
                v_threshold = self.parameter['fp_local_med'],
                size        = self.parameter['fp_local_med_size'])  

            if self.parameter['fp_vld_global_threshold']:
                u, v, Mask = piv_vld.global_val(
                    u, v,
                    u_thresholds=(self.parameter['fp_MinU'], self.parameter['fp_MaxU']),
                    v_thresholds=(self.parameter['fp_MinV'], self.parameter['fp_MaxV']))
                mask += Mask # consolidate effects of mask

            u, v = piv_flt.replace_outliers(
                    u, v,
                    method      = self.parameter['adv_repl_method'],
                    max_iter    = self.parameter['adv_repl_iter'],
                    kernel_size = self.parameter['adv_repl_kernel'])
            print('Filtered first pass result of image pair: {}.'.format(counter+1)) 

            # smoothning  before deformation if 'each pass' is selected
            if self.parameter['smoothn_each_pass']:
                if self.parameter['smoothn_first_more']:
                    s *=2
                u = smoothn(u, s); v = smoothn(v, s) 
                print('Smoothned pass 1 for image pair: {}.'.format(counter+1))
                s = self.parameter['smoothn_val1']

            print('Finished pass 1 for image pair: {}.'.format(counter+1))
            print("window size: "   + str(corr_window_0))
            print('overlap: '       + str(overlap_0), '\n')  

            # evaluation of all other passes
            if passes != 1:
                iterations = passes - 1
                for i in range(2, passes + 1):
                    # setting up the windowing of each pass
                    if self.parameter['custom_windowing']:
                        corr_window = self.parameter['corr_window_%1d' % i]
                        overlap = int(corr_window * overlap_percent)
                        
                    else:
                        if self.parameter['grid_refinement'] == 'all passes' or self.parameter['grid_refinement'] == '2nd pass on':
                            corr_window = self.parameter['corr_window'] * 2**(iterations - 1)
                            overlap     = self.parameter['overlap'] * 2**(iterations - 1) 

                        else:
                            corr_window = self.parameter['corr_window']
                            overlap     = self.parameter['overlap']
                    sizeX = corr_window
                    
                    x, y, u, v, sig2noise, mask = piv_wdf.multipass_img_deform(
                        frame_a.astype(np.int32), frame_b.astype(np.int32),
                        corr_window,
                        overlap,
                        passes, # number of iterations
                        i, # current iteration
                        x, y, u, v,
                        #correlation_method   = self.parameter['corr_method'],
                        subpixel_method      = self.parameter['subpixel_method'],
                        do_sig2noise         = True,
                        sig2noise_mask       = self.parameter['adv_s2n_mask'],
                        MinMaxU              = (self.parameter['sp_MinU'], self.parameter['sp_MaxU']),
                        MinMaxV              = (self.parameter['sp_MinV'], self.parameter['sp_MaxV']),
                        std_threshold        = self.parameter['sp_global_std_threshold'],
                        median_threshold     = self.parameter['sp_local_med_threshold'],
                        median_size          = self.parameter['sp_local_med_size'],
                        filter_method        = self.parameter['adv_repl_method'],
                        max_filter_iteration = self.parameter['adv_repl_iter'],
                        filter_kernel_size   = self.parameter['adv_repl_kernel'],
                        interpolation_order  = self.parameter['adv_interpolation_order'])       

                    # smoothning each individual pass if 'each pass' is selected
                    if self.parameter['smoothn_each_pass']:
                        u = smoothn(u, s); v = smoothn(v, s) 
                        print('Smoothned pass {} for image pair: {}.'.format(i,counter+1))

                    print('Finished pass {} for image pair: {}.'.format(i,counter+1))
                    print("window size: "   + str(corr_window))
                    print('overlap: '       + str(overlap), '\n')
                    iterations -= 1

        if self.parameter['origin'] == 'top left':
            pass
        
        elif self.parameter['origin'] == 'top left (flipped)':
            u = np.flipud(u)
            v = np.flipud(v)
            v *= -1
            
        else:
            v *= -1

                
        # scaling
        u = u/self.parameter['dt']
        v = v/self.parameter['dt']
        x,y,u,v=piv_scl.uniform(x,y,u,v, scaling_factor=self.parameter['scale']) 
        end = time.time() 
        
        # save data to file.
        out = np.vstack([m.ravel() for m in [x, y, u, v, mask, sig2noise]])
        np.savetxt(self.save_fnames[counter], out.T, fmt='%8.4f', delimiter=delimiter)
        print('Processed image pair: {}.'.format(counter+1))
        
        sizeY = sizeX
        sizeX = ((int(frame_a.shape[0] - sizeX) // (sizeX - (sizeX * overlap_percent))) + 1)
        sizeY = ((int(frame_a.shape[1] - sizeY) // (sizeY - (sizeY * overlap_percent))) + 1)
        
        time_per_vec = _round((((end - start) * 1000) / ((sizeX * sizeY) - 1)), 3)
        
        print('Process time: {} second(s)'.format((_round((end - start), 3))))
        print('Amount of vectors: {}'.format(int((sizeX * sizeY) - 1)))
        print('Time per vector: {} millisecond(s)'.format(time_per_vec))