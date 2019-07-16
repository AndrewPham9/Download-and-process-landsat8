from usgs import api
import usgs
from usgs import USGS_API
from usgs import xsi, payloads
import subprocess
import requests
import urllib.request as urllib2
import json
import yu
import argparse


##################################~~~ DOWNLOAD IMAGE FROM USGS ~~~###################################
########### 1) need to use key API and request.Session, once session store 1 cookie, 
###########    allow you to continute work with website in this session.
########### 2) using usgs library to get some url and dump JSON of login
########### 3) modify JSON when search and dumo json form a library by json
########### 4) requets library can get data and header (contain redirected url (after login)
########### 5) only work for landsat 8, if want to download other data modify the dataset name in
###########    jsonSearch and urlDown string
########### bounding box

def Download_Landsat_8 (lowLeftLat,lowLeftLong,upRightLat,upRightLong,date):
    ###create api_key, requests is sent in s1, python will store cookie in this session s1.
    urlLogin = '{}/login'.format(USGS_API)
    jsonLogin  ={
        "jsonRequest":usgs.payloads.login('AndrewDuy', 'nhatduyusgs123',catalogId='EE')
    }
    s1 = requests.Session()
    repLogin = s1.post(urlLogin, jsonLogin)

    ###search for api_key (column = data) in repLogin response
    api_key = repLogin.json()['data']

    ###JSON of request image/ images

    urlSearch = '{}/search'.format(USGS_API)
    jsonSearch ={
            "apiKey":api_key,
            "datasetName":"LANDSAT_8_C1",
            "spatialFilter":{
                "filterType":"mbr",
                "lowerLeft":{
                    "latitude":lowLeftLat,"longitude":lowLeftLong
                },
                
                "upperRight":{
                "latitude":upRightLat,"longitude":upRightLong
                }
            },
            "temporalFilter":{
                "startDate":date,"endDate":date
            },
             "includeUnknownCloudCover":True,
             "maxResults":"4",
             "sortOrder":"ASC"
        }

    jsonSearch = json.dumps(jsonSearch)
    jsonSearch = {
    	"jsonRequest":jsonSearch
    }
    
    #search for DownloadURL in repSearch response
    repSearch = requests.post(urlSearch, jsonSearch)
    urlDown = repSearch.json()
    print (urlDown)
    #trim urlDown to actual download in usgs
    C = list()
    #some times 1 shp cut 2 or 3 scenes
    results = urlDown['data']['results']
    print (results)
    for result in results:
        A = result['metadataUrl']
        B = result['downloadUrl']
        urlDown = B[0:40]+A[44:50]+B[70:91]+'/STANDARD/EE'
        print (urlDown)
        #get data in url or HTML or st else.
        h = s1.head(urlDown, allow_redirects=True)
        yu.download_file(h.url)
        C.append(result['displayId'])
    return (C)
def main ():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l1", dest = "lowLeftLong" , help = "put lowLeftLong here", type = str)
    parser.add_argument("-l2", dest = "lowLeftLat" ,help = "put lowLeftLat here", type = str)
    parser.add_argument("-r1", dest = "upRightLong" ,help = "put upRightLong here", type = str)
    parser.add_argument("-r2", dest = "upRightLat" ,help = "put upRightLat here", type = str)
    parser.add_argument("-da", dest = "date" ,help = "put date here", type = str)
    args = parser.parse_args()
    result = Download_Landsat_8(args.lowLeftLong,args.lowLeftLat,args.upRightLong,args.upRightLat,args.date)

if __name__=='__main__':
    main()  
#test data  = ["9.765700445828669","106.02748811899865","10.340238060900552","106.83092331001583","20190612"]