# -*- coding: utf-8 -*-
from classifier.label_keyword_classifier import *
from classifier.label_hmm_classifier import *
from classifier.label_crf_classifier import *
# import numpy as np
# import pandas as pd

class segmentation():
    def __init__(self, method):
        self.mapping_dic = {
            "0": "basic_info",
            "1": "education",
            "2": "work_experience",
            "3": "social_experience",
            "4": "project_experience",
            "5": "training_experience",
            "-9": "non-related"
        }
        assert (method in ["hmm", "crf", "keyword"])
        self.method = method
        if self.method == "keyword":
            self.classifier = label_keyword_classifier()
        elif self.method == "hmm":
            self.classifier = label_hmm_classifier()
        elif self.method == "crf":
            self.classifier = label_crf_classifier()

    def train(self, training_data):
        self.classifier.train(training_data)
        self.classifier.save_classifier()

    def load_classifier(self):
        self.classifier.load_classifier()

    def predict(self, test_data):
        predicted_result = self.classifier.predict(test_data)
        return predicted_result
