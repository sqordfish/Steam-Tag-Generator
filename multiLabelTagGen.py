# Generates tags for steam games

from sklearn import linear_model
import sys
import json
from bs4 import BeautifulSoup

import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.svm import LinearSVC
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

            tags = []
            for category in gameJson[appid]["data"]["categories"]:
                tags.append(category["description"])
           
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

def multilabelClassify(games):
    allTags = genTagList(games)
    
    descTrainingSet = []
    tagTrainingSet = []
    testGames = []
    testTrainingSet = []
    mapDescToName = {}
    
    for i in range(15):
        testGames.append(games.pop())

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

    for l in tagTrainingSet:
        print(str(l))

    print(str(mlb.classes_))
    
    classifier = Pipeline([
        ('vectorizer', CountVectorizer()),
        ('tfidf', TfidfTransformer()),
        ('clf', OneVsRestClassifier(LinearSVC()))])

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

def main():
    
    if len(sys.argv) != 2:
        print("Usage: tagGenerator.py <input filename>")
        sys.exit(-1)

    inputFilename = sys.argv[1]

    #List of games. Each game is a dictionary containing name, description, and list of tags
    games = readData(inputFilename)


    multilabelClassify(games)

       #for game in games:
    #    print(str(game).encode('utf-8'))

main()
