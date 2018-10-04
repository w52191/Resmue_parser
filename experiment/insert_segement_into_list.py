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

mapping_list = [
	"education\n",
	"work_experience\n",
	"social_experience\n",
	"project_experience\n",
]
write_dir = "/Users/Kay/Desktop/entropy/parser/docs/segement_output_new/"
files=os.listdir(write_dir)

total = {}
for j1,i1 in enumerate(files):
	if re.search(r"\.txt",i1):
		temp_dic = {}
		content=open(write_dir+i1,"rb").read().decode("utf8","ignore").strip()
		split_re = "-------------------\n"
		content_split = re.split(split_re, content)
		content_split[-1] = content_split[-1] + "\n"
		education_index = [i for i, x in enumerate(content_split) if x == "education\n"]
		work_index = [i for i, x in enumerate(content_split) if x == "work_experience\n"]
		social_index = [i for i, x in enumerate(content_split) if x == "social_experience\n"]
		project_index = [i for i, x in enumerate(content_split) if x == "project_experience\n"]
		basic_info_index = [i for i, x in enumerate(content_split) if x == "basic_info\n"]
		total_index = education_index + work_index + social_index + project_index + basic_info_index
		temp_dic['education'] = [content_split[i+1] for i in education_index if ((i+1) not in total_index and (i+1) < len(content_split))]
		temp_dic['work_experience'] = [content_split[i+1] for i in work_index if ((i+1) not in total_index and (i+1) < len(content_split))]
		temp_dic['social_experience'] = [content_split[i+1] for i in social_index if ((i+1) not in total_index and (i+1) < len(content_split))]
		temp_dic['project_experience'] = [content_split[i+1] for i in project_index if ((i+1) not in total_index and (i+1) < len(content_split))]
		left_over_list = list(set(range(len(content_split))) - set(total_index))
		left_over = [content_split[x] for x in left_over_list]
		temp_dic['basic_info'] = list(set(left_over) - set(temp_dic['education']+temp_dic['work_experience']+temp_dic['social_experience']+temp_dic['project_experience']))
		temp_dic['work_experience'] = "".join(temp_dic['work_experience'])
		temp_dic['social_experience'] = "".join(temp_dic['social_experience'])
		temp_dic['project_experience'] = "".join(temp_dic['project_experience'])
		temp_dic['education'] = "".join(temp_dic['education'])
		temp_dic['basic_info'] = "".join(temp_dic['basic_info'])
		total[i1] = temp_dic

pickle.dump(total, open("/Users/Kay/Desktop/entropy/parser/experiment/segmentation_results.p", "wb"))