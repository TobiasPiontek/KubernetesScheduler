import matplotlib.pyplot as plt
import csv

xLabelCount = 13

time_utilization_graph = []
idle_power_watt = 212
max_power_watt = 597

# This block contains parameters for co2 efficiency analysis

run_metadata = [[65, 16, "./first_run_(8.3.21)/co2_unoptimized.csv", "./first_run_(8.3.21)/co2_optimized.csv"],
                [69, 17, "./second_run_(12.3.21)/co2_unoptimized.csv", "./second_run_(12.3.21)/co2_optimized.csv"],
                [78, 17, "./third_run_(21.3.21)/co2_unoptimized.csv", "./third_run_(21.3.21)/co2_optimized.csv"],
                [80, 17, "./third_run_(21.3.21)/co2_unoptimized.csv", "./third_run_(21.3.21)/co2_optimized.csv"]]
run_to_analyze = 3

index_used_in_run = run_metadata[run_to_analyze][0]  # is generated at start of day in scheduler initialization

# first run start hour = 16
benchmark_run_start_hour = run_metadata[run_to_analyze][1]  # hour, at which the scenario is started

unoptimized_csv_log_path = run_metadata[run_to_analyze][2]
optimized_csv_log_path = run_metadata[run_to_analyze][3]


# Function to calculate power consumption
# https://dl.acm.org/doi/pdf/10.1145/1273440.1250665 page 15 Estimating Server Power Usage
def power_estimation(percentage):
    scaling_power = max_power_watt - idle_power_watt
    return idle_power_watt + scaling_power * percentage


def analyse_load_graph(file_to_analyze):
    time_utilization_graph.clear()

    load = []
    with open(file_to_analyze, 'r') as load_csv_file:
        debug_index = 0
        year = csv.reader(load_csv_file, delimiter=',')
        for hour in year:
            debug_index = debug_index + 1
            time_utilization_graph.append(hour[0][:-3])
            print(hour[7])
            print("test index: " + str(debug_index))
            print(float(hour[8]))
            load.append(float(hour[8]))
    return load


unoptimized = analyse_load_graph(unoptimized_csv_log_path)
optimized = analyse_load_graph(optimized_csv_log_path)

print(len(unoptimized))
print(len(optimized))


x_tics = []
x_labels = []

for date in range(0, xLabelCount):
    x_tics.append(date * 120)
    x_labels.append(time_utilization_graph[date * 120])

axes = plt

plt.plot(time_utilization_graph, unoptimized, color='r', linestyle='solid', label="CPU reservation unoptimized")
plt.plot(time_utilization_graph, optimized, color='g', linestyle='solid', label="CPU reservation optimized")
plt.xticks(rotation=20)
plt.xticks(x_tics, x_labels)

plt.xlabel('time')
plt.ylabel('CPU Reservation in %')
plt.title('Kubernetes Cluster cpu reservation', fontsize=20)

plt.grid()
plt.ylim([0, 100])
plt.xlim([0, len(time_utilization_graph) - 1])
plt.legend()
plt.tight_layout()
file_title = "cluster_cpu_reservation_" + str(run_to_analyze)
plt.get_current_fig_manager().set_window_title(file_title)
plt.savefig(file_title + ".pdf")
plt.show()

# Plot power model

utilization_list = []
power_consumption_list = []
for i in range(0, 11):
    utilization = i * 0.1
    utilization_list.append(utilization * 100)
    power_consumption_list.append(power_estimation(utilization))

plt.clf()
plt.ylim(0, max(power_consumption_list) * 1.02)
plt.xlim(0, max(utilization_list))
plt.title('Utilization to power transition model', fontsize=20)
plt.xlabel('cluster utilization in %')
plt.ylabel('cluster power consumption in watt')

plt.grid()

plt.plot(utilization_list, power_consumption_list)
plt.tight_layout()
file_title = "power_model"
plt.get_current_fig_manager().set_window_title(file_title)
plt.savefig(file_title + ".pdf")
plt.show()



# calculate graph for power consumption
def analyse_power_consumption(cpu_utilization):
    power_consumption_of_cluster = []
    for cluster_utilization_measured in cpu_utilization:
        power_consumption_of_cluster.append(power_estimation(cluster_utilization_measured / 100))
    return power_consumption_of_cluster


power_consumption_of_unoptimized_cluster = analyse_power_consumption(unoptimized)
power_consumption_of_optimized_cluster = analyse_power_consumption(optimized)

print("debug")
print(power_consumption_of_unoptimized_cluster)

plt.plot(time_utilization_graph, power_consumption_of_unoptimized_cluster, color='r', linestyle='solid',
         label="unoptimized power consumption")
plt.plot(time_utilization_graph, power_consumption_of_optimized_cluster, color='g', linestyle='solid',
         label="optimized power consumption")

plt.xticks(x_tics, x_labels)
plt.xticks(rotation=20)
plt.ylim(0, max_power_watt * 1.02)
plt.xlim([0, len(time_utilization_graph) - 1])
plt.xlabel('time')
plt.ylabel('cluster power consumption in watt')
plt.title('Kubernetes Cluster energy consumption', fontsize=20)
plt.legend()
plt.grid()
plt.tight_layout()
file_title = "cluster_power_consumption_" + str(run_to_analyze)
plt.get_current_fig_manager().set_window_title(file_title)
plt.savefig(file_title + ".pdf")
plt.show()


# read co2 efficiency graph and calculate
real_co2_emission_data = []
co2_emission_time = []
with open("../../co2_prediction/Germany_CO2_Signal_2021.csv", 'r') as csvfile:
    lines = csv.reader(csvfile, delimiter=',')
    next(lines)  # skip header
    for skip in range(0, index_used_in_run * 24):
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


plt.plot(co2_emission_time, real_co2_emission_data, color='r', linestyle='solid', label="co2 emission curve")
plt.plot(co2_emission_time, co2_prediction_data, color='g', linestyle='solid', label="co2 prediction curve")
plt.title('CO2 efficiency for day', fontsize=20)
plt.grid()
plt.legend()
plt.xlabel('time of day in h')
plt.ylabel('CO2/kw')

plt.ylim(0, max(max(real_co2_emission_data), max(co2_prediction_data)) * 1.02)
plt.xlim(0, max(co2_emission_time))
plt.tight_layout()
file_title = "co2_prediction_accuracy_" + str(run_to_analyze)
plt.get_current_fig_manager().set_window_title(file_title)
plt.savefig(file_title + ".pdf")
plt.show()

co2_unoptimized_sum = 0.0
co2_unoptimized_accumulated = []
co2_per_hour_unoptimized = []

co2_optimized_sum = 0.0
co2_optimized_accumulated = []
co2_per_hour_optimized = []

co2_per_hour_versus = []

# Block to calculate total CO2 emission
for index in range(0, len(power_consumption_of_unoptimized_cluster)):
    co2_hour_index = (int(index / 60) + benchmark_run_start_hour) % 24  # create for lookup
    print(str(co2_hour_index) + ", " + str(index))
    power_consumption_of_optimized_cluster.__getitem__(index)

    current_co2_unoptimized = power_consumption_of_unoptimized_cluster.__getitem__(index) * real_co2_emission_data[
        co2_hour_index] / 60
    co2_unoptimized_sum = co2_unoptimized_sum + current_co2_unoptimized
    co2_unoptimized_accumulated.append(co2_unoptimized_sum)
    co2_per_hour_unoptimized.append(current_co2_unoptimized)

    current_co2_optimized = power_consumption_of_optimized_cluster.__getitem__(index) * real_co2_emission_data[
        co2_hour_index] / 60
    co2_optimized_sum = co2_optimized_sum + current_co2_optimized
    co2_optimized_accumulated.append(co2_optimized_sum)
    co2_per_hour_optimized.append(current_co2_optimized)

    co2_per_hour_versus.append(co2_unoptimized_sum - co2_optimized_sum)


plt.plot(time_utilization_graph, co2_per_hour_unoptimized, color='r', linestyle='solid',
         label="co2 emissions unoptimized")
plt.plot(time_utilization_graph, co2_per_hour_optimized, color='g', linestyle='solid', label="co2 emissions optimized")
plt.title('CO2 emission rate / hour', fontsize=20)
plt.grid()
plt.legend()
plt.xticks(rotation=20)
plt.xticks(x_tics, x_labels)
plt.xlabel('time')
plt.ylabel('CO2 / hour')
plt.ylim(0, max(max(co2_per_hour_unoptimized), max(co2_per_hour_optimized)) * 1.02)
plt.xlim([0, len(time_utilization_graph) - 1])
plt.tight_layout()
file_title = "co2_emissions_per_hour_" + str(run_to_analyze)
plt.get_current_fig_manager().set_window_title(file_title)
plt.savefig(file_title + ".pdf")
plt.show()


plt.plot(time_utilization_graph, co2_unoptimized_accumulated, color='r', linestyle='solid',
         label="co2 emissions unoptimized")
plt.plot(time_utilization_graph, co2_optimized_accumulated, color='g', linestyle='solid',
         label="co2 emissions optimized")
plt.title('total CO2 emissions of day', fontsize=20)
plt.grid()
plt.legend()
plt.xticks(rotation=20)
plt.xticks(x_tics, x_labels)
plt.xlabel('time')
plt.ylabel('total CO2 emission')
plt.ylim(0, max(co2_unoptimized_sum, co2_optimized_sum) * 1.02)
plt.xlim([0, len(time_utilization_graph) - 1])
plt.tight_layout()
file_title = "co2_emissions_accumulated_" + str(run_to_analyze)
plt.get_current_fig_manager().set_window_title(file_title)
plt.savefig(file_title + ".pdf")
plt.show()



plt.plot(time_utilization_graph, co2_per_hour_versus, color='b', linestyle='solid')
plt.title('CO2 emission savings over time', fontsize=20)
plt.grid()
plt.xticks(rotation=20)
plt.xticks(x_tics, x_labels)
plt.xlabel('time')
plt.ylabel('CO2 accumulated difference / hour')
plt.ylim(min(co2_per_hour_versus), max(co2_per_hour_versus) * 1.02)
plt.xlim([0, len(time_utilization_graph) - 1])
plt.tight_layout()
file_title = "accumulated_co2_emissions_per_hour_difference" + str(run_to_analyze)
plt.get_current_fig_manager().set_window_title(file_title)
plt.savefig(file_title + ".pdf")
plt.show()

print("Co2 unoptimized emissions: " + str(co2_unoptimized_sum))
print("CO2 optimized emissions: " + str(co2_optimized_sum))
print("CO2 reduced by: " + str(((co2_unoptimized_sum - co2_optimized_sum) / co2_unoptimized_sum)))
