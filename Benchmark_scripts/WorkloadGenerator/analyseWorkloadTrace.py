import csv
import datetime
import matplotlib.pyplot as plt
import random

# website used for debugging
# https://timestamp.online/

core_count = []
runtime = []
cpu_utilization = []
timestamp = []
lines_used = 0
lines_total = 0

for x in range(0,100):
    print(random.gauss(33, 2))
    

for x in range(0, 24):
    runtime.append([])
    core_count.append([])
    cpu_utilization.append([])
    timestamp.append([]) #variable only used for debugging purposes

with open("anon_jobs.gwf") as file:
    tsv_file = csv.reader(file, delimiter="\t")
    # skip the header part
    fieldcount = 0
    while int(fieldcount) < 29:
        fieldcount = int(len(next(tsv_file)))

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
time_of_day = []
i = 0
for jobs in core_count:
    time_of_day.append(i)
    job_count.append(len(jobs))
    i = i+1



def calculate_avg_hour_usage(list):
    avg_frame = []
    for hour_frame in list:
        sum = 0.0
        for element in hour_frame:
            sum = sum + float(element)
        avg = float(sum) / float(len(hour_frame))
        avg_frame.append(avg)
    return avg_frame


# gain statistical data:
core_count_avg_hour = calculate_avg_hour_usage(core_count)
runtime_avg_hour = calculate_avg_hour_usage(runtime)
cpu_utilization_avg_hour = calculate_avg_hour_usage(cpu_utilization)


print("Valid lines", lines_used, " of total", lines_total, " lines with usage percentage of ", float(lines_used)*100/float(lines_total), "%")

print("average Core Count per hour: ", core_count_avg_hour)
print("average runtime per Hour: ", runtime_avg_hour)
print("cpu utilization avg per Hour: ", cpu_utilization_avg_hour) #unusable
print("job count per hour", job_count)
print("time axis", time_of_day)


def generate_bar_plot(xaxis, yaxis, title):
    fig = plt.figure()
    fig.canvas.manager.set_window_title(title)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.bar(xaxis, yaxis)
    plt.show()


generate_bar_plot(time_of_day, core_count_avg_hour, "average core count per hour")
generate_bar_plot(time_of_day, runtime_avg_hour, "average runtime per hour")
generate_bar_plot(time_of_day, job_count, "average job count per hour")


### Block to generate the workflow list

milicores_total = 2000
maximum_jobs = 100
utilization = 0.6
maximum_runtime = 3600 #one Hour


avg_milicore_per_job = (milicores_total / maximum_jobs) / utilization

print("Debug", avg_milicore_per_job)


# mit gaus funktion generieren der benchmarks
# https://www.geeksforgeeks.org/random-gauss-function-in-python/