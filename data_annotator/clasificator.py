import cv2
import numpy as np
from data_annotator import LBP, RF_clasificator


def ClasificarRF(img, path):
    rows,cols,dim1 = img.shape
    W=128
    H=128
    x=0
    y=0
    ini=(x,y)
    fin=(W,H)
    color=(255,0,0)
    response=0
    clf = RF_clasificator.RTrees()
    clf.load(path)

    for i in range(0,cols,128):
        for j in range(0,rows,128):
             ini=(i,j)
             fin=(W+i,H+j)
             #cv2.rectangle(img,ini,fin, color, 5)
             sample=img[j:j+H,i:i+W]
             rows,cols,depth=sample.shape
             cv2.imshow('sample', sample)
             cv2.waitKey(0)
             if (rows==128 & cols==128):
                 sample=LBP.LBPfeature(sample)
                 sample= sample.ravel()
                 TestSample=sample.astype(np.float32)
                 TestSample=TestSample.reshape(1,-1)
                 response =clf.predict(TestSample)
             
             #RFClasificator(sample,rtree)
             print (response)


def Test_RF(sample,path):
    clf = RF_clasificator.RTrees()
    clf.load(path)
    sample=LBP.LBPfeature(sample)
    sample= sample.ravel()
    TestSample=sample.astype(np.float32)
    TestSample=TestSample.reshape(1,-1)
    response=clf.predict(TestSample)
    return response
