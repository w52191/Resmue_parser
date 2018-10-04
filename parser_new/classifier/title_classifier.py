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

class train_title_classifier(object):
	def __init__(self, mongo_server_ip = '52.220.88.110', save = True):
		self.mongo_server_ip = mongo_server_ip
		self.title_list = []
		self.negative_list = []
		self.save = save
		self.classfier_path = "source/classifier/title_classifier.p"

	def connect_to_mongo(self):
		uri = "mongodb://entropyuser:Goentropy2016@"+self.mongo_server_ip +"/entropy"
		client = MongoClient(uri)
		db = client.entropy
		return db

	def load_major(self):
		db = self.connect_to_mongo()
		temp_title_list = db.job_title_ofweek.find()
		self.title_list = self.title_list + [x['job_title'] for x in temp_title_list]
		
	def load_negative(self):
		path = "../docs/data/training/labelled/"#you should change this for your git location
		file = os.listdir(path)
		keyword=set(["basic_info","education","project_experience","social_experience"])
		self.b = re.compile(u"[\u4e00-\u9fa5]+")
		self.negative_list=[]
		for i in file:
			iswork=False
			f=open(path+i,"rb").read().decode("utf8","ignore").split("\n")
			for j in f:
				if j.strip()=="work_experience":
					iswork=True
				elif j.strip() in keyword:
					iswork=False
				if not iswork:
					kk="".join(self.b.findall(j))
					if len(kk)>0:
						self.negative_list.append(kk)
		self.negative_list = list(set(self.negative_list))

	def preprocess(self):
		self.load_major()
		self.load_negative()
		self.label = np.ones(len(self.negative_list)+len(self.title_list),dtype='int')
		self.label[:len(self.negative_list)] = 0
		self.corpus=[" ".join(jieba.lcut(i)) for i in self.negative_list + self.title_list]
		self.count_vect = CountVectorizer(min_df=1,binary=False,token_pattern=u'(?u)\w+',analyzer=u'word')
		self.count_vect.fit(self.corpus)
		self.word = self.count_vect.get_feature_names()
		self.data = self.count_vect.fit_transform(self.corpus)

	def train_cv(self):
		self.preprocess()
		reg_list = [0.01, 0.05, 0.1, 0.5, 1, 2]
		index=KFold(n_splits=5,shuffle=True,random_state=1234)
		result_dict = {0.01:[],0.05:[],0.1:[],0.5:[],1:[],2:[]}
		for i in reg_list:
			for train_index, test_index in index.split(self.data):
				clf = BernoulliNB(i)
				xtrain = self.data[train_index]
				ytrain = self.label[train_index]
				xtest = self.data[test_index]
				ytest = self.label[test_index]
				clf.fit(xtrain, ytrain)
				result_dict[i].append(clf.score(xtest,ytest))
				ytest_predict = clf.predict(xtest)
				print confusion_matrix(ytest.tolist(), ytest_predict.tolist())
		pprint.pprint(result_dict)

	def train(self, alpha = 0.01):
		self.preprocess()
		# X_train, X_test, y_train, y_test = train_test_split(self.data, self.label, test_size=0.2, random_state=50)
		self.clf = SVC(kernel='linear', C=100, class_weight="balanced")
		self.clf = BernoulliNB(alpha)
		# self.clf.fit(X_train, y_train)
		self.clf.fit(self.data, self.label)
		if self.save == True:
			pickle.dump(self, open(self.classfier_path, "wb"))

	def predict(self, new_word):
		# return map(lambda x: self.clf.predict(x), self.count_vect.transform([" ".join(jieba.lcut(i)) for i in [new_word]]))
		if new_word in self.title_list:
			return 1 
		elif len(jieba.lcut("".join(self.b.findall(new_word)))) > 0 and len("".join(self.b.findall(new_word))) > 1:
			return self.clf.predict(self.count_vect.transform([" ".join(jieba.lcut("".join(self.b.findall(new_word))))])[0])[0]
		else:
			return 0

if __name__ == "__main__":
	temp = train_title_classifier()
	temp.train()
	test_path = "../docs/data/test/labelled/"
	output_path = "/Users/kshen/Desktop/job_title/"
	files = os.listdir(test_path)
	for doc_name in files:
		f = open(test_path + doc_name, "rb").read().decode("utf8", "ignore").split("\n")
		sys.stdout = open(output_path + doc_name, "w+")
		for i in range(len(f)):
			result = temp.predict(f[i])
			if result == 1:
				print f[i].encode("UTF-8") + " <------- job_title"
			else:
				print f[i].encode("UTF-8")

		# for i in range(len(f)):
		# 	if results[i] == 1:
		# 		print f[i].encode("UTF-8") + " <------- major"
		# 	else:
		# 		print f[i].encode("UTF-8")





