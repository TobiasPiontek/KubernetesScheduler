import csv
import datetime

# website used for debugging
# https://timestamp.online/

skip = 52  # lines to skip out of the .gwf file, needs to be recalibrated for each file
core_count = []
runtime = []
cpu_utilization = []
timestamp = []
lines_used = 0
lines_total = 0

for x in range(0, 24):
    runtime.append([])
    core_count.append([])
    cpu_utilization.append([])
    timestamp.append([]) #variable only used for debugging purposes

with open("anon_jobs.gwf") as file:
    tsv_file = csv.reader(file, delimiter="\t")
    # skip the header part
    for x in range(0, skip):
        next(tsv_file)
    # iterate over .gwf data
    for line in tsv_file:
        lines_total = lines_total + 1
        if (float(line.__getitem__(3)) > -0.5) and (float(line.__getitem__(4)) > -0.5) and float(line.__getitem__(5)) > -0.5:
            lines_used = lines_used + 1
            hour = datetime.datetime.fromtimestamp(int(line.__getitem__(1))).hour
            # print(datetime.datetime.fromtimestamp(int(line.__getitem__(1))).strftime('%Y-%m-%d %H:%M:%S'))
            timestamp[hour].append(datetime.datetime.fromtimestamp(int(line.__getitem__(1))).strftime('%Y-%m-%d %H:%M:%S'))
            core_count[hour].append(line.__getitem__(4))
            runtime[hour].append(line.__getitem__(3))
            cpu_utilization[hour].append(line.__getitem__(5))


            #debug block to show inconsistency in data set:
            #gwf 10 file entry: 2341 runtime= 140, cputime=239.89 (should be divided on corecount and cant therefore be greater than runtime)
            #if float(line.__getitem__(5)) > float(line.__getitem__(3)):
                #print("Debug", lines_total)




job_count = []

def calculate_avg_hour_usage(list):
    avg_frame = []
    for hour_frame in list:
        job_count.append(len(hour_frame))
        sum = 0.0
        for element in hour_frame:
            sum = sum + float(element)
        avg = float(sum) / float(len(hour_frame))
        avg_frame.append(avg)
    return avg_frame


# gain statistical data:
core_count_avg_hour = calculate_avg_hour_usage(core_count)
runtime_avg_hour = [calculate_avg_hour_usage(runtime)]
cpu_utilization_avg_hour = [calculate_avg_hour_usage(cpu_utilization)]


print("Valid lines", lines_used, " of total", lines_total, " lines with usage percentage of ", float(lines_used)*100/float(lines_total), "%")

print("average Core Count per hour: ", core_count_avg_hour)
print("average runtime per Hour: ", runtime_avg_hour)
print("cpu utilization avg per Hour: ", cpu_utilization_avg_hour) #unusable
print("job count per hour", job_count)

