# -*- coding: utf-8 -*-
import re
import numpy as np
import jieba
import sys
import os
import pymongo
import pickle
from pymongo import MongoClient
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score,GridSearchCV,KFold,train_test_split
from sklearn.metrics import accuracy_score,confusion_matrix
from sklearn.naive_bayes import BernoulliNB
import pprint
from sklearn.svm import LinearSVC
import pynlpir
pynlpir.open()

class train_company_name_classifier(object):
	def __init__(self, mongo_server_ip = '52.220.88.110', save = True):
		self.mongo_server_ip = mongo_server_ip
		self.company_list = []
		self.negative_list = []
		self.save = save
		self.classfier_path = "/Users/ihuang/git/ziheng2_new/parser/source/company_name_classifier.p"
	def connect_to_mongo(self):
		uri = "mongodb://entropyuser:Goentropy2016@"+self.mongo_server_ip +"/entropy"
		client = MongoClient(uri)
		db = client.entropy
		return db
	def load_company_name(self):
		db = self.connect_to_mongo()
		temp_company_list = db.company.find()
		temp_ziheng_company_list = db.ziheng_company.find()
		self.company_list = self.company_list + [x['company_name'] for x in temp_ziheng_company_list]
		self.company_list = filter(lambda x:re.search(ur"[\u4e00-\u9fa5]",x),set(self.company_list + [x['company_name'] for x in temp_company_list][:100000]))
	def load_negative(self):
		db = self.connect_to_mongo()
		resumes = [x['resume_data'] for x in db.resumes.find()]
		self.b = re.compile(u"[\u4e00-\u9fa5]+")
		self.negative_list=[]
		for resume in resumes:
			goahead=False
			for row in resume:
				if 'company' not in row['tag_label']:
					self.negative_list.append(row['text'])
					goahead=False
				else:
					if re.search(ur"[\u4e00-\u9fa5]",row['text']):
						if goahead==False:
							self.company_list.append(row['text'])
							goahead=True
						else:
							self.company_list[-1]+=row['text']
		self.negative_list = filter(lambda i:not re.search(u"有限公司",i) and not re.search(u"银行",i) and not re.search(u"证券",i), self.negative_list)
		self.negative_list = list(set(self.negative_list))
	def preprocess(self):
		self.load_company_name()
		self.load_negative()
		self.label = np.ones(len(self.negative_list)+len(self.company_list),dtype='int')
		self.label[:len(self.negative_list)] = 0
		#self.corpus=[cor for cor in [" ".join([token for token in jieba.lcut(i) if re.search(ur"[a-zA-Z\u4e00-\u9fa5]",token)]+["last"+token]) for i in self.negative_list + self.company_list] if len(cor.split(" "))>2]
		self.corpus=[" ".join([token for token in pynlpir.segment(i,pos_tagging=False) if re.search(ur"[a-zA-Z\u4e00-\u9fa5]",token)]+["last"+token]) for i in (self.negative_list + self.company_list)]
		#self.corpus=[" ".join(jieba.lcut(i)) for i in self.negative_list + self.company_list]
		self.count_vect = CountVectorizer(min_df=3,binary=False,token_pattern=u'(?u)\w+',analyzer=u'word')
		self.count_vect.fit(self.corpus)
		self.word = self.count_vect.get_feature_names()
		self.data = self.count_vect.fit_transform(self.corpus)


	def train_cv(self):
		self.preprocess()
		reg_list = [0.1, 0.5, 1, 2,5,10]
		index=KFold(n_splits=5,shuffle=True,random_state=1234)
		result_dict = {0.1:[],0.5:[],1:[],2:[],5:[],10:[]}
		for i in reg_list:
			for train_index, test_index in index.split(self.data):
				clf = LinearSVC(C=i)
				xtrain = self.data[train_index]
				ytrain = self.label[train_index]
				xtest = self.data[test_index]
				ytest = self.label[test_index]
				clf.fit(xtrain, ytrain)
				result_dict[i].append(clf.score(xtest,ytest))
				ytest_predict = clf.predict(xtest)
				print i,confusion_matrix(ytest.tolist(), ytest_predict.tolist())
		pprint.pprint(result_dict)

	def train(self, alpha = 0.5):
		self.preprocess()
		# X_train, X_test, y_train, y_test = train_test_split(self.data, self.label, test_size=0.2, random_state=50)
		self.clf = LinearSVC(C=alpha)
		# self.clf.fit(X_train, y_train)
		self.clf.fit(self.data, self.label)
		if self.save == True:
			pickle.dump(self, open(self.classfier_path, "wb"))

	def predict(self, new_word):
		# return map(lambda x: self.clf.predict(x), self.count_vect.transform([" ".join(jieba.lcut(i)) for i in [new_word]]))
		if len(jieba.lcut("".join(self.b.findall(new_word)))) > 0 and len("".join(self.b.findall(new_word))) > 3:
			if re.search(u"有限公司|公司$", new_word):
				return 1
			else:
				return self.clf.predict(self.count_vect.transform([" ".join(jieba.lcut("".join(self.b.findall(new_word))))])[0])[0]
				# new_words_terms = jieba.lcut("".join(self.b.findall(new_word)))
				# term_frequent = np.array([(len(new_words_terms[new_words_terms == x]) if x in new_words_terms else 0) for x in self.word])
				# return self.clf.predict(term_frequent.reshape(1, -1))[0]
		else:
			return 0

	# def predict_batch(self, new_word):
	# 	b = re.compile(u"[\u4e00-\u9fa5]+")
	# 	temp_result = map(lambda x: self.clf.predict(x), self.count_vect.transform([" ".join(jieba.lcut("".join(b.findall(i)))) for i in new_word]))
