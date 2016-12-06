# Generates tags for steam games

from sklearn import linear_model
import sys
import json
from bs4 import BeautifulSoup
import random
import difflib

import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import MultiLabelBinarizer

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

            tags = gameJson["tagsForAI"]
            #tags = []
            #for category in gameJson[appid]["data"]["categories"]:
            #    tags.append(category["description"])
           
            #remove html tags like <br> from the description
            cleanDescription = BeautifulSoup(gameJson[appid]["data"]["detailed_description"], "html.parser").text            

            game = {"name": gameJson[appid]["data"]["name"], "description": cleanDescription, "tags" : tags}
            games.append(game)

    return games

def genTagList(games):
    allTags = []

    for game in games:
        allTags.extend(game["tags"])

    return list(set(allTags))

def multilabelClassify(games, testGames):
    allTags = genTagList(games)
    
    descTrainingSet = []
    tagTrainingSet = []
    #testGames = []
    testTrainingSet = []
    mapDescToName = {}
    
    #for i in range(10):
    #    testGames.append(games.pop())

    for game in testGames:
        testTrainingSet.append(game["description"])
        mapDescToName[game["description"]] = game["name"]

    for game in games:
        descTrainingSet.append(game["description"])
        tagTrainingSet.append(game["tags"])
        #numberedTags = []
    
        #for tag in allTags:
        #    if tag in game["tags"]:
                #print(tag + " is at index " + str(allTags.index(tag)))
        #        numberedTags.append(tag)
                #numberedTags.append(allTags.index(tag))
        
        #tagTrainingSet.append(numberedTags)

    #print("Printing desctrainingset")
    #for d in descTrainingSet:
    #    print(str(d).encode('utf-8'))

    #print("Printing TAGtrainingset")
    #for t in tagTrainingSet:
    #    print(str(t).encode('utf-8'))
    #    for a in t:
    #        print(allTags[a].encode('utf-8'))

    #print(str(len(descTrainingSet)) + " == " + str(len(tagTrainingSet)) + " ?")
    
    descTrainingSet = np.array(descTrainingSet)
    testTrainingSet = np.array(testTrainingSet)
    mlb = MultiLabelBinarizer()
    
    tagTrainingSet = mlb.fit_transform(tagTrainingSet)

    #print("Printing all tags...")
    #for l in tagTrainingSet:
    #    print(str(l))

    #print(str(mlb.classes_))
   
    classifier = Pipeline([
        ('vectorizer', CountVectorizer()),
        ('tfidf', TfidfTransformer()),
        ('clf', OneVsRestClassifier(LinearSVC()))])
        #('clf', KNeighborsClassifier())])
        #('clf',RandomForestClassifier())])

    classifier.fit(descTrainingSet, tagTrainingSet)


    predicted = classifier.predict(testTrainingSet)
    allLabels = mlb.inverse_transform(predicted)

    print("Predicted...")
    for item, labels in zip(testTrainingSet, allLabels):
#        print(("%s => %s" % (mapDescToName[item], ', '.join(allTags[x] for x in labels))).encode('utf-8'))
        print(("%s => %s" % (mapDescToName[item], ', '.join(labels))).encode('utf-8'))

    #for tag in allTags:
    #    print(tag)
    
    #for tag in allTags:
    #    print(tag + " -> " + str(allTags.index(tag)))
        
    print("\nExpected...")
    for game in testGames:
        print((game["name"] + " -> " + str(game["tags"])).encode('utf-8'))


#Randomly chooses n games to test
def genRandomTestGames(games, n):
    testGames = []
    
    for i in range(n):
        testGames.append(games.pop(games.index(random.choice(games))))
    
    return testGames


def getChosenGames(games, n):
    names = [g["name"] for g in games]
    testGames = []

    for i in range(n):
        valid = False

        while(not valid):
            name = input("Enter game name: ")
            if name not in names:
                print("Did you mean one of these?: " + str(difflib.get_close_matches(name, names)))
                continue
            else:
                for game in games:
                    if game["name"] == name:
                        testGame = game

                testGames.append(games.pop(games.index(testGame)))
                break

    return testGames



def main():
    
    if len(sys.argv) != 2:
        print("Usage: tagGenerator.py <input filename>")
        sys.exit(-1)

    inputFilename = sys.argv[1]

    print("***Welcome to the Steam Tag Generator!***\n")
    print("Reading game data from " + inputFilename + "...\n")
    
    #List of games. Each game is a dictionary containing name, description, and list of tags
    games = readData(inputFilename)

    quit = False
    validOptions = ["random","choose","create","help","quit"]

    while(not quit):
        option = input("How would you like to test the classifier? (random/choose/create/help/quit): ")
        
        if option not in validOptions:
            print("Invalid option. Valid options are random, choose, create, help, and quit.\n")
            continue

        elif option == "quit":
            quit = True
            break

        elif option == "help":
            print("random: Randomly generates a test set from all available steam games.")
            print("choose: Generate a test set from a list of steam games that you specify.")
            print("create: Write your own game description in the console and have tags generated for it.")
            print("help: Display a help menu.")
            print("quit: Exit the program.\n")
            continue

        elif option == "random":
            n = input("How many games should be in the random test set?: ")
            testGames = genRandomTestGames(games, int(n))

        elif option == "choose":
            n = input("How many games would you like to choose?: ")
            testGames = getChosenGames(games, int(n))

        elif option == "create":
            name = input("Enter a name for your game: ")
            description = input("Enter a description for your game: ")
            game = {"name" : name, "description" : description, "tags" : [] }            
            testGames = [game]
       
        print("\nTraining classifier...\n")
        multilabelClassify(games, testGames)
        print("\n\n")

main()
