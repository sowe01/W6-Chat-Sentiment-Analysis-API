from pymongo import MongoClient
from bson.json_util import dumps
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import re
from flask import Flask, request
# conexión a Mongo:
client = MongoClient("mongodb://localhost:27017/")

# Creo una base de datos y dos colecciones
db = client.get_database('chat')
user_coll = db["users"]
chat_coll = db["chats"]


# funcion para crear el usuario


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
