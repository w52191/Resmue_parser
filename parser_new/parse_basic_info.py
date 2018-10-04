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
import math
from os import listdir
from os.path import isfile
from itertools import izip
import jieba
import jieba.posseg as pseg
reload(sys)
sys.setdefaultencoding( "utf-8" )
import pynlpir

class parse_basic_info(object):
	def __init__(self, basic_info_part):
		self.basic_info_part= basic_info_part

	def parse_time(self, row):
		time_rex = u"((?:19|20)\d{2})([-./\u5e74]?)((?:[0-1]?|1)[0-9])?([-./\u6708]?)((?:[0-3]?|[1-3])?[0-9])?(?:$|\D)"
		until_now_rex = u"至今|今|现在"
		temp_index = re.findall(time_rex, row)
		until_now_index = re.findall(until_now_rex, row)
		temp_result = 0.0
		if temp_index:
			# return True
			time_part = [len("".join(x)) for x in (temp_index + until_now_index)]
			temp_result = float(sum(time_part))/len(row)
		if temp_result >= 0.8:
			return True
		else:
			return False

	def parse_email(self, row):
		email_rex = "^[_A-Za-z0-9-\\+]+(\\.[_A-Za-z0-9-]+)*@" + "[A-Za-z0-9-]+(\\.[A-Za-z0-9]+)*(\\.[A-Za-z]{2,})$"
		tmp_index=re.search(email_rex,row)
		if tmp_index:
			return True
		else:
			return False

	def parse_phone(self, row):
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

	def parse_gender(self, row):
		gender_rex = u"\u7537|\u5973" 
		tmp_index=re.search(gender_rex,row)
		if tmp_index:
			return True
		else:
			return False

	def parse_national_identity(self, row):
		national_identity = u"身份证"
		tmp_index=re.search(gender_rex,row)
		if tmp_index:
			return True
		else:
			return False

	def parse_name(self, row):
		temp_index = False
		try:
			segments = pynlpir.segment(row, pos_names='all')
		except Exception as e:
			return temp_index
		temp_count = len("".join([x[0] for x in segments if x[1] in [u'noun:personal name']]))
		if float(temp_count)/len(row) >= 0.5:
			return True 
		else:
			return False

	def parse_location(self, row):
		temp_index = False
		try:
			segments = pynlpir.segment(row, pos_names='all')
		except Exception as e:
			return temp_index
		for segment in segments:
			if segment[1] == u'noun:toponym' or segment[1] == u'noun:toponym:transcribed toponym':
				temp_index = True
		return temp_index		

	def add_label(self, row, label):
		try:
			parse_name_result = self.parse_name(row)
		except:
			parse_name_result = False
		try:
			parse_location_result = self.parse_location(row)
		except:
			parse_location_result = False
		if self.parse_time(row) == True:
			label.append("time")
		if self.parse_email(row) == True:
			label.append("email")
		if self.parse_phone(row) == True:
			label.append("phone")
		if self.parse_gender(row) == True:
			label.append("gender")
		if parse_name_result == True:
			label.append("name")
		if parse_location_result == True:
			label.append("location")
		return label

	def parse_basic_info_main(self):
		pynlpir.open()
		for i in range(len(self.basic_info_part)):
			row = self.basic_info_part[i]['text']
			if (row != u"") and (self.basic_info_part[i]['label']!= ["basic_info_label"]):
				self.basic_info_part[i]['label'] = self.add_label(row, self.basic_info_part[i]['label'])
		pynlpir.close()
		return self.basic_info_part

	# def into_dic(self):
	# 	name = True
	# 	gender = True
	# 	phone = True
	# 	email = True
	# 	location = True
	# 	temp_dic = {}
	# 	small_section = self.basic_info_part
	# 	for i in range(len(small_section)):
	# 		if 'name' in small_section[i]['label'] and name == True:
	# 			temp_dic['name'] = small_section[i]['text']
	# 			name = False
	# 		if 'gender' in small_section[i]['label'] and gender == True:
	# 			temp_dic['gender'] = re.search(u"\u7537|\u5973", small_section[i]['text']).group(0)
	# 		if 'phone' in small_section[i]['label'] and phone == True:
	# 			temp_dic['phone'] = small_section[i]['text']
	# 			phone = False
	# 		if 'email' in small_section[i]['label'] and email == True:
	# 			temp_dic['email'] = small_section[i]['text']
	# 		if 'location' in small_section[i]['label'] and location == True:
	# 			temp_dic['location'] = small_section[i]['text']
	# 			location = False
	# 	return temp_dic

if __name__ == "__main__":
	segmentation_results = pickle.load(open("../experiment/segmentation_results.p", "rb"))
	temp_basic_info = segmentation_results['6.txt']['basic_info'].split("\n")
	temp_basic_info_list = [[x, []] for x in temp_basic_info]
	temp = parse_basic_info(temp_basic_info_list)
	results = temp.parse_basic_info_main()
	for item in results:
		print item['text'], item['label']
