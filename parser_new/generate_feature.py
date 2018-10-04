# -*- coding: utf-8 -*-

import pandas as pd
import jieba
import re
from regex.time_reg import *
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )
import pynlpir

class generate_feature(object):
    def __init__(self, data_df, stopword_path = "data/stop_words.txt"):
        self.stoplist = set(open(stopword_path).read().decode("utf8","ignore").split("\n"))
        self.data_df = data_df

    def add_new_words(self):
        self.data_df['new_text'] = self.data_df["text"].map(lambda x: ("".join(re.findall(ur'[a-zA-Z\u4e00-\u9fff]+', x))).strip())

    def add_token_words(self):
        self.data_df['token_words'] = self.data_df['new_text'].map(lambda x: [y for y in jieba.lcut(x, cut_all=False)])

    def add_time(self):
        self.data_df['contain_date'] = self.data_df['text'].str.contains(u"((?:19|20)\d{2})([-./\u5e74]?)((?:[0-1]?|1)[0-9])?([-./\u6708]?)((?:[0-3]?|[1-3])?[0-9])?(?:$|\D)").map(lambda x: True if x else False)

    def add_row_length(self):
        def _cal_length(text):
            if len(text) <= 5:
                return "5_char_less"
            elif len(text) >=15:
                return "15_char_more"
            else:
                return "15_char_less"
        self.data_df['text_length'] = self.data_df['text'].map(lambda x: _cal_length(x))
        self.data_df['text_length_previous'] = self.data_df.groupby('resume_id')['text_length']. \
            shift(periods=1).fillna('')
        self.data_df['text_length_next'] = self.data_df.groupby('resume_id')['text_length'].\
            shift(periods=-1).fillna('')

    def add_row_position(self):
        def _cal_position(position):
            if position <= 0.25:
                return "position_1"
            elif position <= 0.5:
                return "position_2"
            elif position <= 0.75:
                return "position_3"
            else:
                return "position_4"
        self.data_df['row_position'] = self.data_df.groupby(['resume_id'])['row'].transform(lambda x: x / x.max())
        self.data_df['row_position'] = self.data_df['row_position'].map(lambda x: _cal_position(x))

    def add_pos(self):
        pynlpir.open() #tell NLPIR to open the data files and initialize the API
        def _cal_pos(row):
            try:
                segments = pynlpir.segment(row, pos_names='all')
                return segments
            except Exception as e:
                return [(row, "None")]
        # remove '\u3000' in uncut resume
        # self.data_df["pos_text"] = self.data_df["new_text"].map(lambda x: x.replace(u"\u3000", ""))
        # self.data_df['pos'] = self.data_df["pos_text"].map(lambda x: _cal_pos(x))
        self.data_df['pos'] = self.data_df["new_text"].map(lambda x: _cal_pos(x))
        self.data_df['token_words'] = self.data_df['pos'].map(lambda x: [y[0] for y in x])
        pynlpir.close()

    def add_person_name(self):
        def _cal_person_name(row):
            result = [x[0] for x in row["pos"] if x[1] in [u'noun:personal name']]
            return [result, float(len("".join(result)))/len(row["text"])]
        self.data_df["person_name"] = self.data_df.apply(lambda x: _cal_person_name(x), axis = 1)

    def add_location(self):
        def _cal_location(row):
            result = [x[0] for x in row["pos"] if x[1] in [u'noun:toponym', u'noun:toponym:transcribed toponym']]
            return [result, float(len("".join(result)))/len(row["text"])]
        self.data_df["location"] = self.data_df.apply(lambda x: _cal_location(x), axis = 1)

    def add_crf_feature(self):
        self.add_new_words()
        # self.add_token_words()
        self.add_time()
        self.add_row_length()
        self.add_row_position()
        # self.data_df['crf_token_word'] = self.data_df['token_words'].map(lambda x:
        #     [y for y in x if y not in self.stoplist])
        self.add_pos()
        self.data_df['crf_token_word'] = self.data_df['pos'].map(lambda x: [segment[0] + ' '\
            + str(segment[1]) for segment in x])
        self.data_df['crf_feature'] = self.data_df.apply(lambda x: x["crf_token_word"] + \
            ["current: " + x["text_length"], \
            "previous: " + x["text_length_previous"], \
            "next: " + x["text_length_next"],
            x["row_position"],
            ("contain_date" if x["contain_date"] else "not_contain_date")], axis=1)