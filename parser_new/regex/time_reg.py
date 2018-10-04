#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

def parse_time(row):
    time_rex = u"((?:19|20)\d{2})([-./\u5e74]?)((?:[0-1]?|1)[0-9])?([-./\u6708]?)((?:[0-3]?|[1-3])?[0-9])?(?:$|\D)"
    until_now_rex = u"至今|今|现在|预计"
    temp_index = re.findall(time_rex, row)
    until_now_index = re.findall(until_now_rex, row)
    if temp_index:
        return True
    else:
        return False
    # if temp_index:
    #   # return True
    #   time_part = [len("".join(x)) for x in (temp_index + until_now_index)]
    #   return float(sum(time_part))/len(row)
    # else:
    #   return 0.0