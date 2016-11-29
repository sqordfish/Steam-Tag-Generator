# Generates tags for steam games

from sklearn import linear_model
import sys
import json

def readData(filename):
    games = []
    
    with open(filename, 'r') as f:
        for line in f:
            #appid is first element of the json, its in the form {"1234":
            appid = line[line.find("\"")+1:line.find(":")-1]
            
            gameJson = json.loads(line)
            
            if not "data" in gameJson[appid]:
                continue

            if not "categories" in gameJson[appid]["data"]:
                continue

            tags = []
            for category in gameJson[appid]["data"]["categories"]:
                tags.append(category["description"])
            
            game = {"name": gameJson[appid]["data"]["name"], "description": gameJson[appid]["data"]["detailed_description"], "tags" : tags}
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
        print(game)

main()
