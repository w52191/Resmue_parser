import os
from shutil import copyfile

file_path = '/Users/kshen/Desktop/output_1_temp/' # files that have deleted the english part
out_path = "/Users/kshen/Desktop/output_2_no_dup/"

total = {}
for document in os.listdir(file_path):
    if document.split('.')[1] == 'txt':
        document_path = file_path + document
        document_name = document.split('.')[0]
        with open(document_path,'rb') as g:
            a = g.read()
            total[document_name] = a

rm_file = [0 for x in range(len(total)+10000)]
for i in total.keys():
    if rm_file[int(i)] == 0:
        for j in total.keys():
            if int(i) < int(j) and rm_file[int(j)] == 0:
                if total[i] == total[j]:
                    rm_file[int(j)] = 1

for i in range(len(rm_file)):
    file_name = file_path + str(i) + ".txt"
    if os.path.isfile(file_name) and rm_file[i] == 0:
        copyfile(file_name, out_path + str(i) + ".txt")