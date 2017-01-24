from bs4 import BeautifulSoup,SoupStrainer
import argparse
import requests
import StringIO
import zipfile
import shutil
import sys
import os

parser = argparse.ArgumentParser(description='Fetch Various Shape Files')
parser.add_argument('--list_all',dest='list_all',action='store_true',help='List status of available shape files')
parser.set_defaults(list_all=False)
parser.add_argument('-fetch',dest='fetch',nargs=2,help='fetch specified shape file')
parser.add_argument('-year' ,dest='year' ,help='year to fetch')
parser.set_defaults(year='2015')
parser.add_argument('-res'  ,dest='res'  ,help='fetch specified shape file')
parser.set_defaults(res='500k')
args = parser.parse_args()
print args



class shapeFile(object):
    def __init__(self,url,year,res,fname):
        self.url   = url
        self.year  = year
        self.res   = res
        self.fname = fname
    def fetch(self):
        if os.path.isdir(self.fname):
            shutil.rmtree(self.fname)
        os.mkdir(self.fname)
        r = requests.get(self.url, stream=True)
        z = zipfile.ZipFile(StringIO.StringIO(r.content))
        z.extractall(self.fname)

class shapeFileCollection(object):
    def __init__(self,source,name,url):
        self.source = source
        self.name   = name
        self.url    = url
        self.shapeFiles = []

    def findAvailable(self):
        response = requests.get(self.url)
        links = BeautifulSoup(response.content, "html.parser",parse_only=SoupStrainer('a'))
        for link in links:
            if link.has_attr('href'):
                if ".zip" in link['href']:
                    url = link['href']
                    zipname = url.split("/")[-1]
                    fname = zipname.replace(".zip","")
                    fnamesp = fname.split("_")
                    year = fnamesp[1]
                    res  = fnamesp[-1]
                    sf = shapeFile(url,year,res,fname)
                    self.shapeFiles.append(sf)

        

usCensusStateUrl = "https://www.census.gov/geo/maps-data/data/cbf/cbf_state.html"
states = shapeFileCollection("census","state",usCensusStateUrl)
states.findAvailable()
states.shapeFiles[0].fetch()

usCensusCongressionalUrl = "https://www.census.gov/geo/maps-data/data/cbf/cbf_cds.html"

usCensusCountiesUrl = "https://www.census.gov/geo/maps-data/data/cbf/cbf_counties.html"

