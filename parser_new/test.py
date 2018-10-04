import sys
# sys.path.insert(0,'..')
from load_training_data import *
import pandas as pd
from sklearn.metrics import confusion_matrix
from generate_feature import *
from classifier.label_crf_classifier import *

class test(object):
    def __init__(self):
        resume = load_training_data("52.220.88.110")
        resume.load_df()
        self.resume_df = resume.resumes
        self.resume_df['text_previous'] = self.resume_df.groupby('resume_id')['text'].shift(periods=1).fillna('')
        self.resume_df['text_next'] = self.resume_df.groupby('resume_id')['text'].shift(periods=-1).fillna('')
        self.metrics = {}

    def test_tag_re(self, tag, test_function):
        self.metrics = {}
        temp_resume_df = self.resume_df.copy()
        temp_resume_df["filter_tag"] = temp_resume_df["tag_label"].map(lambda x: (True if tag in x else False))
        temp_resume_df["predicted_tag"] = temp_resume_df["text"].map(lambda x: test_function(x))
        temp_resume_df['diff'] = temp_resume_df.apply(lambda row: (1 if row["filter_tag"] != row["predicted_tag"] else 0), axis=1)
        temp_resume_df = temp_resume_df[temp_resume_df["section_label"].str.contains(section)]
        resume_filtered = temp_resume_df[temp_resume_df["diff"] == 1]
        self.metrics["OR"] = temp_resume_df
        self.metrics["FP"] = resume_filtered[resume_filtered["predicted_tag"] == True]
        self.metrics["FN"] = resume_filtered[resume_filtered["predicted_tag"] == False]
        self.metrics["CM"] = confusion_matrix(temp_resume_df["filter_tag"].tolist(), temp_resume_df["predicted_tag"].tolist(), labels=[True, False])
        self.metrics["AS"] = float(self.metrics["CM"][0][0] + self.metrics["CM"][1][1]) / sum(sum(self.metrics["CM"]))

    def test_tag_clf(self, tag, section, test_function):
        self.metrics = {}
        temp_resume_df = self.resume_df.copy()
        gf_class = generate_feature(temp_resume_df)
        gf_class.add_crf_feature()
        temp_resume_df = gf_class.data_df
        # temp_resume_df = temp_resume_df[temp_resume_df["section_label"].str.contains(section)]
        temp_resume_df["filter_tag"] = temp_resume_df["tag_label"].map(lambda x: (True if tag in x else False))
        temp_resume_df["predicted_tag"] = temp_resume_df.apply(lambda x: test_function(x), axis = 1)
        temp_resume_df['diff'] = temp_resume_df.apply(lambda row: (1 if row["filter_tag"] != row["predicted_tag"] else 0), axis=1)
        resume_filtered = temp_resume_df[temp_resume_df["diff"] == 1]
        self.metrics["OR"] = temp_resume_df 
        self.metrics["FP"] = resume_filtered[resume_filtered["predicted_tag"] == True]
        self.metrics["FN"] = resume_filtered[resume_filtered["predicted_tag"] == False]
        self.metrics["CM"] = confusion_matrix(temp_resume_df["filter_tag"].tolist(), temp_resume_df["predicted_tag"].tolist(), labels=[True, False])
        self.metrics["AS"] = float(self.metrics["CM"][0][0] + self.metrics["CM"][1][1]) / sum(sum(self.metrics["CM"]))

    def test_section(self, portion=0.8, c1=0, c2=10, period=300, minfreq=10):
        self.metrics = {}
        # add short label
        temp_resume_df = self.resume_df.copy()
        # generate_features
        gf_class = generate_feature(temp_resume_df)
        gf_class.add_crf_feature()
        temp_resume_df = gf_class.data_df
        # split resume_id
        resume_ids = temp_resume_df['resume_id'].unique()
        id_length = len(resume_ids)
        shuffle(resume_ids)
        train_ids = resume_ids[:int(id_length*portion)]
        test_ids = resume_ids[int(id_length*portion):]
        train_df = temp_resume_df[temp_resume_df['resume_id'].isin(train_ids)]
        test_df = temp_resume_df[temp_resume_df['resume_id'].isin(test_ids)]
        test_df["section_label_true"] = test_df["section_label"].tolist()

        # train model on train_ids
        crf_class = label_crf_classifier()
        crf_class.train(train_df, c1=c1, c2=c2, period=period, minfreq=minfreq)
        test_pred = test_df.groupby("resume_id").apply(lambda x: crf_class.predict(x))
        test_pred = test_pred.rename(columns={'section_label': 'predicted_label', 'section_label_true': 'filter_label'})
        test_pred = test_pred[['resume_id', u'row',  'new_text', 'token_words', u'text', 'filter_label', 'predicted_label']]
        test_pred = test_pred[test_pred["filter_label"] != ""]
        test_pred['diff'] = test_pred.apply(lambda row: (1 if row["filter_label"] != row["predicted_label"] else 0), axis=1)
        self.metrics["result"] = test_pred
        self.metrics["CM"] = confusion_matrix([x[-1:] for x in test_pred["filter_label"].tolist()], [x[-1:] for x in test_pred["predicted_label"].tolist()], labels=["0", "1", "2", "3", "4", "5"])
        self.metrics["AS"] = 1- float(sum(test_pred["diff"].tolist())) / len(test_pred["diff"].tolist())
        # train_pred = crf_class.predict(train_df)

        # print out result
        # return train_pred, test_pred

# [["resume_id","row", "text", "pos", "predicted_tag"]].to_csv("/Users/ke.shen/Desktop/name.txt", encoding = "UTF-8")
