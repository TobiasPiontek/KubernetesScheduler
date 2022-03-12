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

interval_count = 24

# initialize the arrays for analysing workload
for x in range(0, interval_count):
    runtime.append([])
    core_count.append([])
    cpu_utilization.append([])
    timestamp.append([])  # variable only used for debugging purposes

with open("anon_jobs.gwf") as file:
    tsv_file = csv.reader(file, delimiter="\t")
    # skip the header part
    field_count = 0
    while int(field_count) < 29:
        field_count = int(len(next(tsv_file)))

    # iterate over .gwf data

    for line in tsv_file:
        lines_total = lines_total + 1
        if (float(line.__getitem__(3)) > -0.5) and (float(line.__getitem__(4)) > -0.5) and float(
                line.__getitem__(5)) > -0.5:
            lines_used = lines_used + 1
            hour = datetime.datetime.fromtimestamp(int(line.__getitem__(1))).hour
            timestamp[hour].append(
                datetime.datetime.fromtimestamp(int(line.__getitem__(1))).strftime('%Y-%m-%d %H:%M:%S'))
            core_count[hour].append(line.__getitem__(4))
            runtime[hour].append(line.__getitem__(3))
            cpu_utilization[hour].append(line.__getitem__(5))

job_count = []
time_of_day = []
i = 0
for jobs in core_count:
    time_of_day.append(i)
    job_count.append(len(jobs))
    i = i + 1


def calculate_avg_hour_usage(avf_resource):
    avg_frame = []
    for hour_frame in avf_resource:
        resource_sum = 0.0
        for element in hour_frame:
            resource_sum = resource_sum + float(element)
        avg = float(resource_sum) / float(len(hour_frame))
        avg_frame.append(avg)
    return avg_frame


# gain statistical data:
core_count_avg_hour = calculate_avg_hour_usage(core_count)
runtime_avg_hour = calculate_avg_hour_usage(runtime)
cpu_utilization_avg_hour = calculate_avg_hour_usage(cpu_utilization)

print("Valid lines", lines_used, " of total", lines_total, " lines with usage percentage of ",
      float(lines_used) * 100 / float(lines_total), "%")

print("average Core Count per hour: ", core_count_avg_hour)
print("average runtime per Hour: ", runtime_avg_hour)
print("cpu utilization avg per Hour: ", cpu_utilization_avg_hour)  # unusable
print("job count per hour", job_count)
print("time axis", time_of_day)


def generate_bar_plot(x_axis, y_axis, title, x_label, y_label):
    fig = plt.figure()
    fig.canvas.manager.set_window_title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.bar(x_axis, y_axis)
    plt.show()


# Plots about the analyzed .gwf file
generate_bar_plot(time_of_day, core_count_avg_hour, "average core count per hour of workload log", "hour",
                  "average core count")
generate_bar_plot(time_of_day, runtime_avg_hour, "average runtime per hour of workload log", "hour",
                  "average runtime in seconds")
generate_bar_plot(time_of_day, job_count, "average job count per hour of workload log", "hour", "average job count")

# Block to generate the workflow list
# generate total sum of hourly distributions
sum_core = 0
sum_runtime = 0
sum_job_count = 0
for x in range(0, interval_count):
    sum_core = sum_core + core_count_avg_hour.__getitem__(x)
    sum_runtime = sum_runtime + runtime_avg_hour.__getitem__(x)
    sum_job_count = sum_job_count + job_count.__getitem__(x)

# generate normalized utilization
core_count_normalized = []
runtime_normalized = []
job_count_normalized = []

for x in range(0, interval_count):
    core_count_normalized.append(core_count_avg_hour.__getitem__(x) * interval_count / sum_core)
    runtime_normalized.append(runtime_avg_hour.__getitem__(x) * interval_count / sum_runtime)
    job_count_normalized.append(job_count.__getitem__(x) * interval_count / sum_job_count)

# Normalized plots only for debugging
# generate_bar_plot(time_of_day, core_count_normalized, "average core count per hour")
# generate_bar_plot(time_of_day, runtime_normalized, "average runtime per hour")
# generate_bar_plot(time_of_day, job_count_normalized, "average job count per hour")

# generate the average values that get modified

# cluster parameters
total_milli_cores = 4000
system_reserved_milli_cores = 750

# workload calibration parameters
average_pod_count = 50
avg_utilization = 0.6
average_runtime = 60 * 30  # in seconds
rate_of_critical_jobs = 0.6  # rate of critical jobs, that can not be shifted

# parameter for benchmark calibration
start_time = 17  # hour, at which the benchmark run starts 1 equal 01:00, 13 equals 13:00

# pre calculated values for later use
milli_cores_available = total_milli_cores - system_reserved_milli_cores
avg_job_interval = float(average_runtime) / (float(average_pod_count) * avg_utilization)
avg_milli_core_per_job = (milli_cores_available / average_pod_count) * avg_utilization

print("avg job interval", avg_job_interval)
print("Debug", avg_milli_core_per_job)

print("generating prediction graph...")
predicted_load = []
predicted_pod_count = []
predicted_hour_timestamp = []
milli_core_adapted = []
runtime_adapted = []
job_interval_adapted = []
file_prediction = open('workload_prediction.csv', 'w', newline='')
writer_prediction = csv.writer(file_prediction, lineterminator="\n")  # use linux style line endings
for x in range(0, 24):
    milli_core_adapted.append(avg_milli_core_per_job * core_count_normalized[x])
    runtime_adapted.append(average_runtime * runtime_normalized[x])
    job_interval_adapted.append(int(avg_job_interval * (1 / job_count_normalized[x])))
    predicted_load.append(((runtime_adapted[x] / job_interval_adapted[x]) * milli_core_adapted[
        x] + system_reserved_milli_cores) / total_milli_cores)
    predicted_pod_count.append(runtime_adapted[x] / job_interval_adapted[x])
    predicted_hour_timestamp.append(x)
    row = [predicted_load[x]]
    writer_prediction.writerow(row)

file_prediction.close()
generate_bar_plot(predicted_hour_timestamp, predicted_load, "unoptimized load prediction", "hour",
                  "predicted cluster utilization")
generate_bar_plot(predicted_hour_timestamp, predicted_pod_count, "predicted pod count per hour", "hour",
                  "average concurrent pods")

# Block to write the csv file
print("start writing workload file...")
f = open('workload.csv', 'w', newline='')
writer = csv.writer(f, lineterminator="\n")  # use linux style line endings

time_counter = 0
while time_counter < 86400:  # generate for whole day
    # calculating adapted values
    current_hour = int(time_counter / 3600)
    adapted_hour = (current_hour + start_time) % 24

    print("current hour: " + str(adapted_hour))
    print("job interval adapted: " + str(job_interval_adapted[adapted_hour]))

    label = ""
    if random.random() > rate_of_critical_jobs:
        label = "not-critical"
    else:
        label = "critical"
    write_data = [str(int(milli_core_adapted[adapted_hour])), str(int(runtime_adapted[adapted_hour])),
                  str(int(job_interval_adapted[adapted_hour])), label]
    print(write_data)
    writer.writerow(write_data)
    time_counter = int(time_counter) + int(job_interval_adapted[adapted_hour])

f.close()

print("done!")
