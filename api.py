from flask import Flask, request
from pymongo import MongoClient
from BaseDatos import creauser, getSentimentReport, getFinalMetric, chat_coll, user_coll
from bson.json_util import dumps
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import json
app = Flask(__name__)


@app.route('/users/<name>')
def users(name):
    return json.dumps(creauser(name))


# funcion para crear los chats nuevos

@app.route('/chat/<nuevo>')
def crearchat(chat):
    name = str(request.forms.get("name"))
    text = str(request.forms.get("text"))
    new_id = chat_coll.distinct("idUser")[-1] + 1
    new_idm = chat_coll.distinct("idMessage")[-1] + 1
    new_idc = chat_coll.distinct("idChat")[-1] + 1
    new_user = {
        "idUser": new_id,
        "userName": name,
        "idMessage": new_idm,
        "idChat": new_idc,
        'text': text
    }
    chat_coll.insert_one(new_user)
    return json.dumps({new_user: 'hecho'})


# encontrar los usuarios que existen
@app.route("/user")
def getUsers():
    return dumps(user_coll.find().distinct("userName"))

# ver todos los mensajes de la base de datos
@app.route("/messages")
def getChat():
    return dumps(chat_coll.find({}, {"text": 1, '_id': 0}))

# ver todas las conversaciones
@app.route("/chatid")
def getConversations():
    return dumps(chat_coll.find({}, {'idChat': 1, 'text': 1, '_id': 0}))


# analisis de sentimientos
@app.route("/chat/<idChat>/sentiment")
def sentimentReport(idChat):
    chat = dumps(chat_coll.find({'idChat': int(idChat)}, {
                 'userName': 1, 'text': 1, '_id': 0}))
    report = getSentimentReport(chat)
    return report

# sistema de recomendaciones
@app.route("/users")
def getAllUsers():
    return dumps(user_coll.find({}, {'userName': 1, "text": 1, '_id': 0}))


app.run("0.0.0.0", 5000, debug=True)
