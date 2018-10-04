from tika import parser
import os

def parse_tika(document, output_path):
    '''
    input: document name
    return: txt format name
    '''
    parsed = parser.from_file(document)
    parsed = parsed['content'].encode('utf-8')
    f = open((output_path+'/%s.txt') % os.path.splitext(document)[0], "wb")
    f.write(parsed)
    f.close()


file_path = '/Users/Kay/Desktop'
output_path = '/Users/Kay/Desktop/resume-txt'
os.chdir(file_path)
resumes = os.listdir(file_path)


for document in resumes:
    try:
        parse_tika(document, output_path)
    except Exception as e:
        print e
        print document
    