# -*- coding: utf-8 -*-
"""
Created on Fri Sep 23 10:00:10 2016

@author: Ke Shen
Store help functions here
"""
import re

def parse_email(self, row):
	email_rex = "^[_A-Za-z0-9-\\+]+(\\.[_A-Za-z0-9-]+)*@" + "[A-Za-z0-9-]+(\\.[A-Za-z0-9]+)*(\\.[A-Za-z]{2,})$"
	tmp_index=re.search(email_rex,row)
	if tmp_index:
		return True
	else:
		return False