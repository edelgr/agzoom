import cv2
import numpy as np
import os



class StatModel(object):
    '''parent class - starting point to add abstraction'''    
    def load(self, fn):
        #self.model=cv2.ml.RTrees_load(fn)
        self.model=self.model.load(fn)
    def save(self, fn):
        self.model.save(fn)

class RTrees(StatModel):
    def __init__(self):
        self.model = cv2.ml.RTrees_create()

    def train(self, samples, responses):
        self.model.setMaxDepth(20)
        self.model.setMinSampleCount(2)
        self.model.setRegressionAccuracy(0.0)
        self.model.setUseSurrogates(0)
        self.model.setMaxCategories(2)
        self.model.setCalculateVarImportance(0)
        self.model.setActiveVarCount(1000)
        self.model.train(samples, cv2.ml.ROW_SAMPLE, responses.astype(int))

    def predict(self, samples):
        _ret, resp = self.model.predict(samples)
        return resp.ravel()
