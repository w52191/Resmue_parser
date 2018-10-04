# -*- coding: utf-8 -*-
"""
Created on Fri Sep 23 10:00:10 2016

@author: Ke Shen
Store help functions here
"""
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )
import pynlpir

def parse_name(cutoff_point, row):
	pynlpir.open()
	temp_index = False
	try:
		segments = pynlpir.segment(row, pos_names='all')
	except Exception as e:
		return temp_index
	result = [x[0] for x in segments if x[1] in [u'noun:personal name']]
	pynlpir.close()
	part_result = [result, float(len("".join(result)))/len(row)]
	if part_result[1] > cutoff_point:
		return True
	else:
		return False

# require generate_feature processing
def parse_name_test(cutoff_point, row):
	result = [x[0] for x in row["pos"] if x[1] in [u'noun:personal name']]
	part_result = [result, float(len("".join(result)))/len(row["text"])]
	if (part_result[1] > cutoff_point):
		return True
	else:
		return False
