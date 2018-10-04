#!/usr/bin/env python
# -*- coding: utf-8 -*-
from tika import parser
import os
import sys
import numpy as np
import re
import pandas as pd
# import magic

class preprocess_resume(object):
    def __init__(self, document_path, tika_server = "http://localhost:9998/"):
        self.document_path = document_path
        assert os.path.isfile(self.document_path)
        self.tika_server = tika_server

    def parse_pdf_to_txt(self):
        os.system("pdftotext " + self.document_path+ " " + ((self.output_path+'/%s_temp.txt') % os.path.splitext(document)[0]))

    def parse_tika(self):
        parsed = parser.from_file(self.document_path, self.tika_server)['content']
        parsed = [x.strip() for x in parsed.split("\n") if x.strip() != u""]
        return parsed
        
    def check_below(self, n_row, dta, i):
        result = str()
        for row in range(n_row):
            try:
                detect = re.findall(ur'[\u4e00-\u9fff]+', dta[i+row])
                if detect != []:
                    result = dta[i]
            except: 
                pass
        if len(result) == 0:
            return('')
        else: 
            return(result)
    
    def del_en(self, rows):
        output_list = []
        for i in range(len(rows)):
            if re.findall(ur'[\u4e00-\u9fff]+', rows[i]):
                output_list.append(rows[i])
            elif re.findall(ur'@', rows[i]):
                output_list.append(rows[i])
            elif re.findall(ur'[0-9]+', rows[i]):
                output_list.append(self.check_below(3,rows,i)) #? wt
            else: 
                pass
        return output_list

    def reformat_doc(self, content_list):
        split_re = u"；|、|\||\/|\ufe31|\u3001|\uff1a|\uff0c|;|】|【|，|。|！|？|：|\\n|,|:|\\s+|\\t+|[　]+"
        content_split = re.split(split_re, "\n".join(content_list))
        new_content_split = []
        cache_list = []
        for item in content_split:
            if len(item.strip()) > 1:#? wt
                if len(cache_list) != 0:
                    new_content_split.append("".join(cache_list))
                    cache_list = []
                new_content_split.append(item)
            elif len(item.strip()) == 1:
                cache_list.append(item)
        if len(cache_list) != 0:
            new_content_split.append("".join(cache_list))
        return new_content_split

    def process(self):
        try:
            content_list = self.reformat_doc(self.del_en(self.parse_tika()))
            self.content_df = pd.DataFrame(content_list, columns = ["text"])
            file_name = os.path.basename(self.document_path)
            n_row = len(self.content_df)
            self.content_df["resume_id"] = [file_name for x in range(n_row)]
            self.content_df["row"] = range(1, n_row+1)
            return self.content_df
        except Exception as e:
            print e
            print self.document_path
            return None

    def write(self, output_path):
        output_data = self.content_df
        output_data["output_text"] = output_data["text"].map(lambda x: x.encode("UTF-8"))
        output_data[["output_text"]].to_csv(output_path, header = None, index = None, sep = "\t", mode = 'wb')
        


# if __name__ == "__main__":
#   temp = preprocess_resume('/Users/Kay/Desktop/testusjackal', '/Users/Kay/Desktop/test-txt', "bulk")
#   temp.process()

if __name__ == "__main__":#wt
    temp = preprocess_resume('C:/Users/wangt/Desktop/test.pdf')
    content_list = temp.process()
    content_list
    #content_list.to_csv('names', encoding='utf-8')
    