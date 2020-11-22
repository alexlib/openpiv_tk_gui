#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''Post Processing for OpenPIVGui.'''

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
import numpy as np
import openpiv.tools as piv_tls
import openpiv.preprocess as piv_pre
from scipy.ndimage.filters import gaussian_filter
from skimage import exposure, filters, util

'''Pre Processing chain for image arrays.

Parameters
----------
params : openpivgui.OpenPivParams
    Parameter object.
'''
def gen_background(parameter, image1 = None, image2 = None):
    images = parameter['fnames'][parameter['starting_frame'] : parameter['ending_frame']]
    # This needs more testing. It creates artifacts in the correlation for images not selected in the background.
    if parameter['background_type'] == 'global min':
        background = piv_tls.imread(parameter['fnames'][parameter['starting_frame']])
        maximum = background.max()
        background = background / maximum
        background *= 255
        for im in images: 
            if im == parameter['fnames'][parameter['starting_frame']]: # the original image is already included, so skip it in the for loop
                pass
            else:
                image = piv_tls.imread(im)
                maximum = image.max()
                image = image / maximum
                image *= 255
                background = np.min(np.array([background, image]), axis = 0)
        return(background)
    
    elif parameter['background_type'] == 'global mean':
        images = parameter['fnames'][parameter['starting_frame'] : parameter['ending_frame']]
        background = piv_tls.imread(parameter['fnames'][parameter['starting_frame']])
        maximum = background.max()
        background = background / maximum
        background *= 255
        for im in images: 
            if im == parameter['fnames'][parameter['starting_frame']]: # the original image is already included, so skip it in the for loop
                pass
            else:
                image = piv_tls.imread(im)
                maximum = image.max()
                image = image / maximum
                image *= 255
                background += image
        background /= (parameter['ending_frame'] - parameter['starting_frame'])
        return(background)
    
    elif parameter['background_type'] == 'minA - minB':
        # normalize image1 and image2 intensities to [0,255]
        maximum1 = image1.max(); maximum2 = image2.max()
        image1 = image1 / maximum1; image2 = image2 / maximum2
        image1 *= 255; image2 *= 255
        background = np.min(np.array([image2, image1]), axis = 0)
        return(background)
        
    else:
        print('Background algorithm not implemented.')
    
    
    
def process_images(parameter, 
                   img,  
                   background = None,
                   crop_ROI = False,
                   crop_roiX = '200,800',
                   crop_roiY = '200,800',
                   dynamic_mask = False,
                   dynamic_mask_type = 'edge',
                   dynamic_mask_threshold = 0.1,
                   dynamic_mask_size = 7,
                   invert = False,
                   CLAHE = True,
                   CLAHE_first = True,
                   CLAHE_auto_kernel = True,
                   CLAHE_kernel = 20,
                   CLAHE_clip = 1,
                   high_pass = False,
                   hp_sigma = 5,
                   hp_clip = True,
                   intensity_cap = True,
                   ic_mult = 2,
                   gaussian_filt = False,
                   gf_sigma = 2,
                   intensity_clip = False,
                   intensity_clip_min = 15
                   ):
    '''Starting the pre-processing chain'''
    # normalize image to [0, 1] float
    maximum = img.max()
    img = img / maximum
    resize = parameter['img_int_resize']

    if invert == True:
        img = util.invert(img)
        
    if parameter['background_subtract']:
        try:
            img *= 255
            img -= background
            img[img<0] = 0 # values less than zero are set to zero
            img = img / 255
        except:
            print('Could not subtract background. Ignoring background subtraction.')
            
    if crop_ROI == True: # ROI crop done after background subtraction to avoid image shape issues
        crop_x = (int(list(crop_roiX.split(','))[0]),
                     int(list(crop_roiX.split(','))[1]))
        crop_y = (int(list(crop_roiY.split(','))[0]),
                     int(list(crop_roiY.split(','))[1]))
        img = img[crop_y[0]:crop_y[1],crop_x[0]:crop_x[1]]    

    if dynamic_mask == True:    
        img = piv_pre.dynamic_masking(img,
                                      method      = dynamic_mask_type,
                                      filter_size = dynamic_mask_size,
                                      threshold   = dynamic_mask_threshold)
        
    if CLAHE == True or high_pass == True:
        if CLAHE_first == True:    
            if CLAHE == True:
                if CLAHE_auto_kernel == True:
                    kernel = None
                else:
                    kernel = CLAHE_kernel
                    
                clip_limit = CLAHE_clip * 0.001
                img = exposure.equalize_adapthist(img, 
                                                  kernel_size = kernel, 
                                                  clip_limit  = clip_limit,
                                                  nbins       = 256)

            if high_pass == True:
                low_pass = gaussian_filter(img, sigma = hp_sigma)
                img -= low_pass
                
                if hp_clip:
                    img[img < 0] = 0
        
        else:
            if high_pass == True:
                low_pass = gaussian_filter(img, sigma = hp_sigma)
                img -= low_pass
                
                if hp_clip:
                    img[img < 0] = 0
                
            if CLAHE == True:
                if CLAHE_auto_kernel == True:
                    kernel = None
                else:
                    kernel = CLAHE_kernel
                    
                clip_limit = CLAHE_clip * 0.001
                img = exposure.equalize_adapthist(img, 
                                                  kernel_size = kernel, 
                                                  clip_limit  = clip_limit,
                                                  nbins       = 256)
                
    # simple intensity capping
    if intensity_cap == True:
        upper_limit = np.mean(img) + ic_mult * img.std()
        img[img > upper_limit] = upper_limit
    
    # simple intensity clipping
    if intensity_clip == True:
        img *= resize
        lower_limit = intensity_clip_min
        img[img < lower_limit] = 0
        img /= resize
        
    if gaussian_filt == True:
        img = gaussian_filter(img, sigma = gf_sigma)

    return(img * resize)