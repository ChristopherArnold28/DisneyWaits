from bs4 import BeautifulSoup
import pandas as pd
import requests
import re

response = requests.get("https://touringplans.com/magic-kingdom/attractions/barnstormer/wait-times/date/2014-01-01#_ABSTRACT_RENDERER_ID_0")
content = response.content

parser = BeautifulSoup(content, "html.parser")
circles = parser.select("#google_chart_100")[0]
print(circles)
