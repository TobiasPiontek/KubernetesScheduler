import matplotlib.pyplot as plt
import csv


xLabelCount=15

x = []
y = []
  
with open('utilization-logs.csv','r') as csvfile:
    lines = csv.reader(csvfile, delimiter=',')
    for row in lines:
        x.append(row[0])
        y.append(float(row[3]))
  
plt.plot(x, y, color = 'g', linestyle = 'dashed',
         marker = 'o',label = "CPU utilization")

xtics = []
xlabels = []

for date in range(1, len(x), int(len(x)/xLabelCount)):
    xtics.append(date)
    xlabels.append(x[date])


axes=plt

plt.xticks(rotation = 45)
plt.xticks(xtics,xlabels)

plt.fill_between(x,y)
plt.xlabel('Times')
plt.ylabel('CPU Utilization in %')
plt.title('Kubernetes Cluster Load', fontsize = 20)
plt.grid()
plt.legend()
plt.show()