# Gathers data from the steam store api

import requests
import sys
import time

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
            r = requests.get("http://store.steampowered.com/api/appdetails?appids=" + appid)
            f.write(str(r.text.encode("utf-8")) + "\n")
    
            #Steam only allows around one request per a second without banning you
            time.sleep(1)

def main():

    if len(sys.argv) != 2:
        print("Usage: steamDataGatherer.py <output filename>")
        sys.exit(-1)

    appids = getAppIDs()

    outputFilename = sys.argv[1]
 
    writeDescriptionsToFile(appids, outputFilename)
    
main()
