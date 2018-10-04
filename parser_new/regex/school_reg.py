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
import re

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