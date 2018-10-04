# -*- coding: utf-8 -*-
"""
Created on Fri Sep 23 10:00:10 2016

@author: Min Xu
Store help functions here
"""
import jieba
import jieba.posseg as pseg
import os
import json

filter_flags = set(["s","r","v","t","b","z","p"])

#compute overlap between school names
def intersect(a, b):
    res = ""
    for c in a:
        if c in b and not c in res:
            res += c
    return res

#validate the line to see if it contains too many non-nouns
#if yes, then this line is not suitable for extracting school names
def valid_name(line):
    if line is None: 
        return False
    words = pseg.cut(line)
    cnt = 0
#    if not words.next().flag.startswith("n"): 
#        return False
    for word in words:
        #print word.word, word.flag
        cnt = cnt + 1 if not "n" in word.flag else cnt
    if cnt > 2:
        return False
    else:
        return True

#consider invalid school name if the first flag is in the filter_flags set
def filter_school_by_first_flag(line):
    firstword = pseg.cut(line).next()
    for flag in filter_flags:
        if firstword.flag.startswith(flag): 
            return False
    return True

def load_config(config_type):
    config = None
    try:
		with open('parser/source/config/config.json') as data_file:    
			config = json.load(data_file)[config_type]
    except Exception as e:	
		try:
			with open('source/config/config.json') as data_file:    
				config = json.load(data_file)[config_type]
		except Exception as e:
			try:
				with open('config/config.json') as data_file:    
					config = json.load(data_file)[config_type]
			except Exception as e:
				try:
					with open('config.json') as data_file:    
						config = json.load(data_file)[config_type]
				except Exception as e:
					print e
    return config		