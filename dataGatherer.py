# Gathers data from the steam store api

import requests
import sys
import time
import json
import re

def getAppIDs():
    appids = []
    r = requests.get("http://api.steampowered.com/ISteamApps/GetAppList/v0001/")
    
    for line in r.text.split("{"):
        #App IDs are between the first occurence of a blank space and a comma in each line
        appids.append(line[line.find(" "):line.find(",")].strip())
   
    #The first 8 lines from the request were garbage data or ids for non games
    del appids[:7] 
 
    return appids

def writeDescriptionsToFile(appids, filename):
    
    with open(filename, 'w') as f:
        for appid in appids:
            #Steam only allows around one request per a second without banning you
            time.sleep(1)

            try:
                apiRequest = requests.get("http://store.steampowered.com/api/appdetails?appids=" + appid)
                
                #Wait another second inbetween requests
                time.sleep(1)
                
                #Scrape default steam webpage for the game for the user generated tags
                tagRequest = requests.get("http://store.steampowered.com/app/" + appid)
                tagRegex = re.findall("<a[^>]*class=\\\"app_tag\\\"[^>]*>([^<]*)</a>", tagRequest.text)
                tags = []

                for tag in tagRegex:
                    tags.append(str(tag).strip())
                
                #Create a new JSON object with the user generated tags included
                gameJson = json.loads(apiRequest.text)
                tagJson = {'tagsForAI' : tags}
                newJson = gameJson.copy()
                newJson.update(tagJson)

                #print(str(newJson))
                #print(str(tagRegex).encode('utf-8'))
                #print("test")
                json.dump(newJson, f)
                f.write("\n")
            except:
                print("Unexpected error:", sys.exc_info()[0])
                continue

def main():

    if len(sys.argv) != 2:
        print("Usage: steamDataGatherer.py <output filename>")
        sys.exit(-1)

    appids = getAppIDs()

    outputFilename = sys.argv[1]
 
    writeDescriptionsToFile(appids, outputFilename)
    
main()
