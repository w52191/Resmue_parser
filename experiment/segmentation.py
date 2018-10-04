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
import os,re
import json
import pickle
import sys
from segment_classification import *
import math

mapping_dic = {
	0: "basic_info",
	1: "education",
	2: "work_experience",
	3: "social_experience",
	4: "project_experience",
	-9: "non-related"
}
write_dir = "/Users/kshen/Desktop/segement_output_new/"
data_dir = "/Users/kshen/github/parser/docs/sample_resume_new/"
test_dir = "/Users/kshen/Desktop/testusjackal-txt/"
# write_dir = "/Users/Kay/Desktop/segement_output_new/"
# data_dir = "/Users/Kay/Desktop/entropy/parser/docs/sample_resume_new/"

files=os.listdir(data_dir)
# segment_word=[u"自我评价",u"教育经历",u"工作经验",u"培训经历",u"项目经验",u"项目经历",u"求职意向",u"推荐证明",u"语言能力",u"联系方式",u"工作情况",u"工作简历",u"附加信息",u"教育情况",u"主要工作业绩",u"基本情况",u"个人概况",u"工作简历",u"工作经历",u"语言能力",u"教育",u"教育背景",u"基本信息",u"个人基本信息",u"教育培训经历",u"职业简历",u"专业技能",u"证书",u"技能",u"附加信息",u"联系方式"]
# with open('source/segmentation/segmentation.json') as data_file:    
# 	segment_word = json.load(data_file)

# with open('/Users/kshen/github/parser/docs/keywords.txt', "rb") as data_file:    
# 	segment_word = re.split("\n",data_file.read().decode("utf8", "ignore"))

# j1 = 1
# i1 = u'999.txt'

file_name = "segment.p"
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
idf = transformer.idf_


# non_word_value = 9.2564775671942705

clf = svm.SVC(gamma=0.001, C=100.)
clf.fit(weight, label)
# final_results = clf.predict(weight)

test_files=os.listdir(test_dir)
alldict=[]
for j1,i1 in enumerate(test_files):
	if re.search(r"\.txt",i1):
		sys.stdout = open(write_dir+i1, "w+")
		segment_word = [u"教育", u"社会实践", u"工作", u"经历", u"活动", u"项目", u"论文", u"技能", u"个人信息", u"评价", u"爱好", u"特长"]
		content=open(test_dir+i1,"rb").read().decode("utf8","ignore").strip()
		split_re = u"；|、|\u3001|\uff1a|\uff0c|;|】|【|，|。|！|？|：|\\n|,|:|\\s+|\\t+|[　]+"
		content_split = re.split(split_re, content)
		for row in content_split:
			if len(row) <=8:
				index_total = 0
				for segment in segment_word:
					tmp_index=re.search(segment,row)
					if tmp_index:
						index_total += 1
				if index_total > 0:
					new_words = ("".join(re.findall(ur'[\u4e00-\u9fff]+', row))).strip()
					new_words_terms = jieba.lcut(new_words, cut_all=False)
					try:
						term_frequent = np.array([(len(new_words_terms[new_words_terms == x]) if x in new_words_terms else 0) for x in word])
						test_array = [term_frequent[i]*idf[i] for i in range(len(idf))]
						norm_value = np.linalg.norm(test_array)
						if sum(test_array) == 0:
							test_array = np.array(test_array).reshape(1, -1)
						else:
							test_array = np.array([x/norm_value for x in test_array]).reshape(1,-1)
						final_results = clf.predict(test_array)[0]
						# item_location = org_word.index(new_words)
						# if final_results[item_location] != -9:
						if final_results != -9:
							print "-------------------"
							# print mapping_dic[final_results[item_location]]
							print mapping_dic[final_results]
							print "-------------------"
							print row.encode('UTF-8')
							print "-------------------"
						else:
							print row.encode('UTF-8')
					except Exception as e:
						print row.encode('UTF-8')
				else:
					print row.encode('UTF-8')
			else:
				print row.encode('UTF-8')
		sys.stdout.close()

# sys.stdout = open("/Users/kshen/Desktop/keywords.txt", "w+")
# for item in alldict:
# 	print item.encode('UTF-8')

# sys.stdout.close()


