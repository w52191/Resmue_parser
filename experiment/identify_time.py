# -*- coding: utf-8 -*-
import re

time_rex = u"((?:19|20)\d{2})[-./\u5e74]?((?:[0-1]?|1)[0-9])?[-./\u6708]?((?:[0-3]?|[1-3])?[0-9])?[^\d]"


rows = [u"32016年1月12日", u"2016年1月", u"2016年", u"1998-09-11", u"1979/08/17", u"1989.08", u"1989 /08", u"123121989091", u"宁波诺丁汉大学"]
for row in rows:
	temp_index = re.search(time_rex, row)
	if temp_index:
		print row
