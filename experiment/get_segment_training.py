# -*- coding: utf-8 -*-


import os,re
import json
import source.utility.utilities as utilities
import pickle
import sys

with open('/Users/kshen/github/parser/docs/keywords.txt', "rb") as data_file:    
	segment_word = re.split("\n",data_file.read().decode("utf8", "ignore"))

sys.stdout = open("/Users/kshen/Desktop/keywords.txt", "w+")
for item in segment_word:
	print item.encode('UTF-8') + "|"

sys.stdout.close()


# -*- coding: utf-8 -*-


import os,re
import json
import source.utility.utilities as utilities
import pickle
import sys

# class segmentation():
# 	def __init__(self):
# 		self.config = utilities.load_config('ke') # ke, min, ziheng
# 		self.data_dir = self.config['data_dir']
# 		self.files=os.listdir(self.data_dir)
# 		with open('source/segmentation/segmentation.json') as data_file:    
# 			self.segment_word = json.load(data_file)

write_dir = "/Users/kshen/Desktop/segement_output/"
config = utilities.load_config('ke') # ke, min, ziheng
data_dir = config['data_dir']
files=os.listdir(data_dir)
# segment_word=[u"自我评价",u"教育经历",u"工作经验",u"培训经历",u"项目经验",u"项目经历",u"求职意向",u"推荐证明",u"语言能力",u"联系方式",u"工作情况",u"工作简历",u"附加信息",u"教育情况",u"主要工作业绩",u"基本情况",u"个人概况",u"工作简历",u"工作经历",u"语言能力",u"教育",u"教育背景",u"基本信息",u"个人基本信息",u"教育培训经历",u"职业简历",u"专业技能",u"证书",u"技能",u"附加信息",u"联系方式"]
# with open('source/segmentation/segmentation.json') as data_file:    
# 	segment_word = json.load(data_file)

# with open('/Users/kshen/github/parser/docs/keywords.txt', "rb") as data_file:    
# 	segment_word = re.split("\n",data_file.read().decode("utf8", "ignore"))

# j1 = 1
# i1 = u'999.txt'
alldict={}
for j1,i1 in enumerate(files):
	if re.search(r"\.txt",i1):
		# sys.stdout = open(write_dir+i1, "w+")
		segment_word = [u"教育", u"社会实践", u"工作", u"经历", u"活动", u"项目", u"论文", u"技能", u"个人信息", u"评价", u"爱好", u"特长"]
		content=open(data_dir+i1,"rb").read().decode("utf8","ignore").strip()
		split_re = "；|;|，|。|！|？|：|\\n|,|:|\\s+|\\t+|[　]+"
		content_split = re.split(split_re, content)
		for row in content_split:
			if len(row) <=8:
				index_total = 0
				for segment in segment_word:
					tmp_index=re.search(segment,row)
					if tmp_index:
						index_total += 1
				if index_total > 0:
					# print "-------------------"
					# print row.encode('UTF-8')
					# print "-------------------"
					if row.strip() not in alldict.keys():
						alldict[row.strip()] = [i1.split(".")[0]]
					else:
						alldict[row.strip()] = alldict[row.strip()] + [i1.split(".")[0]]
		# 		else:
		# 			print row.encode('UTF-8')
		# 	else:
		# 		print row.encode('UTF-8')
		# sys.stdout.close()

sys.stdout = open("/Users/kshen/Desktop/keywords.txt", "w+")
for item in alldict.keys():
	print item.encode('UTF-8')

sys.stdout.close()


sys.stdout = open("/Users/kshen/Desktop/keywords_source.txt", "w+")
for item in alldict.keys():
	print ", ".join(alldict[item])

sys.stdout.close()



