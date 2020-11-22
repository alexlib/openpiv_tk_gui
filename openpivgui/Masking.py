import numpy as np
import matplotlib.pyplot as plt

from openpiv import tools
from PIL import Image, ImageDraw, ImageOps
    
def gen_mask_image(image, mask_list, invert = False):
    height = image.shape[0]
    width = image.shape[1]
    img = Image.new('L', (width, height))
    for i in range(len(mask_list)):
        ImageDraw.Draw(img).polygon(mask_list[i], outline=1, fill=1)
    if invert:
        img = ImageOps.invert(img)
        mask = np.array(img)
        mask = mask / mask.max()
        mask[mask < 0.999] = 0
    else:
        mask = np.array(img)
    return(mask)