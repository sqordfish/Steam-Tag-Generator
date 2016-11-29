# Generates tags for steam games

from sklearn import linear_model
import sys
import json
from bs4 import BeautifulSoup

def readData(filename):
    games = []
    
    with open(filename, 'r') as f:
        for line in f:
            #appid is first element of the json, its in the form {"1234":
            appid = line[line.find("\"")+1:line.find(":")-1]
            
            gameJson = json.loads(line)

            #Basically if it is not a game
            if not "data" in gameJson[appid]:
                continue

            #If it doesn't have any tags
            if not "categories" in gameJson[appid]["data"]:
                continue

            tags = []
            for category in gameJson[appid]["data"]["categories"]:
                tags.append(category["description"])
           
            #remove html tags like <br> from the description
            cleanDescription = BeautifulSoup(gameJson[appid]["data"]["detailed_description"]).text            

            game = {"name": gameJson[appid]["data"]["name"], "description": cleanDescription, "tags" : tags}
            games.append(game)

    return games

def main():
    
    if len(sys.argv) != 2:
        print("Usage: tagGenerator.py <input filename>")
        sys.exit(-1)

    inputFilename = sys.argv[1]

    #List of games. Each game is a dictionary containing name, description, and list of tags
    games = readData(inputFilename)

    for game in games:
        print(str(game).encode('utf-8'))

main()
