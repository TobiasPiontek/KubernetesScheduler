import csv
import datetime

a = 0

monday = []
tuesday = []
wednesday = []
thursday = []
friday = []
saturday = []
sunday = []

week_array = [monday, tuesday, wednesday, thursday, friday, saturday, sunday]

day_before = 0  # debug
counter = 0

print("start of proggram")


# nth-day = the weekday with 0 = monday 6 = sunday
def get_day_array(nth_day, weekday):
    week_day_hours = week_array[int(weekday)]
    startindex = int(nth_day * 24)
    endindex = int(startindex + 24)
    resultday = []
    for x in range(startindex, endindex):
        resultday.append(week_day_hours[x])
    return resultday


timezone_unix_factor = 3600  # factor is necessary, as the unix timestamp is not standard compliant as timeszone is set to UTC + 1
# print(datetime.datetime.fromtimestamp(1514764800).hour)
with open('UniGroningen_DE_2018.csv', 'r') as csvfile:
    lines = csv.reader(csvfile, delimiter=',')
    next(lines)  # skip the label field
    for row in lines:
        # print(row[3])
        a = a + 1
        day = datetime.datetime.fromtimestamp(
            int(row[1]) - timezone_unix_factor)  # correction as timestamp is UTC not UTC + 1
        # print(day.weekday()) # 0 equals a monday
        # day.month()

        if day.weekday() == day_before:
            counter = counter + 1
            if counter > 23:
                print("hit encountered!")
                print(row[1])
        else:
            counter = 0
            day_before = day.weekday()

        day_number = day.weekday()

        co2emmisionrow = 3
        if day_number == 0:
            daylist = []
            monday.append(row[co2emmisionrow])

        elif day_number == 1:
            tuesday.append(row[co2emmisionrow])

        elif day_number == 2:
            wednesday.append(row[co2emmisionrow])

        elif day_number == 3:
            thursday.append(row[co2emmisionrow])

        elif day_number == 4:
            friday.append(row[co2emmisionrow])

        elif day_number == 5:
            saturday.append(row[co2emmisionrow])

        elif day_number == 6:
            sunday.append(row[co2emmisionrow])

print(week_array[0])
print(week_array[1])
print(len(monday))
print(len(tuesday))
print(len(wednesday))
print(len(thursday))
print(len(friday))
print(len(saturday))
print(len(sunday))

print("end of loop!")
print("total hours: " + str(a))
print("days: " + str(a / 24))

print(get_day_array(0, 0))
print(get_day_array(0, 1))
print(get_day_array(1, 0))