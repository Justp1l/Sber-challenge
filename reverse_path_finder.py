import json
import pathlib

log = open(".\\raw_data\\log_example.json")
json_object = json.load(log)
some_time_list = list()
for vel in json_object['data']:
    line = vel['time_from_start']
    some_time_list.append(line)
print(some_time_list)

