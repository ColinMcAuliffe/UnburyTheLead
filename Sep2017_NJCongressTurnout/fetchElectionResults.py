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
links = [link for link in links if '2016-municipality-hor-district' in link["href"]]

osCounties = ["passaic","union"]
prefx = "http://nj.gov/state/elections/"
data = [["District","County Name","Municipality Name","Dem","Rep","Ind","Total"]]
for link in links:
    print link['href']
    districtResponse = requests.get(prefx+link['href'])
    districtName = link['href'].split("-")[-1].replace(".pdf","")
    fname = os.path.join("ElectionResults",districtName+".pdf")
    with open(fname, 'wb') as f:
        f.write(districtResponse.content)

    pdfFileObj = open(fname, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    npage     = pdfReader.numPages
    for p in range(npage):
        pageObj = pdfReader.getPage(p)
        text = pageObj.extractText()
        text = text.split("\n")
        print text
        countyHeaders = [(c.replace(" County",""),i) for i,c in enumerate(text) if "County" in c]
        print countyHeaders
        lenPage = len(text)
        inc = (countyHeaders[0][1] - 4)/2 + 1
        print inc
        for countyName,idx in countyHeaders:
            idx +=1

            while True:
                muniName = text[idx]
                print text[idx:idx+inc]
                if muniName == 'Federal Overseas': break
                if muniName == 'COUNTY TOTAL': break
                if idx+inc > lenPage: break
                demVoters = int(text[idx+1].replace(",",""))
                repVoters = int(text[idx+2].replace(",",""))
                indVoters = 0
                for i in range(3,inc):
                    indVoters += int(text[idx+i].replace(",",""))
                totVoters = demVoters+repVoters+indVoters
                data.append([districtName,countyName,muniName,demVoters,repVoters,indVoters,totVoters])
                idx += inc

data = pd.DataFrame(data)
new_header = data.iloc[0] #grab the first row for the header
data = data[1:] #take the data less the header row
data.columns = new_header #set the header row as the df header
data.index = range(len(data))
data.to_csv(os.path.join("ElectionResults","NJTurnout.csv"))
print data

