import matplotlib.pyplot as plt
import csv


xLabelCount = 12

x = []
y = []
idle_power_watt = 212
max_power_watt = 597

file_to_analyze = 'utilization-logs.csv'


# Function to calculate power consumption
# https://dl.acm.org/doi/pdf/10.1145/1273440.1250665 page 15 Estimating Server Power Usage
def power_estimation(percentage):
    scaling_power = max_power_watt-idle_power_watt
    return idle_power_watt + scaling_power*percentage


i = 0
with open(file_to_analyze, 'r') as csvfile:
    lines = csv.reader(csvfile, delimiter=',')
    for row in lines:
        i = i+1
        x.append(row[0][:-3])
        print(row[7])
        print("test index: " + str(i))
        print(float(row[8]))
        y.append(float(row[8]))
  
plt.plot(x, y, color='b', linestyle='solid', label="CPU reservation")

x_tics = []
x_labels = []

for date in range(1, len(x), int(len(x)/xLabelCount)):
    x_tics.append(date)
    x_labels.append(x[date])


axes = plt

plt.xticks(rotation=20)
plt.xticks(x_tics, x_labels)

plt.fill_between(x, y)
plt.xlabel('Times')
plt.ylabel('CPU Reservation in %')
plt.title('Kubernetes Cluster cpu reservation', fontsize=20)
plt.grid()
plt.ylim([0, 100])
plt.xlim([0, len(y)-1])
plt.legend()
plt.show()


# calculate graph for power consumption

power_consumption_of_cluster = []
for cluster_utilization_measured in y:
    power_consumption_of_cluster.append(power_estimation(cluster_utilization_measured/100))

plt.plot(x, power_consumption_of_cluster)
plt.xticks(x_tics, x_labels)
plt.xticks(rotation=20)
plt.ylim(0, 600)
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
