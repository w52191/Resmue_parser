# -*- coding: utf-8 -*-
import pickle
import re
import os
from os import listdir
from os.path import isfile
from itertools import izip
import jieba
import jieba.posseg as pseg
import source.utility.utilities as utilities
from train_major_classifier import *
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )
import pynlpir

class parse_education(object):
	def __init__(self, education_part, re_train = False):
		self.education_part= education_part
		self.school_set = set()
		self.cut_label = ""
		self.in_section = ""
		if re_train == True:
			self.major_classifier = train_major_classifier.train_major_classifier()
			self.major_classifier.train()
		else:
			self.major_classifier = pickle.load(open("source/classifier/major_classifier.p", "rb"))

	def parse_time(self, row):
		time_rex = u"((?:19|20)\d{2})([-./\u5e74]?)((?:[0-1]?|1)[0-9])?([-./\u6708]?)((?:[0-3]?|[1-3])?[0-9])?(?:$|\D)"
		until_now_rex = u"至今|今|现在|预计"
		temp_index = re.findall(time_rex, row)
		until_now_index = re.findall(until_now_rex, row)
		if temp_index:
			# return True
			time_part = [len("".join(x)) for x in (temp_index + until_now_index)]
			return float(sum(time_part))/len(row)
		else:
			return 0.0

	def parse_edu(self, row):
		re_schooltoken = re.compile(u"[\u4e00-\u9fa5]+(大学|学院|分校)[\u4e00-\u9fa5]*\s?", re.UNICODE)
		re_schoolname = re.compile(u"[\u4e00-\u9fa5]+(大学|学院|分校)\s?", re.UNICODE)
		match_sc = re.search(re_schooltoken, row)
		token = None if not match_sc else match_sc.group().strip()
		if utilities.valid_name(token):
			school = re.search(re_schoolname, token).group().strip()
			#print school
			if utilities.filter_school_by_first_flag(school):
				if len(self.school_set) == 0:
					self.school_set.add(school)
					return float(len(school))/len(row)
				else:
					#check previously added school names, determine whether
					#to add the current name or not, default is to add
					can_add = True
					for pre in self.school_set:
						new_set = set(self.school_set)
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
						self.school_set = new_set
					if can_add:
						self.school_set.add(school)
					return float(len(school))/len(row)
			else:
				return 0.0
		else:
			return 0.0

	def parse_location(self, row):
		temp_index = False
		try:
			segments = pynlpir.segment(row, pos_names='all')
		except Exception as e:
			return temp_index
		temp_count = len("".join([x[0] for x in segments if x[1] in [u'noun:toponym', u'noun:toponym:transcribed toponym']]))
		if float(temp_count)/len(row) >= 0.5:
			return True 
		else:
			return False

	def parse_degree(self, row):
		degree_rex = u'学士|硕士|本科|博士|研究生'
		temp_index = re.findall(degree_rex, row)
		if temp_index:
			return True
		else:
			return False

	def parse_course_label(self, row):
		course_rex = u"课程"
		if len(row) <=  8 and re.findall(course_rex, row):
			return True
		else:
			return False

	def split_degree(self, row):
		degree_rex = u'学士|硕士|本科|博士|研究生'
		return re.split(degree_rex, row)[0]

	def parse_reward(self, row):
		reward_rex = u'奖项|奖|优秀'
		temp_index = re.findall(reward_rex, row)
		if temp_index:
			return True
		else:
			return False

	def parse_gpa(self, row):
		gpa_rex = u'GPA|gpa|平均|绩点'
		temp_index = re.findall(gpa_rex, row)
		if temp_index:
			return True
		else:
			return False 

	def add_label(self, row, label):
		time_percentage = self.parse_time(row)
		education_percentage = self.parse_edu(row)
		if time_percentage + education_percentage >= 0.8:
			if time_percentage >= 0.8:
				temp_label = ["time"]
			elif education_percentage >= 0.8:
				temp_label = ["school"]
			else:
				temp_label = ["time", "school"]
			label = label + temp_label
			if self.cut_label == "":
				self.cut_label = temp_label[0]
		try:
			parse_location_result = self.parse_location(row)
		except:
			parse_location_result = False
		if parse_location_result == True:
			label.append("location")
		if self.parse_degree(row) == True:
			label.append("degree")
		if self.major_classifier.predict(row) == 1 and self.in_course_section == False:
			label.append("major")

		if self.parse_gpa(row) == True:
			label.append('gpa')
			self.in_section = "gpa"
		elif self.parse_reward(row) == True:
			label.append('reward')
			self.in_section = "reward"
		elif self.parse_course_label(row) == True:
			label.append('course')
			self.in_section = 'course'
		elif (len(label) == 0 or label == ['time']) and self.in_section != "":
			label.append(self.in_section)
		elif self.in_section != "":
			self.in_section = ""
		if self.major_classifier.predict(row) == 1 and self.in_course_section == False:
			label.append("major")
		return label

	def parse_education_main(self):
		pynlpir.open()
		for i in range(len(self.education_part)):
			row = self.education_part[i]['text']
			if (row != u"") and (self.education_part[i]['label']!= ["education_label"]):
				self.education_part[i]['label'] = self.add_label(row, self.education_part[i]['label'])
				# if i >= 1:
				# 	self.education_part[i-1 : i+1] = self.add_label_before_after(self.education_part[i-1 : i+1])
				if (self.cut_label in self.education_part[i]['label']) and len(self.cut_label) > 0:
					self.education_part[i]['label'] = self.education_part[i]['label'] + ['small_section_cut']
		pynlpir.close()
		return self.education_part

if __name__ == "__main__":
	segmentation_results = pickle.load(open("../experiment/segmentation_results.p", "rb"))
	for file_name in segmentation_results.keys():
	# file_name = '2.txt'
		if segmentation_results[file_name]['education'] != u"":
			temp_education = segmentation_results[file_name]['education'].split("\n")
			temp_education_list = [[x, []] for x in temp_education]
			temp = parse_education(temp_education_list)
			results = temp.parse_education_main()
			# for item in results:
			# 	print item[0], item[1]
			sys.stdout = open("/Users/kshen/Desktop/education_segement/" + file_name, "w+")
			for i in range(len(results)):
				if (temp.cut_label == results[i]['label']) and len(temp.cut_label) > 0:
					print "*******************"
					print results[i]['text'].encode('UTF-8')
				else:
					print results[i]['text'].encode('UTF-8')
	sys.stdout.close()
