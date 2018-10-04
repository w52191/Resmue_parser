# -*- coding: utf-8 -*-

import pymongo
from pymongo import MongoClient
import pandas as pd

class load_training_data(object):
    def __init__ (self, mongodb_ip = '52.220.88.110'):
        self.mongodb_ip = mongodb_ip

    def connect_to_mongo(self):
        url = "mongodb://entropyuser:Goentropy2016@"+ self.mongodb_ip +"/entropy"
        client = MongoClient(url)
        db = client.entropy
        return db

    def add_resume_id(self, resume_data_row, resume_id):
        resume_data_row.setdefault("resume_id", resume_id)
        return resume_data_row

    def load(self):
        db = self.connect_to_mongo()
        self.resumes = [x for x in db.resumes.find()]
        self.resume_labels = [x for x in db.resume_labels.find()]
        self.uncut_resumes = [x for x in db.uncut_resumes.find()]

    def load_df(self):
    	db = self.connect_to_mongo()
    	temp_resume = [x for x in db.resumes.find()]
    	self.resumes = pd.DataFrame([self.add_resume_id(row, resume["resume_id"]) for resume in temp_resume for row in resume['resume_data']])
        self.resume_labels = [x for x in db.resume_labels.find()]
        self.uncut_resumes = [x for x in db.uncut_resumes.find()]

    def load_company_name(self):
        temp_company_list = db.company.find()
        temp_ziheng_company_list = db.ziheng_company.find()
        company_list = company_list + [x['company_name'] for x in temp_ziheng_company_list]
        company_list = filter(lambda x:re.search(ur"[\u4e00-\u9fa5]",x),set(company_list + [x['company_name'] for x in temp_company_list][:100000]))


        temp_resumes = resumes.copy() # the following 4 lines move one tab left
        temp_resumes["company"] = temp_resume["tag_label"].map(lambda x: (True if "company" in x else False))
        self.company_name_negative = temp_resumes[temp_resumes["company"] == False]
        self.company_name_positive = temp_resumes[temp_resumes["company"] == True]



