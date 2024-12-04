# train_bot.py
import json
import numpy as np
import mysql.connector
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import StratifiedKFold
from collections import Counter
from pymongo import MongoClient 
import asyncio

mydb = mysql.connector.connect(host="localhost", user="admin",passwd="1234",database="trainingdata")

#mongodb 

uri = "mongodb+srv://Visitor:researchgogogo@reseearch.a2rwr6l.mongodb.net/"

client = MongoClient(uri)
db = client['research']
collection = db['data']


    
def getMongdoDB():
    myquery = {"tag":0,"patterns":1 }
    data = collection.find()
    tags=[]
    tagsforPatters=[]
    patterns=[]
    new =[]
    for x in data:
        new =x.get("patterns")
        for i in new:
            tagsforPatters.append(x.get("tag"))
        patterns = patterns+new
    
    testpatterns = []
    testtags = []
    for i in range(50):
        testpatterns.append(patterns[i])
        testtags.append(tagsforPatters[i])

    return testpatterns,testtags


def train_chatbot():

    X,y = getMongdoDB()
    
    vectorizer = TfidfVectorizer()
    X_tfidf = vectorizer.fit_transform(X)

    labels = list(set(y))
    print(labels)

    param_grid = {
        'C': [0.1, 1, 10],
        'kernel': ['linear', 'rbf', 'sigmoid'],
        'gamma': ['scale', 'auto'] + [0.001, 0.01, 0.1, 1, 10]
    }
    svm_model = SVC(probability=True)
    grid_search = GridSearchCV(svm_model, param_grid, cv=5, n_jobs=1)
    grid_search.fit(X_tfidf, y)
    best_svm_model = grid_search.best_estimator_
    print(grid_search.classes_)
    return vectorizer, best_svm_model, labels

if __name__ == "__main__":
    train_chatbot()
