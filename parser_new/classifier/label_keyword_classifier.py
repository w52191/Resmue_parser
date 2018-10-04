# -*- coding: utf-8 -*-
import jieba
import jieba.posseg as pseg
import pandas as pd
import sys
import pickle
import re
from sklearn import feature_extraction  
from sklearn.feature_extraction.text import TfidfTransformer  
from sklearn.feature_extraction.text import CountVectorizer 
import numpy as np
from sklearn import svm
from sklearn.svm import SVC
import os,re
import json
import pickle
import sys
import math

class label_keyword_classifier(object):
    def __init__(self):
        self.segment_word = [u"教育", u"实践", u"工作", u"经历", u"活动", u"项目", u"论文", u"技能", u"个人信息", u"评价", u"爱好", u"特长", u"荣誉", u"奖项", u"奖励", u"其他信息"]

    def find_keywords(self, text):
        if len([1 for x in self.segment_word if (re.search(x, text) and len(text) <= 9)]) > 0:
            return True
        else:
            return False

    def preprocess(self, training_data):
        self.training_df = pd.DataFrame([row for resume in training_data for row in resume['resume_data'] if self.find_keywords(row["text"])])
        self.training_df['new_words'] = self.training_df["text"].map(lambda x: ("".join(re.findall(ur'[\u4e00-\u9fff]+', x))).strip())
        self.training_df['token_words'] = self.training_df['new_words'].map(lambda x: " ".join(jieba.lcut(x, cut_all=False)))
        self.training_df['new_section_label'] = self.training_df.apply(lambda row: (row["section_label"][2:] if row["section_label"].startswith("B") else "-9"), axis=1)
        self.training_df = self.training_df.reindex(np.random.permutation(self.training_df.index))
        self.corpus = self.training_df['token_words'].tolist()
        self.label = self.training_df['new_section_label'].tolist()
        self.vectorizer=CountVectorizer()
        self.transformer=TfidfTransformer()
        self.tfidf= self.transformer.fit_transform(self.vectorizer.fit_transform(self.corpus))
        self.word=self.vectorizer.get_feature_names()
        self.weight=self.tfidf.toarray()
        self.label = np.asarray(self.label)
        self.idf = self.transformer.idf_

    def train(self, training_data):
        self.preprocess(training_data)
        self.clf = SVC(kernel='linear', C=100, class_weight="balanced")
        self.clf.fit(self.weight, self.label)

    def save_classifier(self, classifier_path = "classifier/cache/label_keyword_classifier.p"):
        pickle.dump(self, open(classifier_path, "wb"))

    def load_classifier(self, classifier_path = "classifier/cache/label_keyword_classifier.p"):
        assert os.path.isfile(classifier_path)
        classifier_class = pickle.load(open(classifier_path, "rb"))
        self.word = classifier_class.word
        self.idf = classifier_class.idf
        self.clf = classifier_class.clf

    def predict_word(self, test_word):
        if self.find_keywords(test_word):
            new_words = ("".join(re.findall(ur'[\u4e00-\u9fff]+', test_word))).strip()
            new_words_terms = jieba.lcut(new_words, cut_all=False)
            try:
                term_frequent = np.array([(len(new_words_terms[new_words_terms == x]) if x in new_words_terms else 0) for x in self.word])
                test_array = [term_frequent[j]*self.idf[j] for j in range(len(self.idf))]
                norm_value = np.linalg.norm(test_array)
                if sum(test_array) == 0:
                    test_array = np.array(test_array).reshape(1, -1)
                else:
                    test_array = np.array([x/norm_value for x in test_array]).reshape(1,-1)
                final_results = self.clf.predict(test_array)[0]
            except Exception as e:
                final_results = "-9"
            return final_results
        else:
            return "-9"

    def predict(self, test_data):
        section_label = []
        current_status = "0"
        for x in test_data["text"].tolist():
            section_label_temp = self.predict_word(x)
            if section_label_temp != "-9":
                current_status = section_label_temp
                section_label.append("B-" + current_status)
            else:
                section_label.append("I-" + current_status)
        test_data["section_label"] = section_label
        return test_data



