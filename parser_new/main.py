from utility.utilities import *
import load_training_data
import preprocess_resume
import segmentation
import generate_feature
# import parse_basic_info
# import parse_education
# import parse_work_experience
# import numpy as np
# import pandas as pd
import sys
import os

class main(object):
    def __init__(self, config_type):
        package_path = os.path.dirname(os.path.abspath(__file__))
        sys.path.append(package_path)
        self.config = load_config(config_type)
        self.segmentation_class = segmentation.segmentation("keyword")

    def filter_section(self, section_name):
        return filter(lambda d: section_name in d['section'], self.resume_df)

    def train(self):
        training_data = load_training_data.load_training_data(self.config["mongodb"]["server"])
        print "loading training data ..."
        training_data.load_df()
        self.resumes = training_data.resumes
        self.resume_labels = training_data.resume_labels
        self.uncut_resumes = training_data.uncut_resumes
        generate_feature_class = generate_feature.generate_feature(self.resumes)
        generate_feature_class.add_crf_feature()
        resume_df = generate_feature_class.data_df
        return resume_df
        # print "training labels ..."
        # self.segmentation_class.train(self.resumes)

    def load_classifier(self):
        self.segmentation_class.load_classifier()

    def predict(self, input_path, method = "single"):
        print "preprocessing resume"
        preprocess_object = preprocess_resume.preprocess_resume(input_path)
        resume_df = preprocess_object.process()
        print "generating features"
        generate_feature_class = generate_feature.generate_feature(resume_df)
        # generate_feature_class.add_pos()
        # generate_feature_class.add_person_name()
        # generate_feature_class.add_location()
        generate_feature_class.add_crf_feature()
        resume_df = generate_feature_class.data_df
        # print "segmentation"
        # resume_df = self.segmentation_class.predict(resume_df)
        return resume_df


    # def process(self):
    #   print "preprocessing..."
    #   preprocess_object = preprocess_resume.preprocess_resume(self.filename, self.filename_txt, "single")
    #   preprocess_object.process()
    #   print "segmentation..."
    #   self.resume_df = segmentation.segmentation(self.filename_txt + preprocess_object.docs[0]+".txt", self.re_train).cut()
    #   print "basic info"
    #   self.parse_basic_info = parse_basic_info.parse_basic_info(self.filter_section('basic_info')).parse_basic_info_main()
    #   print "education"
    #   self.parse_education = parse_education.parse_education(self.filter_section('education')).parse_education_main()
    #   print "work experience"
    #   self.parse_work_experience = parse_work_experience.parse_work_experience(self.filter_section('work_experience'), self.re_train).parse_work_experience_main()
    #   self.s = pd.DataFrame(self.resume_df)
        
# if __name__ == "__main__":
#   os.system('rm -r ../tmp/*')
#   pd.set_option('display.max_rows', 1000)
#   temp = main("/Users/Kay/Desktop/03a3d9de52658a8be25bf3c78b310b83", re_train = False)
#   temp.process()
#   sys.stdout = open("../tmp/result.txt", "wb")
#   print len(temp.resume_df)
#   for item in temp.resume_df:
#       if len(item['label']) > 0:
#           print item['text'].encode('UTF-8') + "  <------ " + ", ".join(item['label'])
#       else:
#           print item['text'].encode('UTF-8')
#   sys.stdout.close()

# if __name__ == "__main__":
#     os.system('rm -r ../tmp/*')
#     pd.set_option('display.max_rows', 1000)
#     file_dir = "/Users/kshen/Desktop/testusjackal/"
#     # output_dir = "/Users/Kay/Desktop/testusjackal_output/"
#     files = os.listdir(file_dir)
#     for doc_name in files:
#         try:
#             temp = main(file_dir + doc_name, re_train = False)
#             temp.process()
#             sys.stdout = open("../tmp/" + doc_name + ".txt", "wb")
#             # print len(temp.resume_df)
#             for item in temp.resume_df:
#                 if len(item['label']) > 0 and item['label'][0] in ["basic_info_label", "education_label", "work_experience_label", "social_experience_label", "project_experience_label", "training_experience_label"]:
#                     print "-------------------"
#                     print item['label'][0]
#                     print "-------------------"
#                     print item['text'].encode('UTF-8')
#                     print "*******************"
#                 elif len(item['label']) > 0:
#                     print item['text'].encode('UTF-8') + "  <------ " + ", ".join(item['label'])
#                 else:
#                     print item['text'].encode('UTF-8')
#             sys.stdout.close()
#         except Exception as e:
#             print e
#             continue
