import cv2
import numpy as np
import os


class StatModel(object):
    '''parent class - starting point to add abstraction'''    
    def load(self, fn):
        self.model=cv2.ml.SVM_load(fn)
    def save(self, fn):
        self.model.save(fn)


class SVM(StatModel):
    #'wrapper for OpenCV SimpleVectorMachine algorithm'
    def __init__(self):
        self.model = cv2.ml_SVM.create()

    def train(self, samples, responses):
        #setting algorithm parameters
        params = dict( kernel_type = cv2.ml.SVM_LINEAR, 
                       svm_type = cv2.ml.SVM_C_SVC,
                       C = 1 )

        #train_data=cv2.ml.TrainData_create(samples=samples,layout=cv2.ml.ROW_SAMPLE, responses=responses)
        self.model.train(samples,cv2.ml.ROW_SAMPLE, responses)

    def predict(self, sample):
        response=0
        
       # return np.float32( [self.model.predict(s) for s in sample])
        response=self.model.predict(sample)

        return  response
