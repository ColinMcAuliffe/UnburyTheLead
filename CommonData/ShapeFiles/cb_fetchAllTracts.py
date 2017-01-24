from bs4 import BeautifulSoup,SoupStrainer
import argparse
import requests
import StringIO
import zipfile
import shutil
import sys
import os

#1{{{
us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY',
}
states = [x.replace(" ","") for x in us_state_abbrev.keys()]
#1}}}

usCensusTractsUrl = "https://www.census.gov/geo/maps-data/data/cbf/cbf_tracts.html"
topDir = "CensusTracts"
response = requests.get(usCensusTractsUrl)
bsObj = BeautifulSoup(response.content, "html.parser")
for select in bsObj.find_all('select'):
    print select['id']
selection = bsObj.find_all('select',{'id':'ct2015m'})
for option in selection[0].find_all('option'):
    if option.text.replace(" ","") in states:
        print "fetching census tracts for ",option.text
        url = option['value']
        zipname = url.split("/")[-1]
        fname = os.path.join(topDir,zipname.replace(".zip",""))
        r = requests.get(url, stream=True)
        z = zipfile.ZipFile(StringIO.StringIO(r.content))
        z.extractall(fname)
        



