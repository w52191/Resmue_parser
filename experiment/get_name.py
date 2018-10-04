#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pickle


results = pickle.load(open("/Users/Kay/Desktop/entropy/parser/experiment/segmentation_results.p", "rb"))
with open("../docs/lastname_dic.txt", "rb") as f:
	lastname = [x for x in f.read().decode('UTF-8').split("\n") if x != ""]

for key in results.keys():
	print "-------------------"
	print key
	print "-------------------"
	temp = []
	temp_index = []
	rows = [x for x in results[key]['basic_info'].split("\n") if x != ""]
	for row in rows:
		if (row[0] in lastname) & (len(row) >= 2) & (len(row) <= 4):
			temp = temp + [row]
			temp_index = temp_index + [lastname.index(row[0])]
	print temp[temp_index.index(min(temp_index))]



# coding:utf-8

import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

import pynlpir

pynlpir.open()
s = '沈科是个人'
segments = pynlpir.segment(s)
for segment in segments:
    print segment[0], '\t', segment[1]

pynlpir.close()

print results['1742.txt']['basic_info']