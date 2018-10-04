import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )
import pynlpir

def parse_location(self, row):
	temp_index = False
	try:
		segments = pynlpir.segment(row, pos_names='all')
	except Exception as e:
		return temp_index
	temp_count = len("".join([x[0] for x in segments if x[1] in [u'noun:toponym', u'noun:toponym:transcribed toponym']]))
	if float(temp_count)/len(row) >= 0.5:
		return True 
	else:
		return False