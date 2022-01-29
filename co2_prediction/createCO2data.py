import csv
import datetime

a = 0


week_array = [[], [], [], [], [], [], []]

day_before = 0  # debug
counter = 0

print("start of proggram")


# nth-day = the weekday with 0 = monday 6 = sunday
def get_day_array(nth_day, weekday):
    week_day_hours = week_array[int(weekday)]
    startindex = int(nth_day * 24) % len(week_day_hours)
    endindex = int(startindex + 24)
    resultday = []
    for x in range(startindex, endindex):
        resultday.append(week_day_hours[x])
    return resultday


timezone_unix_factor = 3600  # factor is necessary, as the unix timestamp is not standard compliant as timeszone is set to UTC + 1
co2emmisionrow = 3
# print(datetime.datetime.fromtimestamp(1514764800).hour)
with open('UniGroningen_DE_2018.csv', 'r') as csvfile:
    lines = csv.reader(csvfile, delimiter=',')
    next(lines)  # skip the label field
    for row in lines:
        a = a + 1
        day = datetime.datetime.fromtimestamp(
            int(row[1]) - timezone_unix_factor)  # correction as timestamp is UTC not UTC + 1

        day_number = day.weekday()
        print("Debug: ", row[co2emmisionrow])

        week_array[day_number].append(row[co2emmisionrow])


# stage for calculating the median weekday values

print("end of loop!")
print("total hours: " + str(a))
print("days: " + str(a / 24))

print(get_day_array(0, 0))
print(get_day_array(-53, 0))
print(get_day_array(53, 0))



print(get_day_array(0, 1))
print(get_day_array(1, 0))


#

print("next debug block")


median_weekday = [[], [], [], [], [], [], []]

for weekday in range(0, len(week_array)): # iterate for all days from
    for day in range(0, int (len(week_array[weekday]) / 24)):
        first_week = get_day_array(day - 2, weekday)
        second_week = get_day_array(day - 1, weekday)
        current_week = get_day_array(day, weekday)
        fourth_week = get_day_array(day + 1, weekday)
        fifth_week = get_day_array(day + 2, weekday)

        average_day_efficiency = []
        for hour in range (0, len(first_week)):
            average_hour = first_week[hour]*0.1 + second_week[hour]*0.2 + current_week[hour]*0.4 + fourth_week[hour]*0.2 + fifth_week[hour]*0.1
            average_day_efficiency.append(average_hour)

        if day == 0 and weekday == 0:
            print(current_week)
        median_weekday[weekday].append(average_day_efficiency)

print("last output")
print(median_weekday[0])