#!/usr/bin/python3
import datetime
import json
import re
import requests
import sys
from dateutil import parser
from bs4 import BeautifulSoup


# pip install requests beautifulsoup4

# get paths to files
tides_site = 'https://www.thephuketnews.com/'
tides_url = tides_site + 'phuket-tide-table.php'


def get_tides(soup): 
	# get paht to mouths
	month_btns = soup.select('.btn.btn-outline-secondary')
	# error, if lenght of mouths is 0
	if len(month_btns) == 0:
		print("can not find current month button")
		sys.exit(1)

	# ???, parse mouth data
	month_text = month_btns[0].text
	try:
		month_dt = parser.parse(month_text)
	except:
		print("failed to parse month button text")
		sys.exit(1)

	# find tbody in timetable
	table = soup.find(id='tidetable')
	tbody = table.find('tbody')
	data_cells = tbody.find_all('div')

	res = {}

	# loop on data
	for div in data_cells:
		div_id = div['id']
		if not div_id:
			continue

		result = re.match(r"^i-([0-9]+)-j-([0-9]+)$", div_id)
		if not result:
			continue

		day = int(result[1])
		hour = int(result[2])
		dt = datetime.datetime(month_dt.year, month_dt.month, day, hour, 0, 0, 0)

		value = float(div.text.strip())

		res[dt.strftime("%Y-%m-%dT%H:%M:%S")] = value

	return res
# }

if __name__ == "__main__":
	out = None
	if len(sys.argv) == 2:
		out = sys.argv[1]

	# get data from sourse
	html_text = requests.get(tides_url).text
	soup = BeautifulSoup(html_text, 'html.parser')

	# get data about current month
	res1 = get_tides(soup)

	# get data about next month
	month_btns = soup.select('.btn.btn-primary')
	if len(month_btns) != 2:
		print("can not find months button")
		sys.exit(1)

	next_month_url = tides_site + month_btns[1]['href'][2:]
	
	html_text = requests.get(next_month_url).text
	soup = BeautifulSoup(html_text, 'html.parser')

	res2 = get_tides(soup)

	res = {**res1, **res2}

	# do result (write to json file, if we have out file || write to terminal, if we haven't out file)
	if out:
		with open(out, "w") as outfile:
			print('tides_data = ' + json.dumps(res, indent=4), file=outfile)
	else:
		print(json.dumps(res, indent=4))
# }