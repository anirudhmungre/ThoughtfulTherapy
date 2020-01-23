from psycopg2 import connect, sql, Error

# This object controls and interfaces with the Cloud PostgreSQL DB
class SQL(object):
    def __init__(self, DB_CONFIG):
        # Connection to DB using predifined connection params
        self.conn = self.connect_to_db(DB_CONFIG)

    def connect_to_db(self, DB_CONFIG):
        """
        Using predefined connection params, establishes and stores connection to DB
        """
        try:
            conn = connect(
                    user=DB_CONFIG['username'],
                    password=DB_CONFIG['password'],
                    host=DB_CONFIG['host'],
                    port=DB_CONFIG['port'],
                    database=DB_CONFIG['database']
                )
            return conn
        except (Exception, Error) as error :
            #print ('Error while connecting to PostgreSQL', error)
            pass
    
    def disconnect_from_db(self):
        """
        Closes connection to DB
        """
        self.conn.close()

    def new_client(self, name, username, password):
        """
        Registers a new client and adds them to the DB
        """
        try:
            cursor = self.conn.cursor()
            # Add a new client into the DB with credentials specified
            cursor.execute(
                sql.SQL("""
                    INSERT INTO Client(name, username, password)
                    VALUES (%s, %s, %s);
                """),
                [name, username, password]
            )
            
        except (Exception, Error) as error :
            if(self.conn):
                cursor.close()
            return False
        finally:
            self.conn.commit()
            if(self.conn):
                cursor.close()
        return True

    def login(self, username, password):
        """
        Checks if client login params match DB, if they do return client info
        if they don't return None
        """
        try:
            cursor = self.conn.cursor()
            # Check if client exists with defined credentials
            cursor.execute(
                sql.SQL("""
                    SELECT id, username
                    FROM Client
                    WHERE username=%s AND password=%s;
                """),
                [username, password]
            )

            client = cursor.fetchall()
        except (Exception, Error) as error :
            if(self.conn):
                cursor.close()
            return None
        finally:
            if(self.conn):
                cursor.close()
        if len(client):
            return client[0]
        else:
            return None

    def new_session(self, client_id):
        """
        Create a new chat session with empty messages with the therapist AI
        Each session message is tracked and separated from each other session
        """
        session_id = None
        try:
            # Create new sessionwith client ID (sessionID is generated in server side)
            cursor = self.conn.cursor()
            cursor.execute(
                sql.SQL("""
                    INSERT INTO Session(clientID)
                    VALUES (%s);
                """),
                [client_id]
            )

            # Get the new sessionID that was generated
            cursor.execute(
                sql.SQL("""
                    SELECT id FROM Session
                    WHERE clientID=%s
                """),
                [client_id]
            )

            session_id = cursor.fetchall()[-1]
        except (Exception, Error) as error :
            if(self.conn):
                cursor.close()
            return None
        finally:
            self.conn.commit()
            if(self.conn):
                cursor.close()
        return session_id

    def message(self, message):
        """
        Adds a new message in each interaction.
        The message object holds all required info including session info
        """
        try:
            cursor = self.conn.cursor()
            # Create new Interaction with message data
            cursor.execute(
                sql.SQL("""
                    INSERT INTO Interaction(message, senderID, recipientID, time, sentiment)
                    VALUES (%s, %s, %s, %s, %s)
                """),
                [message['text'], message['sender'], message['recipient'], message['time'], message['sentiment']]
            )

            # Get the created interactions interactionID
            cursor.execute(
                sql.SQL("""
                    SELECT id
                    FROM Interaction
                    WHERE time=%s AND senderID=%s AND recipientID=%s
                """),
                [message['time'], message['sender'], message['recipient']]
            )
            interaction_id = cursor.fetchone()[0]

            # Create a relationship between the current session and the new interaction
            cursor.execute(
                sql.SQL("""
                    INSERT INTO InteractionSessionRelational(interactionID, sessionID)
                    VALUES (%s, %s)
                """),
                [interaction_id, message['session']]
            )
        except (Exception, Error) as error :
            if(self.conn):
                cursor.close()
            return False
        finally:
            self.conn.commit()
            if(self.conn):
                cursor.close()
        return True
    
    def get_messages(self, session_id):
        """
        Retrieve all messages associated with a certain session
        """
        try:
            cursor = self.conn.cursor()
            # Get all messages per session ID
            cursor.execute(
                sql.SQL("""
                    SELECT message, senderID, recipientID, time
                    FROM InteractionSessionRelational AS ISR
                    JOIN Interaction AS I ON ISR.interactionID=I.id
                    WHERE sessionID=%s
                """),
                [session_id]
            )

            # Nicely format into list of dicts for json parsing in javascript return
            messages = [ {
                'message': message,
                'senderID': sender_id,
                'recipientID': recipient_id,
                'time': time
                } for (message, sender_id, recipient_id, time) in cursor.fetchall()]
        except (Exception, Error) as error :
            if(self.conn):
                cursor.close()
            return None
        finally:
            if(self.conn):
                cursor.close()
        if len(messages):
            return messages
        else:
            return None

    # EVERYTHING DOWN HERE FOR THERAPISTS
    def get_clients(self):
        """
        Returns all clients on the website
        """
        try:
            cursor = self.conn.cursor()
            # Retrieves all clients and the average sentiment 
            # (or happiness of each client through their experience on the website)
            # Exclued 'b11f6ede-11c7-4705-92cb-d92785903f3d' because that is the ID for the AI
            cursor.execute(
                sql.SQL("""
                    SELECT c.id, c.name, AVG(i.sentiment) AS averageSentiment
                    FROM client AS c
                    LEFT JOIN interaction AS i
                    ON i.senderID=c.id
                    WHERE c.id!=%s
                    GROUP BY c.id
                    ORDER BY c.name;
                """),
                ['b11f6ede-11c7-4705-92cb-d92785903f3d']
            )

            # Nicely format return for clients
            clients = [ {
                'clientID': client_id,
                'clientName': client_name,
                'averageSentiment': average_sentiment
                } for (client_id, client_name, average_sentiment) in cursor.fetchall()]
        except (Exception, Error) as error :
            if(self.conn):
                cursor.close()
            return None
        finally:
            if(self.conn):
                cursor.close()
        if len(clients):
            return clients
        else:
            return None
    
    def all_messages(self, client_id):
        """
        Retrieves every message or interaction by the client from all sessions form all time
        """
        try:
            cursor = self.conn.cursor()
            # Get all sent or received messages by the client from every session
            cursor.execute(
                sql.SQL("""
                    SELECT sessionId, message, senderID, recipientID, time, sentiment
                    FROM InteractionSessionRelational AS ISR
                    JOIN Interaction AS I ON ISR.interactionID=I.id
                    WHERE senderID=%s OR recipientID=%s
                """),
                [client_id, client_id]
            )

            # format all messages for return
            messages = [ {
                'sessionID': session_id,
                'message': message,
                'senderID': sender_id,
                'recipientID': recipient_id,
                'time': time,
                'sentiment': sentiment
                } for (session_id, message, sender_id, recipient_id, time, sentiment) in cursor.fetchall()]

            # Get all sessions the client was a part of and the average sentiment per each of those sessions
            # Also the start and end times of each of those sessions
            cursor.execute(
                sql.SQL("""
                    SELECT S.id, AVG(I.sentiment) AS averageSentiment, MIN(I.time) AS start, MAX(I.time) AS end
                    FROM Session AS S
                    JOIN interactionsessionrelational AS ISR
                    ON ISR.sessionID=S.id
                    LEFT JOIN Interaction AS I
                    ON ISR.interactionID=I.id
                    WHERE I.senderID=%s
                    GROUP BY S.id
                """),
                [client_id]
            )

            # Nicely format for return
            session_sentiments = [{
                'sessionID': session_id,
                'averageSentiment': avg_sentiment,
                'start': start,
                'end': end
            } for (session_id, avg_sentiment, start, end) in cursor.fetchall()]

            # Get the name of the client for front end knowledge
            cursor.execute(
                sql.SQL("""
                    SELECT name
                    FROM Client
                    WHERE id=%s
                """),
                [client_id]
            )
            name = cursor.fetchone()[0]
        except (Exception, Error) as error :
            if(self.conn):
                cursor.close()
            return None
        finally:
            if(self.conn):
                cursor.close()
        if len(messages):
            return messages, session_sentiments, name
        else:
            return None