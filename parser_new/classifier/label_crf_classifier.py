import os
import re
import sys
import nltk
import pickle
import numpy as np
import jieba
from random import shuffle
from sklearn.metrics import accuracy_score, confusion_matrix
from pycrfsuite import ItemSequence, Trainer, Tagger
import pandas as pd
import generate_feature as gf

class label_crf_classifier(object):
    """Conditional Random Field model"""
    def __init__(self, stopword_path = "data/stop_words.txt"):
        self.stoplist = set(open(stopword_path).read().decode("utf8","ignore").split("\n"))

    def preprocess(self, training_data):
        self.training_df = training_data[training_data["section_label"] != ""]
        self.training_df['crf_feature'] = self.training_df['crf_feature'].map(lambda x: [y for y in x if y not in self.stoplist])
        self.x = self.training_df.groupby("resume_id")["crf_feature"].apply(list)
        self.y = self.training_df.groupby("resume_id")["section_label"].apply(list)

    def train(self, training_data, classifier_path = "classifier/cache/label_crf_classifier", c1 = 0, c2 = 10, period = 300, minfreq = 5):
        self.preprocess(training_data)
        train = Trainer()
        for i1, i in enumerate(self.x):
            train.append(ItemSequence(i), self.y[i1])
        params = {
            "c1": c1,
            "c2": c2,
            "period": period,
            "feature.minfreq": minfreq,
            "max_iterations": 1000
            # "calibration.eta": 0.05,
            # "calibration_samples": 400,
        }
        # train.select(algorithm = "l2sgd")
        train.set_params(params)
        train.train(classifier_path)
        self.tagger = Tagger()
        self.tagger.open(classifier_path)

    def save_classifier(self, classifier_path = "classifier/cache/label_crf_classifier"):
        pass

    def load_classifier(self, classifier_path = "classifier/cache/label_crf_classifier"):
        self.tagger = Tagger()
        self.tagger.open(classifier_path)

    def predict(self, test_data):
        """Input: x should be a list of strings"""
        result = self.tagger.tag(ItemSequence(test_data["crf_feature"]))
        test_data["section_label"] = result
        return test_data

    # def score(self, training_data, classifier_path="classifier/cache/label_crf_classifier", portion=0.8, c1=0, c2=10, period=300, minfreq=10):
    #     # split resume_id
    #     resume_ids = np.unique([resume['resume_id'] for resume in training_data])
    #     length = len(resume_ids)
    #     shuffle(resume_ids)
    #     train_ids = resume_ids[:int(length*portion)]
    #     test_ids = resume_ids[int(length*portion):]

    #     train_df = [resume for resume in training_data if resume['resume_id'] in train_ids]
    #     test_df = [resume for resume in training_data if resume['resume_id'] in test_ids]

    #     # train model on train_ids
    #     self.train(train_df, classifier_path=classifier_path, c1=c1, c2=c2, period=period, minfreq=minfreq)
    #     test_pred = self.predict_all(test_df)
    #     train_pred = self.predict_all(train_df)

    #     # print out result
    #     return train_pred, test_pred

# if __name__ == "__main__":
#     data = MongoRetriveData()
#     resumes = data.get_data_mongo()
#     # pickle.dump(resumes, open('./resume_data.pkl', 'wb'))
#     # resumes = pickle.load(open('./resume_data.pkl', 'rb'))
#     stopword_path = './stopword.txt'
#     model_path = './model.txt'
#     resume_data = resumes
#     clf = Crf(stopword_path, model_path, resume_data)
#     clf.CleanData()
#     clf.Fit()
#     clf.Score()
#     # result = clf.Predict(clf.data)   
#     # print result