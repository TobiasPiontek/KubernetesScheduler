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


def generate_bar_plot(x_axis, y_axis, title):
    fig = plt.figure()
    fig.canvas.manager.set_window_title(title)
    plt.bar(x_axis, y_axis)
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

# cluster parameters
total_millicores = 4000
system_reserved_millicores = 750

#workload calibration parameters
average_pod_count = 50
avg_utilization = 0.6
average_runtime = 600 #10 minutes
rate_of_critical_jobs = 0.8 #rate of critical jobs, a reduction of this percentage leads to more shiftable workload, thus more optimization potential

#parameter for benchmark calibration
start_time = 1 #hour, at which the benchmark run starts 1 equal 01:00, 13 equals 13:00

#pre calculated values for later use
milli_cores_available = total_millicores - system_reserved_millicores   # this values is picked since 750 mcores are system reserved
avg_job_interval_hour = float(3600) / (float(average_pod_count) * avg_utilization * (3600 / float(average_runtime)))
avg_milli_core_per_job = (milli_cores_available / average_pod_count) * avg_utilization


print("avg job interval", avg_job_interval_hour)
print("Debug", avg_milli_core_per_job)



print("generating prediction grap...")
predicted_load = []
predicted_pod_count = []
predicted_hour_timestamp = []
milli_core_adapted = []
runtime_adapted = []
job_interval_adapted = []
file_prediction = open('workload_prediction.csv', 'w', newline='')
writer_prediction = csv.writer(file_prediction, lineterminator="\n") #use linux style line endings
for x in range(0, 24):
    milli_core_adapted.append(avg_milli_core_per_job * core_count_normalized[x])
    runtime_adapted.append(average_runtime * runtime_normalized[x])
    job_interval_adapted.append(int(avg_job_interval_hour * (1 / job_count_normalized[x]))) # invert value, as many jobs per hour mean low latency between job queue intervall
    predicted_load.append(((runtime_adapted[x] / job_interval_adapted[x]) * milli_core_adapted[x] + system_reserved_millicores) / total_millicores)
    predicted_pod_count.append(runtime_adapted[x] / job_interval_adapted[x])
    predicted_hour_timestamp.append(x)
    row = [predicted_load[x]]
    writer_prediction.writerow(row)

file_prediction.close()
generate_bar_plot(predicted_hour_timestamp, predicted_load, "Unoptimized load prediction")
generate_bar_plot(predicted_hour_timestamp, predicted_pod_count, "Predicted Pod count per hour")



#Block to write the csv file
print("start writing workload file...")
f = open('workload.csv', 'w', newline='')
writer = csv.writer(f, lineterminator="\n") #use linux style line endings

time_counter = 0
while time_counter < 86400: #generate for whole day
    #calculating adapted values
    current_hour = int(time_counter / 3600)
    adapted_hour = (current_hour + start_time) % 24


    print("current hour: " + str(adapted_hour))
    print("job interval adapted: " + str(job_interval_adapted[adapted_hour]))

    label = ""
    if random.random() > rate_of_critical_jobs:
        label = "not-critical"
    else:
        label = "critical"
    write_data = [str(int(milli_core_adapted[adapted_hour])), str(int(runtime_adapted[adapted_hour])), str(int(job_interval_adapted[adapted_hour])), label]
    print(write_data)
    writer.writerow(write_data)
    time_counter = int(time_counter) + int(job_interval_adapted[adapted_hour])

f.close()

print("done!")

# mit gaus funktion generieren der benchmarks
# https://www.geeksforgeeks.org/random-gauss-function-in-python/

#for x in range(0,100):
#    print(random.gauss(33, 2))