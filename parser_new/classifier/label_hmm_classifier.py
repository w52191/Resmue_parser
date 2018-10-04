# -*- coding: utf-8 -*-
import nltk
import re 
import pickle
import numpy as np
import jieba
import jieba.posseg as pseg
import pandas as pd
from math import *
from sklearn.feature_extraction.text import CountVectorizer
import os

class label_hmm_classifier(object):
    def __init__(self, stopword_path = "data/stop_words.txt", alpha1 = 0.01, alpha2 = 0.0000001):
        self.hm = dict(zip([u'B-0', u'I-0', u'B-1', u'I-1', u'B-2', u'I-2', u'B-3', u'I-3', u'B-4', u'I-4', u'B-5', u'I-5'],range(12)))
        self.hmr = dict(zip(range(12),[u'B-0', u'I-0', u'B-1', u'I-1', u'B-2', u'I-2', u'B-3', u'I-3', u'B-4', u'I-4', u'B-5', u'I-5']))
        self.stoplist = set(open(stopword_path).read().decode("utf8","ignore").split("\n"))
        self.state_set = range(len(self.hm))
        self.n_state = len(self.state_set)
        self.alpha1 = alpha1
        self.alpha2 = alpha2

    def add_resume_id(self, resume_data_row, resume_id):
        resume_data_row.setdefault("resume_id", resume_id)
        return resume_data_row

    def preprocess(self, training_data):
        self.training_df = pd.DataFrame([self.add_resume_id(row, resume["resume_id"]) for resume in training_data for row in resume['resume_data'] if (row["section_label"] != "")])
        self.training_df['new_words'] = self.training_df["text"].map(lambda x: ("".join(re.findall(ur'[a-zA-Z\u4e00-\u9fff]+', x))).strip())
        self.training_df['token_words'] = self.training_df['new_words'].map(lambda x: " ".join([x for x in jieba.lcut(x, cut_all=False) if x not in self.stoplist]))
        self.training_df['new_section_label'] = self.training_df['section_label'].map(lambda x: self.hm[x])
        self.label = self.training_df.groupby("resume_id")["new_section_label"].apply(list)
        self.corpus = self.training_df['token_words'].tolist()
        self.count_vect = CountVectorizer(min_df=5,binary=False,ngram_range=(1,1),token_pattern=u'(?u)\w+',analyzer=u'word')
        self.count_vect.fit(self.corpus)
        self.n_voc = len(self.count_vect.vocabulary_)


    def train(self, training_data):
        self.preprocess(training_data)
        self.emission = np.ones([self.n_state, self.n_voc]) * self.alpha2
        self.pi = np.ones(self.n_state) * self.alpha1
        self.beta = np.ones([self.n_state, self.n_state]) * self.alpha1
        ##compute the best emission matrix
        for i1, i2 in enumerate(self.state_set):
            tmp_voc = self.training_df[self.training_df["new_section_label"] == i2]["token_words"].tolist()
            self.emission[i1,:] = self.emission[i1,:] + self.count_vect.transform(tmp_voc).sum(0).__array__()[0]
            self.emission[i1,:] = self.emission[i1,:]/sum(self.emission[i1,:])
        ##Initial matrix
        for i1, i2 in nltk.FreqDist([i[0] for i in self.label]).items():
            self.pi[i1] += i2
        self.pi /= sum(self.pi)
        ##transition matrix
        trans = nltk.FreqDist(reduce(lambda m, n: m+n, map(lambda k:zip(k[0:-1], k[1:]), self.label), []))
        for i1,i2 in trans.items():
            self.beta[i1[0],i1[1]]+= i2
        self.beta = self.beta/self.beta.sum(1).reshape([-1,1])
        print "Finish Fit the model"
    
    def save_classifier(self, classifier_path = "classifier/cache/label_hmm_classifier.p"):
        pickle.dump(self, open(classifier_path, "wb"))

    def load_classifier(self, classifier_path = "classifier/cache/label_hmm_classifier.p"):
        assert os.path.isfile(classifier_path)
        classifier_class = pickle.load(open(classifier_path, "rb"))
        self.count_vect = classifier_class.count_vect
        self.pi = classifier_class.pi
        self.emission = classifier_class.emission
        self.beta = classifier_class.beta
        self.n_state = classifier_class.n_state
        self.hmr = classifier_class.hmr
    
    def predict(self, test_data):
        test_corpus = test_data['text'].map(lambda x: " ".join([x for x in jieba.lcut(x, cut_all=False)])).tolist()
        x_test = self.count_vect.transform(test_corpus).toarray()
        bestpath_prob = np.ones([self.n_state, len(x_test)])
        bestpath = np.ones([self.n_state, len(x_test)], dtype = int)*np.arange(self.n_state).reshape([self.n_state,1])
        for i in range(len(x_test)):
            tmp_bestpath = np.ones([self.n_state,i],dtype = int) 
            for j in range(self.n_state):
                if i == 0:
                    bestpath_prob[j,i] = log(self.pi[j]) + np.log(self.emission[j]).dot(x_test[i])
                else:
                    tmp = bestpath_prob[:,i-1] + np.log(self.emission[j]).dot(x_test[i]) + np.log(self.beta[:,j])
                    tmp_bestpath[j,:] = bestpath[np.argmax(tmp),:i]
                    bestpath_prob[j,i] = max(tmp)
            bestpath[:,:i] = tmp_bestpath
        test_data["section_label"] = [self.hmr[x] for x in bestpath[np.argmax(bestpath_prob[:, -1])].tolist()]
        return test_data

    