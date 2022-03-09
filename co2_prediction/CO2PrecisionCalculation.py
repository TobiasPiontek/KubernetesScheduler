import csv
import datetime

real_world_future_co2_data = 'Germany_CO2_Signal_2021.csv'
predicted_co2_data = 'average_co2_emissions.csv'
co2_emission_column = 5     # 2018 column = 3, 2020 & 2021 = 5
unix_timestamp_column = 3   # 2018 column = 1, 2020 & 2021 = 3

# read real world co2 data in:
co2_emission_real_world_future = []
co2_emission_prediction = []

skip_to_same_day_monday = 3

with open(real_world_future_co2_data, 'r') as csvfile:
    lines = csv.reader(csvfile, delimiter=',')
    next(lines)  # skip the label field
    for i in range(0, skip_to_same_day_monday*24):
        next(lines)
    for row in lines:
        co2_emission_real_world_future.append(float(row[co2_emission_column]))


# read predicted co2 data for 2021:
with open(predicted_co2_data, 'r') as csvfile:
    lines = csv.reader(csvfile, delimiter=',')
    # next(lines)  # skip the label field
    for row in lines:
        for column in row:
            co2_emission_prediction.append(float(column))



n = min(len(co2_emission_real_world_future), len(co2_emission_prediction))

#test = 2

mape_sum = 0.0
mse_sum = 0.0
for i in range(n):
    forecasting_error = abs(co2_emission_real_world_future[i] - co2_emission_prediction[i])

    mape_term = forecasting_error / co2_emission_real_world_future[i]
    mape_sum = mape_sum + mape_term

    mse_term = pow(forecasting_error, 2)
    mse_sum = mse_term + mse_term

MAPE = (mape_sum / n) * 100
MSE = mse_sum / n

print("Mape result is: " + str(MAPE) + " %")
print("MSE result is: " + str(MSE))



# print(co2_emissions_prediction)
