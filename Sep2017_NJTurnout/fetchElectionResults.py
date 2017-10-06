import os
import numpy as np
import pandas as pd
import geopandas as gpd
from bs4 import BeautifulSoup, SoupStrainer
import requests

import PyPDF2

url = "http://nj.gov/state/elections/election-information-archive-2016.html"
response = requests.get(url)

links = BeautifulSoup(response.content, "html.parser", parse_only=SoupStrainer('a'))

links = [link for link in links if link.has_attr("href")]
links = [link for link in links if '2016-gen-elect-ballotscast-results' in link["href"]]

osCounties = ["passaic","union"]
prefx = "http://nj.gov/state/elections/"
data = [["County Name","Municipality Name","Registered Voters","Ballots Cast"]]
for link in links:
    print link['href']
    countyResponse = requests.get(prefx+link['href'])
    countyName = link['href'].split("-")[-1].replace(".pdf","")
    fname = os.path.join("ElectionResults",countyName+".pdf")
    with open(fname, 'wb') as f:
        f.write(countyResponse.content)

    pdfFileObj = open(fname, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    npage     = pdfReader.numPages
    for p in range(npage):
        pageObj = pdfReader.getPage(p)
        text = pageObj.extractText()
        text = text.split("\n")
        lenPage = len(text)
        if countyName in osCounties:
            idx = 14
            inc = 7
        else:
            idx = 12
            inc = 6

        while True:
            muniName = text[idx]
            print text[idx:idx+inc]
            if muniName == 'Federal Overseas': break
            if muniName == 'COUNTY TOTAL': break
            if idx+inc > lenPage: break
            regVoters = int(text[idx+1].replace(",",""))
            ballots   = int(text[idx+2].replace(",",""))
            data.append([countyName,muniName,regVoters,ballots])
            idx += inc

data = pd.DataFrame(data)
new_header = data.iloc[0] #grab the first row for the header
data = data[1:] #take the data less the header row
data.columns = new_header #set the header row as the df header
data.index = range(len(data))
data.to_csv(os.path.join("ElectionResults","NJTurnout.csv"))
print data

