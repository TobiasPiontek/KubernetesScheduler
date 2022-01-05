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

intervallcount = 24




for x in range(0, intervallcount):
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
    plt.bar(xaxis,yaxis)
    plt.show()


#Plots about the analyzed .gwf file
generate_bar_plot(time_of_day, core_count_avg_hour, "average core count per hour")
generate_bar_plot(time_of_day, runtime_avg_hour, "average runtime per hour")
generate_bar_plot(time_of_day, job_count, "average job count per hour")


### Block to generate the workflow list
#generate total sum of hourly distributions
sum_core=0
sum_runtime=0
sum_job_count=0
for x in range(0, intervallcount):
    sum_core = sum_core + core_count_avg_hour.__getitem__(x)
    sum_runtime = sum_runtime + runtime_avg_hour.__getitem__(x)
    sum_job_count = sum_job_count + job_count.__getitem__(x)

#generate normalized utilizations
core_count_normalized = []
runtime_normalized = []
job_count_normalized = []

for x in range(0, intervallcount):
    core_count_normalized.append(core_count_avg_hour.__getitem__(x)*intervallcount/sum_core)
    runtime_normalized.append(runtime_avg_hour.__getitem__(x)*intervallcount/sum_runtime)
    job_count_normalized.append(job_count.__getitem__(x)*intervallcount/sum_job_count)

generate_bar_plot(time_of_day, core_count_normalized, "average core count per hour")
generate_bar_plot(time_of_day, runtime_normalized, "average runtime per hour")
generate_bar_plot(time_of_day, job_count_normalized, "average job count per hour")

#generate the average values that get modified
milicores_total = 1250
maximum_jobs = 100
avg_utilization = 0.8
average_runtime = 600 #10 minutes
avg_job_interval_hour = float(3600) / (float(maximum_jobs) * avg_utilization * (3600 / float(average_runtime)))
avg_milicore_per_job = (milicores_total / maximum_jobs) * avg_utilization


print("avg job interval", avg_job_interval_hour)
print("Debug", avg_milicore_per_job)


#Block to write the csv file

f = open('workload.csv', 'w', newline='')
writer = csv.writer(f, lineterminator="\n") #use linux style line endings


print("start writing workload file...")

time_counter = 0
while time_counter < 86400: #generate for whole day
    label = ""
    if random.random() > 0.9:
        label="not-critical"
    else:
        label="critical"
    write_data = [str(int(avg_milicore_per_job)), str(int(average_runtime)), str(int(avg_job_interval_hour)), label]
    print(write_data)
    writer.writerow(write_data)
    time_counter = int(time_counter) + int(avg_job_interval_hour)

f.close()

print("done!")

# mit gaus funktion generieren der benchmarks
# https://www.geeksforgeeks.org/random-gauss-function-in-python/

#for x in range(0,100):
#    print(random.gauss(33, 2))