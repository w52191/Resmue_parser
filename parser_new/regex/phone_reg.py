# -*- coding: utf-8 -*-
"""
Created on Fri Sep 23 10:00:10 2016

@author: Ke Shen
Store help functions here
"""
import re

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