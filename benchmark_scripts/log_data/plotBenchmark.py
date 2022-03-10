import matplotlib.pyplot as plt
import csv


xLabelCount = 12

time_utilization_graph = []
idle_power_watt = 212
max_power_watt = 597


# This block contains parameters for co2 efficiency analaysis
# first run day index = 65
index_used_in_run = 65  # is generated at start of day in scheduler initialization
benchmark_run_start_hour = 16  # hour, at which the scenario is started


# Function to calculate power consumption
# https://dl.acm.org/doi/pdf/10.1145/1273440.1250665 page 15 Estimating Server Power Usage
def power_estimation(percentage):
    scaling_power = max_power_watt-idle_power_watt
    return idle_power_watt + scaling_power*percentage


def analyse_load_graph(file_to_analyze):
    time_utilization_graph.clear()
    i = 0
    load = []
    with open(file_to_analyze, 'r') as csvfile:
        lines = csv.reader(csvfile, delimiter=',')
        for row in lines:
            i = i+1
            time_utilization_graph.append(row[0][:-3])
            print(row[7])
            print("test index: " + str(i))
            print(float(row[8]))
            load.append(float(row[8]))
    return load


unoptimized = analyse_load_graph("./first_run_(8.3.21)/co2_unoptimized.csv")
optimized = analyse_load_graph("./first_run_(8.3.21)/co2_optimized.csv")

print(len(unoptimized))
print(len(optimized))

plt.plot(time_utilization_graph, unoptimized, color='r', linestyle='solid', label="CPU reservation unoptimized")
plt.plot(time_utilization_graph, optimized, color='g', linestyle='solid', label="CPU reservation optimized")


x_tics = []
x_labels = []

for date in range(1, len(time_utilization_graph), int(len(time_utilization_graph) / xLabelCount)):
    x_tics.append(date)
    x_labels.append(time_utilization_graph[date])


axes = plt

plt.xticks(rotation=20)
plt.xticks(x_tics, x_labels)

plt.xlabel('time')
plt.ylabel('CPU Reservation in %')
plt.title('Kubernetes Cluster cpu reservation', fontsize=20)
plt.grid()
plt.ylim([0, 100])
plt.xlim([0, len(time_utilization_graph) - 1])
plt.legend()
plt.show()


# calculate graph for power consumption
def analyse_power_consumption(cpu_utilization):
    power_consumption_of_cluster = []
    for cluster_utilization_measured in cpu_utilization:
        power_consumption_of_cluster.append(power_estimation(cluster_utilization_measured/100))
    return power_consumption_of_cluster


power_consumption_of_unoptimized_cluster = analyse_power_consumption(unoptimized)
power_consumption_of_optimized_cluster = analyse_power_consumption(optimized)

print("debug")
print(power_consumption_of_unoptimized_cluster)

plt.plot(time_utilization_graph, power_consumption_of_unoptimized_cluster, color='r', linestyle='solid', label="unoptimized power consumption")
plt.plot(time_utilization_graph, power_consumption_of_optimized_cluster, color='g', linestyle='solid', label="optimized power consumption")

# plt.plot(time_utilization_graph, power_consumption_of_optimized_cluster, "test2")
plt.xticks(x_tics, x_labels)
plt.xticks(rotation=20)
plt.ylim(0, max_power_watt)
plt.xlim([0, len(time_utilization_graph) - 1])
plt.xlabel('time')
plt.ylabel('cluster power consumption in watt')
plt.legend()
plt.grid()
plt.show()


# Plot power model

utilization_list = []
power_consumption_list = []
for i in range(0, 11):
    utilization = i*0.1
    utilization_list.append(utilization * 100)
    power_consumption_list.append(power_estimation(utilization))


plt.clf()
plt.ylim(0, max(power_consumption_list))
plt.xlim(0, max(utilization_list))
plt.title('Utilization to power transition model', fontsize=20)
plt.xlabel('cluster utilization in %')
plt.ylabel('cluster power consumption in watt')
plt.grid()

plt.plot(utilization_list, power_consumption_list)
plt.show()


# read co2 efficiency graph and calculate
real_co2_emission_data = []
co2_emission_time = []
with open("../../co2_prediction/Germany_CO2_Signal_2021.csv", 'r') as csvfile:
    lines = csv.reader(csvfile, delimiter=',')
    next(lines)  # skip header
    for skip in range(0, index_used_in_run*24):
        next(lines)
    time_window = 0
    for row in lines:
        real_co2_emission_data.append(float(row[5]))
        co2_emission_time.append(time_window)
        time_window = time_window + 1
        print(row[5])
        if time_window > 23:
            break

co2_prediction_data = []
with open("../../co2_prediction/average_co2_emissions.csv", 'r') as csvfile:
    co2_prediction_data_string = []
    lines = csv.reader(csvfile, delimiter=',')
    for skip in range(0, index_used_in_run):
        next(lines)
    co2_prediction_data_string = next(lines)
    for element in co2_prediction_data_string:
        co2_prediction_data.append(float(element))


# plt.clf()
plt.plot(co2_emission_time, real_co2_emission_data, color='r', linestyle='solid', label="co2 emission curve")
plt.plot(co2_emission_time, co2_prediction_data, color='g', linestyle='solid', label="co2 prediction curve")
plt.title('CO2 efficiency for day', fontsize=20)
plt.grid()
plt.legend()
plt.xlabel('CO2/kw')
plt.ylabel('time of day in h')
plt.ylim(0, max(max(real_co2_emission_data), max(co2_prediction_data)))
plt.xlim(0, max(co2_emission_time))
plt.show()


co2_unoptimized_sum = 0.0
co2_unoptimized = []

co2_optimized_sum = 0.0
co2_optimized = []


# Block to calculate total CO2 emission
for index in range(0, len(power_consumption_of_unoptimized_cluster)):
    co2_hour_index = (int(index / 60) + benchmark_run_start_hour) % 24  # create for lookup
    print(str(co2_hour_index) + ", " + str(index))
    power_consumption_of_optimized_cluster.__getitem__(index)

    co2_unoptimized_sum = co2_unoptimized_sum + power_consumption_of_unoptimized_cluster.__getitem__(index) * real_co2_emission_data[co2_hour_index]/60
    co2_unoptimized.append(co2_unoptimized_sum)

    co2_optimized_sum = co2_optimized_sum + power_consumption_of_optimized_cluster.__getitem__(index) * real_co2_emission_data[co2_hour_index]/60
    co2_optimized.append(co2_optimized_sum)


print("Co2 unoptimized emissions: " + str(co2_unoptimized_sum))
print("CO2 optimized emissions: " + str(co2_optimized_sum))
print(co2_unoptimized)

plt.plot(time_utilization_graph, co2_unoptimized, color='r', linestyle='solid', label="co2 emissions unoptimized")
plt.plot(time_utilization_graph, co2_optimized, color='g', linestyle='solid', label="co2 emissions optimized")
plt.title('CO2 emissions of day', fontsize=20)
plt.grid()
plt.legend()
plt.xticks(rotation=20)
plt.xticks(x_tics, x_labels)
plt.xlabel('CO2 emissions')
plt.ylabel('time')
plt.ylim(0, max(co2_unoptimized_sum, co2_optimized_sum))
plt.xlim([0, len(time_utilization_graph) - 1])
plt.show()
