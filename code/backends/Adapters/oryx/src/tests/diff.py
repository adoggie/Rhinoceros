#coding:utf-8

"""
diff.py
筛选出yto合同车辆未在现有监控列表中的清单

"""
import os.path
import json

covered_file='select__DISTINCT__id__as_id__from_mo_dat_20170511.json'
yto_file = 'yto_contract_vehicles_20170511.txt'
uncoverd_file='uncovered_vehicles.txt'
incoverd_file='covered_vehicles.txt'

covered_list = json.loads(open(covered_file).read())
covered_list = map(lambda _:_['id'],covered_list)
print len(covered_list )

yto_list = map(lambda _: _.decode('utf-8').strip(),open(yto_file).read().split('\r')[1:])

yto_file = filter(lambda _: len(_)>0,yto_file)

print covered_list[0]
print yto_list[0]
hit = []
unhit= []
for yto in yto_list:
    if covered_list.count(yto):
       hit.append(yto)
    else:
        unhit.append(yto)

print 'hit objects:',len(hit)
print 'unhit objects:',len(unhit)

fp = open(uncoverd_file,'w')
for _ in unhit:
    fp.write("%s\n"%_.encode('utf-8'))

fp = open(incoverd_file,'w')
for _ in hit:
    fp.write("%s\n"%_.encode('utf-8'))



