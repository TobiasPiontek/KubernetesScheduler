import csv
import datetime

file_to_use = 'Germany_CO2_Signal_2020.csv'

co2_emission_column = 5  # 2018 column = 3, 2020 & 2021 = 5
unix_timestamp_column = 3  # 2018 column = 1, 2020 & 2021 = 3

a = 0

week_array = [[], [], [], [], [], [], []]

day_before = 0  # debug
counter = 0

print("start of program")


# nth-day = the weekday with 0 = monday 6 = sunday
def get_day_array(nth_day, week_day):
    week_day_hours = week_array[int(week_day)]
    start_index = int(nth_day * 24) % len(week_day_hours)
    end_index = int(start_index + 24)
    result_day = []
    for x in range(start_index, end_index):
        result_day.append(week_day_hours[x])
    return result_day


def set_day_array(nth_day, week_day, hour_log):
    week_day_hours = week_array[int(week_day)]
    start_index = int(nth_day * 24) % len(week_day_hours)
    end_index = int(start_index + 24)
    for x in range(start_index, end_index):
        week_array[week_day][x] = hour_log[x - start_index]


# factor is necessary, as the unix timestamp is not standard compliant as timezone is set to UTC + 1
timezone_unix_factor = 3600

with open(file_to_use, 'r') as csvfile:
    lines = csv.reader(csvfile, delimiter=',')
    next(lines)  # skip the label field
    for row in lines:
        a = a + 1
        day = datetime.datetime.fromtimestamp(
            int(row[unix_timestamp_column]) - timezone_unix_factor)  # correction as timestamp is UTC not UTC + 1

        day_number = day.weekday()
        week_array[day_number].append(row[co2_emission_column])

print("starting data cleaning")

days_fixed = 0
for week in range(0, 52):
    for weekday in range(0, 7):
        day_hours = get_day_array(week, weekday)
        found = False
        for hour in day_hours:
            if not hour:
                found = True

        if found:
            days_fixed = days_fixed + 1
            print(week, ",", weekday)
            print("missing value found!")
            print(get_day_array(week, weekday))
            past_weekday = None
            past_week = None
            if weekday == 0:
                past_weekday = 6
                past_week = week - 1
            else:
                past_weekday = weekday - 1
                past_week = week
            print("debug: ", past_week, ",", past_weekday)
            day_before = get_day_array(past_week, past_weekday)
            print(day_before)
            set_day_array(week, weekday, day_before)
            print(get_day_array(week, weekday))

print(days_fixed, "days fixed!")
print("ending data cleaning")

print("end of loop!")
print("total hours: " + str(a))
print("days: " + str(a / 24))

print("starting average week calculation")
median_weekday = [[], [], [], [], [], [], []]

for weekday in range(0, len(week_array)):  # iterate for all days from
    for day in range(0, int(len(week_array[weekday]) / 24)):
        first_week = get_day_array(day - 2, weekday)
        second_week = get_day_array(day - 1, weekday)
        current_week = get_day_array(day, weekday)
        fourth_week = get_day_array(day + 1, weekday)
        fifth_week = get_day_array(day + 2, weekday)

        average_day_efficiency = []
        for hour in range(0, len(first_week)):
            average_hour = float(first_week[hour]) * 0.1 + float(second_week[hour]) * 0.2 + float(
                current_week[hour]) * 0.4 + float(fourth_week[hour]) * 0.2 + float(fifth_week[hour]) * 0.1
            average_day_efficiency.append(average_hour)

        if day == 0 and weekday == 0:
            print(current_week)
        median_weekday[weekday].append(average_day_efficiency)

print("last output")
print(median_weekday[0][0])

print("generating .csv file")
f = open('./average_co2_emissions.csv', 'w', newline='')
writer = csv.writer(f, lineterminator="\n")
for week in range(0, len(week_array)):  # iterate for all days from
    for day in range(0, int(len(week_array[week]) / 24)):
        writer.writerow(median_weekday[week][day])
