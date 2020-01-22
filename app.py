from secret.config import DB_CONFIG, MODEL_CONFIG, AI_ID
from objects.sql import SQL
from objects.model import Model
from objects.message import Message
from objects.responses import good_responses, bad_responses, start_conversation_responses

from flask import Flask, request, render_template
from flask_cors import CORS
from hashlib import sha256
from json import dumps
from random import randint
from datetime import datetime

# Global Items
sql = SQL(DB_CONFIG)
model = Model(MODEL_CONFIG)

app = Flask(__name__)
CORS(app)

@app.route('/')
def root():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/request/register', methods=['POST'])
def request_register():
    data = request.get_json()
    try:
        completed = sql.new_client(data['name'], data['username'], data['password'])
        if completed:
            return {'success': True}, 200
        else:
            return {'success': False}, 400
    except:
        return {'success': False}, 400

@app.route('/request/login', methods=['POST'])
def request_login():
    data = request.get_json()
    try:
        client = sql.login(data['username'], data['password'])
        if client:
            return {'clientID': client[0], 'success': True}, 200
        else:
            return {'clientID': None, 'success': False}, 400
    except:
        return {'clientID': None, 'success': False}, 400

@app.route('/start', methods=['POST'])
def start():
    data = request.get_json()
    try:
        session = sql.new_session(data['clientID'])
        if session:
            return {'sessionID': session[0], 'success': True}, 200
        else:
            return {'sessionID': None, 'success': False}, 400
    except:
        return {'sessionID': None, 'success': False}, 400

@app.route('/send', methods=['POST'])
def send():
    data = request.get_json()
    
    try:
        prediction = model.predict(data['message'])
        sentiment = None
        for annotation_payload in prediction:
                sentiment = annotation_payload.text_sentiment.sentiment

        messageClient = Message(data['message'], data['sessionID'], data['clientID'], AI_ID, sentiment)
        completed0 = sql.message(vars(messageClient))
        
        messageToClient = ""
        if any([start_convo in data['message'].lower().split() for start_convo in ['hi', 'hello', 'yo', 'hey']]):
            messageToClient = start_conversation_responses[randint(0, 4)]
        elif (('thanks' in data['message'].lower()) or ('thank you' in data['message'].lower())):
            messageToClient = 'No problem! I\'m always here to help!'
        else:
            if sentiment == 1:
                messageToClient = good_responses[randint(0, 4)]
            else:
                messageToClient = bad_responses[randint(0, 4)]

        messageAI = Message(messageToClient, data['sessionID'], AI_ID, data['clientID'], sentiment)
        completed1 = sql.message(vars(messageAI))

        if completed0 and completed1:
            return {'success': True}, 200
        else:
            return {'success': False}, 400
    except:
        return {'success': False}, 400

@app.route('/messages', methods=['POST'])
def get_messages():
    data = request.get_json()
    try:
        messages = sql.get_messages(data['sessionID'])
        if messages:
            return {'messages': messages, 'success': True}, 200
        else:
            return {'messages': [], 'success': True}, 200
    except:
        return {'messages': [], 'success': False}, 200


# ALL FOR THERAPIST
@app.route('/therapist/client/<client_id>', methods=['GET'])
def clients(client_id):
    try:
        if client_id == 'all':
            clients = sql.get_clients()
            return render_template('clients.html', clients=clients)
        else:
            messages, session_sentiments, name = sql.all_messages(client_id)
            return render_template('clientProfile.html', messages=messages, session_sentiments=session_sentiments, name=name)
    except:
        return "didnt work"

# @app.route('/therapist/client/<client_id>/session/<session_id>', methods=['GET'])
# def client_messages(id):
#     try:
#         messages, session_ids = sql.all_messages(id)
#         return render_template('clientSessions.html', messages=messages, session_ids=session_ids)
#     except:
#         pass

@app.template_filter('human_readable')
def caps(timestamp):
    return datetime.fromtimestamp(int(timestamp/1000)).strftime('%Y-%m-%d %I:%M:%S %p')

if __name__ == '__main__':
    app.run(debug=True, port=8000)