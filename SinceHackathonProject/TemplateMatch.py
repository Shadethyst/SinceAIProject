import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt

class TemplateMatch(object):

 
    img_rgb = cv.imread('pageB.png')
    assert img_rgb is not None, "file could not be read, check with os.path.exists()"
    img_gray = cv.cvtColor(img_rgb, cv.COLOR_BGR2GRAY)
    template = cv.imread('tempb.PNG', cv.IMREAD_GRAYSCALE)
    assert template is not None, "file could not be read, check with os.path.exists()"
    w, h = template.shape[::-1]
     
    res = cv.matchTemplate(img_gray,template,cv.TM_SQDIFF_NORMED)
    threshold = 0.9
    loc = np.where( res >= threshold)
    for pt in zip(*loc[::-1]):
        cv.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)
    
    cv.imwrite('res.png',img_rgb)




