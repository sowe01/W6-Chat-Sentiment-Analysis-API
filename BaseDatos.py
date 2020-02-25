from pymongo import MongoClient
from bson.json_util import dumps
import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import re
from flask import Flask, request
from errorHandler import jsonErrorHandler

# conexión a Mongo:
client = MongoClient("mongodb://localhost:27017/")

# Creo una base de datos y dos colecciones
db = client.get_database('chat')
user_coll = db["users"]


# funcion para crear el usuario

@jsonErrorHandler
def creauser(name):
    if len(list(user_coll.find({}, {"idUser": 1}))) == 0:
        new_id = 1
    else:
        new_id = id_check() + 1
    new_user = {
        "idUser": new_id,
        "userName": name
    }

    user_coll.insert_one(new_user)
    return {name: 'was created in mongo'}

# funcion para encontrar el ultimo idUser


def id_check():
    id_number = list(user_coll.find({}, {"idUser": 1}))[-1]["idUser"]
    print(id_number)
    return id_number

#comprueba si el usuario existe para evitar duplicados
def checkName(name, tipo="name"):
    q = {"userName": {"$exists": True}}
    query = user_coll.find(q, projection={"userName": 1, "_id": 0})
    findname = [name for i in query for name in i.values()]

    if name in findname:
        if tipo == "name":
            return f"{name} ya existe en la base de datos. Por favor elige otro nombre."
        elif tipo == "conversation":
            return "OK"
    else:
        if tipo == "name":
            return "OK"
        elif tipo == "conversation":
            return f"{name} NO existe en la base de datos"




@jsonErrorHandler
def getUserSentiment(name):
    """
    Get sentimientos de un usuario --> API @app.route("/get/sentiment/user/<name>")
    """
    sia = SentimentIntensityAnalyzer()
    name = name.capitalize()
    q = {"userName": name}
    query = user_coll.find(q, projection={"idUser": 0, "idMessage": 1})
    if not query:
        raise ValueError("No se han encontrado usuarios")

    lst = list(query)
    count = 0
    df = pd.DataFrame(columns=["neg", "neu", "pos", "compound"]).T
    for elem in lst:
        for idMessage in elem.values():
            sent = sia.polarity_scores(idMessage)
            df[count] = sent.values()
            count += 1
    df = df.T
    negative = df.neg.mean()
    neutral = df.neu.mean()
    positive = df.pos.mean()

    return {
        "user_name": name,
        "negative": (negative * 100).round(2),
        "neutral": (neutral * 100).round(2),
        "positive": (positive * 100).round(2),
    }

@jsonErrorHandler
def getAllSentiment():
    """
    Get sentimientos de todos los usuarios --> API @app.route("/get/sentiments")
    """
    df = getMySentMatrix()
    df_json = df.to_json(orient="records")

    return df_json

def getMySentMatrix():
    """
    Devuelve la matriz de sentimientos de los usuarios registrados. 
    Útil para analizar sentimientos y realizar recomendaciones.
    """
    q = {}
    query_quote = user_coll.find(q, projection={"idUser": 0, "idMessage": 1})
    query_user = user_coll.find(q, projection={"idUser": 0, "name": 1})

    lst_quote = list(query_quote)
    lst_user = list(query_user)

    count = 0
    df = pd.DataFrame(columns=["neg", "neu", "pos", "compound"]).T
    sia = SentimentIntensityAnalyzer()
    for elem in lst_quote:
        for idMessage in elem.values():
            sent = sia.polarity_scores(idMessage)
            df[count] = sent.values()
            count += 1
    df = df.T

    names = [user for elem in lst_user for user in elem.values()]

    df["name"] = names

    df = (
        df.groupby("name")
        .mean()
        .round(4)
        .sort_values("compound", ascending=False)
        .reset_index()
    )

    return df
'''
# realiza la media de los sentimientos y devuelve el resultado final

def getFinalMetric(chat):
    sid = SentimentIntensityAnalyzer()
    scores = []
    conversation = []
    for text in chat:
        conversation.append(text['userName']+': '+text['text'])
        scores.append(sid.polarity_scores(text['text']))
    df = pd.DataFrame(scores)
    df = df[['neg', 'neu', 'pos']]
    means = df.mean(axis=0)
    df = pd.DataFrame(means)
    df.columns = ['Scores']
    df.index.name = 'Sentiment Metric'
    scores = df['Scores']
    final_sentiment_metric = {}
    for s in scores:
        final_sentiment_metric['neg'] = scores[0]
        final_sentiment_metric['neu'] = scores[1]
        final_sentiment_metric['pos'] = scores[2]
    return final_sentiment_metric

# funcion que devuelve la puntuacion del analasis de sentimientos


def getSentimentReport(chat):
    chat = json.loads(chat)
    sid = SentimentIntensityAnalyzer()
    scores = {}
    for text in chat:
        scores['Message {} analysis'.format(chat.index(
            text)+1)] = (text['userName']+': '+text['text']), (sid.polarity_scores(text['text']))
    scores['Complete chat sentiment Metric'] = getFinalMetric(chat)
    return scores
'''