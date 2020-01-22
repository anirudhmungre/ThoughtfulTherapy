from time import time

# This object is the template of each message and all items for each message
class Message(object):
    def __init__(self, text, session, sender, recipient, sentiment, widget=None):
        # Holds the text content of the message
        self.text = text
        # The sessionID that the message was sent in
        self.session = session
        # The ID of the sender of the message
        self.sender = sender
        # The ID of the recipient of the message
        self.recipient = recipient
        # The time that the message occurred in unix milliseconds
        self.time = int(time() * 1000)
        # The sentiment of the message (0 is bad, 1 is good)
        self.sentiment = sentiment
        # Holds  events and things for the message for configuration
        self.widget = widget