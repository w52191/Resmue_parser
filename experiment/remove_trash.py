import os
from shutil import copyfile

file_path = '/Users/kshen/github/parser/docs/sample_resume_new/' # files that have deleted the english part
out_path = "/Users/kshen/Desktop/sample_resume_new/"
split_re = "；|;|，|。|！|？|：|\\n|,|:|\\s+|\\t+|[　]+"

total = {}
for document in os.listdir(file_path):
if document.split('.')[1] == 'txt':
    document_path = file_path + document
    document_name = document.split('.')[0]
    with open(document_path,'rb') as g:
        content = g.read().decode("utf8","ignore").strip()
        content_split = re.split(split_re, content)
        if len(content_split) > 10:
             copyfile(document_path, out_path + document_name + ".txt")
