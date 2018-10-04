# -*- coding: utf-8 -*-
import jieba
import jieba.posseg as pseg
from train_company_name_classifier import *
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )
import pynlpir

class parse_work_experience(object):
	def __init__(self, work_experience_part, re_train = False):
		self.work_experience_part = work_experience_part
		self.cut_label = []
		if re_train == True:
			self.classifier = train_company_name_classifier()
			self.classifier.train()
		else:
			self.classifier = pickle.load(open("source/classifier/company_name_classifier.p", "rb"))

	def parse_time(self, row):
		time_rex = u"((?:19|20)\d{2})([-./\u5e74]?)((?:[0-1]?|1)[0-9])?([-./\u6708]?)((?:[0-3]?|[1-3])?[0-9])?(?:$|\D)"
		until_now_rex = u"至今|今|现在"
		temp_index = re.findall(time_rex, row)
		until_now_index = re.findall(until_now_rex, row)
		if temp_index:
			# return True
			time_part = [len("".join(x)) for x in (temp_index + until_now_index)]
			return float(sum(time_part))/len(row)
		else:
			return 0.0

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

	def parse_company_name(self, row):
		return self.classifier.predict(row)

	def add_label(self, row, label):
		time_percentage = self.parse_time(row)
		company_name_percentage = self.parse_company_name(row)
		if time_percentage + company_name_percentage >= 0.8:
			if time_percentage >= 0.8:
				temp_label = ["time"]
			elif company_name_percentage >= 0.8:
				temp_label = ["company"]
			else:
				temp_label = ["time", "company"]
			label = label + temp_label
			if self.cut_label == []:
				self.cut_label = temp_label
		try:
			parse_location_result = self.parse_location(row)
		except:
			parse_location_result = False
		if parse_location_result == True:
			label.append('location')
		return label

	def parse_work_experience_main(self):
		pynlpir.open()
		for i in range(len(self.work_experience_part)):
			row = self.work_experience_part[i]['text']
			if (row != u"") and (self.work_experience_part[i]['label']!= ["education_label"]):
				self.work_experience_part[i]['label'] = self.add_label(row, self.work_experience_part[i]['label'])
				if (self.cut_label == self.work_experience_part[i]['label']) and len(self.cut_label) > 0:
					self.work_experience_part[i]['label'] = self.work_experience_part[i]['label'] + ['small_section_cut']
		pynlpir.close()
		return self.work_experience_part