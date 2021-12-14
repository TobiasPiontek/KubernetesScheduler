import csv
import datetime

#https://timestamp.online/

i = 0
skip = 52 #lines to skip out of the .gwf file
core_count=[]
runtime=[]
cpu_utilization=[]
timestamp=[]


for x in range(0, 24):
    runtime.append([])
    core_count.append([])
    cpu_utilization.append([])
    timestamp.append([])
print("list size: ")
print(core_count)

with open("anon_jobs.gwf") as file:
    tsv_file = csv.reader(file, delimiter="\t")
    #skip the header part
    for x in range(0, skip):
        next(tsv_file)
    #iterate over main data
    for line in tsv_file:
        #print(line.__getitem__(0))
        hour = datetime.datetime.fromtimestamp(int(line.__getitem__(1))).hour
        #print(datetime.datetime.fromtimestamp(int(line.__getitem__(1))).strftime('%Y-%m-%d %H:%M:%S'))
        timestamp[hour].append(datetime.datetime.fromtimestamp(int(line.__getitem__(1))).strftime('%Y-%m-%d %H:%M:%S'))
        core_count[hour].append(line.__getitem__(4))
        runtime[hour].append(line.__getitem__(3))
        cpu_utilization[hour].append(line.__getitem__(5))




    #print(timestamp[2].__getitem__(0))
    #print(cpu_utilization[2].__getitem__(0))
    #print(timestamp[3].__getitem__(0))
    #print(cpu_utilization[3].__getitem__(0))
    #print(timestamp[16].__getitem__(0))
    #print(cpu_utilization[16].__getitem__(0))

