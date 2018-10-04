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
from os import listdir
from os.path import isfile
from itertools import izip
import jieba
import jieba.posseg as pseg
import utilities as utilities
reload(sys)
sys.setdefaultencoding( "utf-8" )
import pynlpir

pynlpir.open()

def parse_email(row):
	email_rex = "^[_A-Za-z0-9-\\+]+(\\.[_A-Za-z0-9-]+)*@" + "[A-Za-z0-9-]+(\\.[A-Za-z0-9]+)*(\\.[A-Za-z]{2,})$"
	tmp_index=re.search(email_rex,row)
	if tmp_index:
		return True
	else:
		return False

def parse_phone(row):
	phone_area_number = "(\\+?((\\d{1,3})|\\d{1,3}|(\\(\\d{1,3}\\)))?)"	
	phone_append_rex = "((\\d{3}[-]?((\\d{4}[-]?\\d{4})|(\\d{5}[-]?\\d{3})|(\\d{3}[-]?\\d{5})))|(\\d{4}[-]?\\d{3}[-]?\\d{4}))"
	phone_number_rex = phone_area_number +"[-]?" + phone_append_rex
	tmp_index = re.search(phone_number_rex,row)
	if tmp_index:
		tmp_length = len("".join(re.findall(u'[0-9]', row)))
		if tmp_length == 11:
			return True
		else:
			return False
	else:
		return False

def parse_gender(row):
	gender_rex = u"\u7537|\u5973" 
	tmp_index=re.search(gender_rex,row)
	if tmp_index:
		return True
	else:
		return False

def parse_edu(row, school_set):
	re_schooltoken = re.compile(u"[\u4e00-\u9fa5]+(大学|学院|分校)[\u4e00-\u9fa5]*\s?", re.UNICODE)
	re_schoolname = re.compile(u"[\u4e00-\u9fa5]+(大学|学院|分校)\s?", re.UNICODE)
	#match_edu = re.search(re_edu, row)
	#match_exp = re.search(re_exp, row)
	#school_start = False if not match_edu and not school_start else True

	#for token in row.split():
	match_sc = re.search(re_schooltoken, row)
	token = None if not match_sc else match_sc.group().strip()
	#print token
	#print utilities.valid_name(token)
	if utilities.valid_name(token):
		school = re.search(re_schoolname, token).group().strip()
		#print school
		if utilities.filter_school_by_first_flag(school):
			if len(school_set) == 0:
				school_set.add(school)
			else:
				#check previously added school names, determine whether
				#to add the current name or not, default is to add
				can_add = True
				for pre in school_set:
					new_set = set(school_set)
					inters = utilities.intersect(pre, school)
					
					#magic number, school name has at least 4 chars
					#if overlap greater than 4, then need to disgard the
					#longer name since it contains other chars
					#only when name in current string has appeared,
					#and the previously added name is shorter, we do
					#not need to add this name since it contains 
					#unneccessary words
					if len(inters) >= 4: 
						if len(school) >= len(pre):
							can_add = False
						else:
							new_set.remove(pre)
					elif len(school) <= 3:
						can_add = False
					school_set = new_set
				if can_add:
					school_set.add(school)
			return True
		else:
			return False
	else:
		return False

def identify_time(row):
	time_rex = u"((19|20)\d{2})[-./\u5e74]?((?:[0-1]?|1)[0-9])?[-./\u6708]?((?:[0-3]?|[1-3])?[0-9])?[^\d]"
	temp_index = re.search(time_rex, row)
	return temp_index 


def parse_name(row):
	segments = pynlpir.segment(row, pos_names='all')
	temp_index = False
	try:
		segments = pynlpir.segment(row, pos_names='all')
	except Exception as e:
		return temp_index
	for segment in segments:
		if segment[1] == u'noun:personal name':
			temp_index = True
	return temp_index

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
test_dir = "/Users/kshen/Desktop/output_1/"

if not os.path.exists(write_dir):
	os.makedirs(write_dir)
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
		school_set = set()
		sys.stdout = open(write_dir+i1, "w+")
		segment_word = [u"教育", u"社会实践", u"工作", u"经历", u"活动", u"项目", u"论文", u"技能", u"个人信息", u"评价", u"爱好", u"特长"]
		content=open(test_dir+i1,"rb").read().decode("utf8","ignore").strip()
		split_re = u"；|、|\u3001|\uff1a|\uff0c|;|】|【|，|。|！|？|：|\\n|,|:|\\s+|\\t+|[　]+"
		content_split = re.split(split_re, content)
		current_segement = "basic_info"
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
							print "*******************"
							current_segement = mapping_dic[final_results]
						else:
							if identify_time(row):
								print row.encode("utf-8") + " <--------- Time"
							elif parse_edu(row, school_set) & (current_segement == "education"):
								print row.encode("utf-8") + " <--------- School"
							elif parse_email(row) & (current_segement == "basic_info"):
								print row.encode("utf-8") + " <--------- Email"
							elif parse_phone(row) & (current_segement == "basic_info"):
								print row.encode("utf-8") + " <--------- Phone"
							elif parse_gender(row) & (current_segement == "basic_info"):
								print row.encode("utf-8") + " <--------- Gender"
							elif (current_segement == "basic_info"):
								try:
									parse_name_result = parse_name(row)
								except:
									parse_name_result = False
								if parse_name_result == True:
									print row.encode("utf-8") + " <--------- Name"
								else:
									print row.encode("utf-8")
							else:
								print row.encode("utf-8")
					except Exception as e:
						if identify_time(row):
							print row.encode("utf-8") + " <--------- Time"
						elif parse_edu(row, school_set) & (current_segement == "education"):
							print row.encode("utf-8") + " <--------- School"
						elif parse_email(row) & (current_segement == "basic_info"):
							print row.encode("utf-8") + " <--------- Email"
						elif parse_phone(row) & (current_segement == "basic_info"):
							print row.encode("utf-8") + " <--------- Phone"
						elif parse_gender(row) & (current_segement == "basic_info"):
							print row.encode("utf-8") + " <--------- Gender"
						elif (current_segement == "basic_info"):
							try:
								parse_name_result = parse_name(row)
							except:
								parse_name_result = False
							if parse_name_result == True:
								print row.encode("utf-8") + " <--------- Name"
							else: 
								print row.encode("utf-8")
						else:
							print row.encode("utf-8")
				else:
					if identify_time(row):
						print row.encode("utf-8") + " <--------- Time"
					elif parse_edu(row, school_set) & (current_segement == "education"):
						print row.encode("utf-8") + " <--------- School"
					elif parse_email(row) & (current_segement == "basic_info"):
						print row.encode("utf-8") + " <--------- Email"
					elif parse_phone(row) & (current_segement == "basic_info"):
						print row.encode("utf-8") + " <--------- Phone"
					elif parse_gender(row) & (current_segement == "basic_info"):
						print row.encode("utf-8") + " <--------- Gender"
					elif (current_segement == "basic_info"):
						try:
							parse_name_result = parse_name(row)
						except:
							parse_name_result = False
						if parse_name_result == True:
							print row.encode("utf-8") + " <--------- Name"
						else:
							print row.encode("utf-8")
					else:
						print row.encode("utf-8")
			else:
				if identify_time(row):
					print row.encode("utf-8") + " <--------- Time"
				elif parse_edu(row, school_set) & (current_segement == "education"):
					print row.encode("utf-8") + " <--------- School"
				elif parse_email(row) & (current_segement == "basic_info"):
					print row.encode("utf-8") + " <--------- Email"
				elif parse_phone(row) & (current_segement == "basic_info"):
					print row.encode("utf-8") + " <--------- Phone"
				elif parse_gender(row) & (current_segement == "basic_info"):
					print row.encode("utf-8") + " <--------- Gender"
				elif (current_segement == "basic_info"):
					try:
						parse_name_result = parse_name(row)
					except:
						parse_name_result = False
					if parse_name_result == True:
						print row.encode("utf-8") + " <--------- Name"
					else:
						print row.encode("utf-8")
				else:
					print row.encode("utf-8")
		sys.stdout.close()

pynlpir.close()
# sys.stdout = open("/Users/kshen/Desktop/keywords.txt", "w+")
# for item in alldict:
# 	print item.encode('UTF-8')

# sys.stdout.close()


