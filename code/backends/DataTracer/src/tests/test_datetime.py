#coding:utf-8

import datetime
import datetime

def get_across_days(start,end):
    s = datetime.datetime.fromtimestamp(start)
    e = datetime.datetime.fromtimestamp(end)
    days = e.date() - s.date()
    result=[]
    s = datetime.datetime(s.year,s.month,s.day)
    for _ in range(days.days+1):
        day = s + datetime.timedelta(_)
        result.append(day)
    return result


if __name__ == '__main__':
    print get_across_days(1490702667-3600*24,1493732667)