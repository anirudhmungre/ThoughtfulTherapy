from os import environ

def create_secrets():
    pass

from secret.config import DB_CONFIG, MODEL_ID, AI_ID
from google.oauth2 import service_account
from objects.sql import SQL
from objects.model import Model
from objects.message import Message
from objects.responses import good_responses, bad_responses, start_conversation_responses

from flask import Flask, request, render_template
from hashlib import sha256
from json import dumps
from random import randint
from datetime import datetime

# Global Items
# Creates Interfaces for DB and Model
CREDENTIALS = service_account.Credentials.from_service_account_file(
    './secret/therapistAI.json',
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)
sql = SQL(DB_CONFIG)
model = Model(MODEL_ID, CREDENTIALS)

app = Flask(__name__)

@app.route('/')
def root():
    """
    Renders the main page
    """
    return render_template('index.html')

@app.route('/register')
def register():
    """
    Renders the register page
    """
    return render_template('register.html')

@app.route('/login')
def login():
    """
    Renders the login page
    """
    return render_template('login.html')

@app.route('/chat')
def chat():
    """
    Renders the chat page
    """
    return render_template('chat.html')

@app.route('/request/register', methods=['POST'])
def request_register():
    """
    Request endpoint to register a new user
    """
    data = request.get_json()
    try:
        # Completed represents if the user was added with no issue
        completed = sql.new_client(data['name'], data['username'], data['password'])
        if completed:
            return {'success': True}, 200
        else:
            return {'success': False}, 400
    except:
        return {'success': False}, 400

@app.route('/request/login', methods=['POST'])
def request_login():
    """
    Request endpoint to login an already existing user
    """
    data = request.get_json()
    try:
        # client will hold the user ID of the logged in user if successful
        client = sql.login(data['username'], data['password'])
        if client:
            return {'clientID': client[0], 'success': True}, 200
        else:
            return {'clientID': None, 'success': False}, 400
    except:
        return {'clientID': None, 'success': False}, 400

@app.route('/start', methods=['POST'])
def start():
    """
    Starts a new messaging session
    """
    data = request.get_json()
    try:
        # session is the newly generated session ID
        session = sql.new_session(data['clientID'])
        if session:
            return {'sessionID': session[0], 'success': True}, 200
        else:
            return {'sessionID': None, 'success': False}, 400
    except:
        return {'sessionID': None, 'success': False}, 400

@app.route('/send', methods=['POST'])
def send():
    """
    Request endpoint to send a message to the bot
    """
    data = request.get_json()
    
    try:
        # Retrieves the sentiment of the sent message
        prediction = model.predict(data['message'])
        sentiment = None
        for annotation_payload in prediction:
                sentiment = annotation_payload.text_sentiment.sentiment

        # Creates a new message object to the AI
        messageClient = Message(data['message'], data['sessionID'], data['clientID'], AI_ID, sentiment)
        # If successful it counts as completed
        completed0 = sql.message(vars(messageClient))
        
        # Based on multiple factors (below) the bot will return a predefined appropriate response
        # Factor 1 -> Start conversation containing 'hi', 'hello', 'hey', or 'yo'
        # Factor 2 -> End conversation containing 'thanks' or 'thank you'
        # Factor 3 -> Bad sentiment response of 0 must send reassuring message back
        # Factor 4 -> Good sentiment response of 1 must send message back that will aid in happiness continuation
        # Randomization of predetermined messages are used to pick a message
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

        # Creates a message from the AI object and sends to SQL to input in DB for session
        messageAI = Message(messageToClient, data['sessionID'], AI_ID, data['clientID'], sentiment)
        completed1 = sql.message(vars(messageAI))

        # If both messages sent successfully then success is imminent
        if completed0 and completed1:
            return {'success': True}, 200
        else:
            return {'success': False}, 400
    except:
        return {'success': False}, 400

@app.route('/messages', methods=['POST'])
def get_messages():
    """
    Get all messages of a certain session
    """
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
    """
    Renders All of the clients or a specific one based on URL
    """
    try:
        if client_id == 'all':
            clients = sql.get_clients()
            return render_template('clients.html', clients=clients)
        else:
            messages, session_sentiments, name = sql.all_messages(client_id)
            # Calculate the average sentiment of the user over all sessions for profile info
            average_sentiment = sum([s['averageSentiment'] for s in session_sentiments])/len(session_sentiments)
            # Send to the front end all required info
            return render_template(
                    'clientProfile.html', 
                    messages=messages, 
                    session_sentiments=session_sentiments, 
                    name=name,
                    average_sentiment=average_sentiment
                )
    except:
        return "didnt work"

@app.template_filter('human_readable')
def caps(timestamp):
    """
    Custom filter to format the UNIX timestamp from DB into a readable format for the users
    """
    return datetime.fromtimestamp(int(timestamp/1000)).strftime('%Y-%m-%d %I:%M:%S %p')

if __name__ == '__main__':
    app.run(debug=True, port=8000)