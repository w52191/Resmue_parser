import numpy as np
import re, os

def Check_below(n_row, dta, i):
    result = str()
    for row in range(n_row):
        try:
            detect = re.findall(ur'[\u4e00-\u9fff]+', dta[i+row].decode('utf-8'))
            if detect != []:
                result = dta[i]
        except: pass
    if len(result) == 0:
        return('')
    else: return(result)


file_path = '/Users/Kay/Desktop/entropy/parser/docs/sample_resume/'
output_path = '/Users/Kay/Desktop/result/'

for document in os.listdir(file_path):
    document_path = file_path + document
    with open(document_path,'rb') as g:
        a = g.readlines()

        # delete the \n
        space = [' \n', '\n', '!\n']
        I = [i for i,j in enumerate(a) if a[i] in space]
        a = np.delete(a,I).tolist()

        output_file = output_path + document
        with open(output_file,'ab') as textfile:
            for i in range(len(a)):
                if re.findall(ur'[\u4e00-\u9fff]+', a[i].decode('utf-8')):
                    textfile.write(a[i])
                elif re.findall(ur'@', a[i].decode('utf-8')):
                    textfile.write(a[i])
                elif re.findall(ur'[0-9]+', a[i].decode('utf-8')):
                    textfile.write(Check_below(3,a,i))
                else: pass