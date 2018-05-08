from bs4 import BeautifulSoup
import pandas as pd
import requests
import re

response = requests.get("https://touringplans.com/magic-kingdom/wait-times/date/2014-01-01.html")
content = response.content

parser = BeautifulSoup(content, "html.parser")
#print(content)

wait_times_table = parser.select("#entity_wait_times")[0].find_all("tr")
#print(wait_times_table)
ride_data = []

for item in wait_times_table:
    current_ride = {}
    table_data = item.find_all("td")
    ride_name = table_data[0].text
    current_ride["ride_name"] = ride_name
    if len(table_data[1:]) < 2:
        current_ride["predicted_wait"] = "not operational"
        current_ride["observed_wait"] = "not operational"
        current_ride["ride_status"] = table_data[1].text

    else:
        current_ride["predicted_wait"] = table_data[1].text
        current_ride["observed_wait"] = table_data[2].text
        current_ride["ride_status"] = "operational"
    ride_data.append(current_ride)

print(ride_data)

ride_table = pd.DataFrame(ride_data[0:])
print(ride_table)
