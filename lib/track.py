"""
Functions in this file
    getthresholdedimg(im)
    track_data(frame)
    optimize_mouse_center(old_center,new_center)
    filter_fingers(data)
    find_center(centers)
"""
import cv
from basic import dummy_object
import config
import numpy as N
def getthresholdedimg(im,color_range):
    imghsv=cv.CreateImage(cv.GetSize(im),8,3)
    cv.CvtColor(im,imghsv,cv.CV_BGR2HSV)				# Convert image from RGB to HSV
    imgthreshold=cv.CreateImage(cv.GetSize(im),8,1)
    cv.InRangeS(imghsv,color_range['MIN'],color_range['MAX'],imgthreshold)	# Select a range of yellow color
    return imgthreshold

def track_data(frame,color_range):#this gets all data and the color_image from a given frame
    color_image = frame
    cv.Flip(color_image,color_image,1)
    cv.Smooth(color_image, color_image, cv.CV_GAUSSIAN, 3, 0)
    imgyellowthresh=getthresholdedimg(color_image,color_range)
    cv.Erode(imgyellowthresh,imgyellowthresh,None,3)
    cv.Dilate(imgyellowthresh,imgyellowthresh,None,10)
    storage = cv.CreateMemStorage(0)
    contour = cv.FindContours(imgyellowthresh, storage, cv.CV_RETR_CCOMP, cv.CV_CHAIN_APPROX_SIMPLE)
    centers=[]
    areas=[]
    #This is the new part here. ie Use of cv.BoundingRect()
    #print list(contour)
    while contour:
        # Draw bounding rectangles
        bound_rect = cv.BoundingRect(list(contour))
        #cv.DrawContours(color_image,contour,cv.CV_RGB(255,0,0),cv.CV_RGB(0,0,255),0,2,8)
        contour = contour.h_next()
        # for more details about cv.BoundingRect,see documentation
        pt1 = (bound_rect[0], bound_rect[1])
        pt2 = (bound_rect[0] + bound_rect[2], bound_rect[1] + bound_rect[3])
        cv.Rectangle(color_image, pt1, pt2, cv.CV_RGB(255,0,0), 1)

        #this will have center of each box
        centers.append(
            (cv.Round((pt1[0]+pt2[0])/2),cv.Round((pt1[1]+pt2[1])/2))
        )
        #Compute areas
        areas.append(pow((pt1[0]-pt2[0]),2))

    #Computing center
    center=find_center(centers)
    #Add to data
    data=dummy_object()
    data.center=center
    data.centers=centers
    data.areas=areas
    data.contour=contour
    return color_image,data

def optimize_mouse_center(old_center,new_center):#returns optimized centers based on old centers
    try:
        if(new_center and (old_center!=new_center)):
            return (new_center['x']*config.RESOLUTION[0]*config.SCALE_FACTOR)/640,(new_center['y']*config.RESOLUTION[1]*config.SCALE_FACTOR)/480
    except:
        pass
    return None,None

def filter_contour(data):#returns with adjusted center
    try:
        index=data.areas.index(max(data.areas))
        data.center={'x':data.centers[index][0],'y':data.centers[index][1]}
    except:
        data.center=find_center(data.centers)
    return data

def find_center(centers):#given centers this will find a center
    try:
        center={'x':0,'y':0}
        for c in centers:
            center['x']+=c[0]
            center['y']+=c[1]
        center['x']=center['x']/len(centers)
        center['y']=center['y']/len(centers)
        return center
    except:
        center=None
def ipl2array(im):
    depth2dtype = {
        cv.IPL_DEPTH_8U: 'uint8',
        cv.IPL_DEPTH_8S: 'int8',
        cv.IPL_DEPTH_16U: 'uint16',
        cv.IPL_DEPTH_16S: 'int16',
        cv.IPL_DEPTH_32S: 'int32',
        cv.IPL_DEPTH_32F: 'float32',
        cv.IPL_DEPTH_64F: 'float64',
    }

    a = N.fromstring(im.tostring(),
                     dtype=depth2dtype[im.depth],
                     count=im.width * im.height * im.nChannels)
    a.shape = (im.height, im.width, im.nChannels)
    return a
