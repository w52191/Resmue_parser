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

def segment_classification(file_name = "segment.p"):
	df = pickle.load(open(file_name, "rb"))
	df['new_words'] = df["words"].map(lambda x: ("".join(re.findall(ur'[\u4e00-\u9fff]+', x))).strip())
	df['token_words'] = df['new_words'].map(lambda x: " ".join(jieba.lcut(x, cut_all=False)))
	df = df.reindex(np.random.permutation(df.index))
	corpus = []
	label = []
	org_word = []
	for i in range(len(df)):
		corpus = corpus + [df['token_words'][i] for x in range(df['num_term'][i]+1)]
		label = label + [df['label'][i] for x in range(df['num_term'][i]+1)]
		org_word = org_word + [df['new_words'][i] for x in range(df['num_term'][i]+1)]

	vectorizer=CountVectorizer()
	transformer=TfidfTransformer()
	tfidf=transformer.fit_transform(vectorizer.fit_transform(corpus))
	word=vectorizer.get_feature_names()
	weight=tfidf.toarray()
	label = np.asarray(label)


	clf = svm.SVC(gamma=0.001, C=100.)
	clf.fit(weight, label)
	temp = clf.predict(weight)
	return temp
# temp = clf.predict(weight)
# label

# for x in org_word[-100:]:
# 	print x 

# for x in corpus[-100:]:
# 	print x

