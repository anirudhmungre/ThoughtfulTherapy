const addMessage = (text, time, userMessage) => {
    // This function manipulates the DOM to add a new message in the message box element
    // Everything is general formatting for the messages
    let datetime = new Date(time);
    let messageBox = document.getElementById('message-box');

    let messageRow = document.createElement('DIV');
    messageRow.className = 'row';

    let blankSpace = document.createElement('DIV');
    blankSpace.className = 'col';

    let messageSlot = document.createElement('DIV');
    messageSlot.className = 'col-7'

    // Only thing different here is it check who sent message and formats accordingly
    let message = document.createElement('P');
    message.textContent = text;
    message.className = userMessage ? 'message user' : 'message bot';

    let messageTime = document.createElement('P');
    messageTime.textContent = datetime.toLocaleTimeString();
    messageTime.className = 'font-weight-light text-right';

    // Appends all elements to eachother to show the message on the DOM
    message.appendChild(messageTime);
    messageSlot.appendChild(message);
    if (userMessage) {
        messageRow.appendChild(blankSpace);
        messageRow.appendChild(messageSlot);
    } else {
        messageRow.appendChild(messageSlot);
        messageRow.appendChild(blankSpace);
    }

    messageBox.appendChild(messageRow);
};

const updateMessages = (messages) => {
    // This function updates the DOM to show all new messages
    messages = messages.sort((a, b) => { return a.time < b.time; });
    let messageBox = document.getElementById('message-box');
    messageBox.innerHTML = '';
    messages.forEach(m => {
        addMessage(m.message, m.time, m.recipientID == 'b11f6ede-11c7-4705-92cb-d92785903f3d');
    });
    // Automatically scrolls to the bottom once new message arrives
    window.scrollTo(0,document.body.scrollHeight);
};

const getMessages = (sessionID) => {
    // This makes a request to retrieve all new messages of the current session
    // TEST SESSION '6a4c14ac-ef1a-47a6-b451-438d7d572887'
    let sessionData = {
        sessionID: sessionID
    }
    fetch('/messages', {
        method: 'POST',
        body: JSON.stringify(sessionData),
        headers: { 'Content-Type': 'application/json' }
    }).then((response) => {
        return response.json();
    }).then((data) => {
        if (data['success']) {
            // Updates all messages if received new messages
            updateMessages(data['messages']);
        } else {
            // If there is an issue force a logout by clearing client ID creds in storage
            alert('Issue with retrieving messages. Try logging in again.');
            logout();
        }
    });
};

const sendMessage = (clientID, sessionID, message) => {
    // This sends a new message from the client to the AI
    let messageData = {
        message: message,
        sessionID: sessionID,
        clientID: clientID
    }
    fetch('/send', {
        method: 'POST',
        body: JSON.stringify(messageData),
        headers: { 'Content-Type': 'application/json' }
    }).then((response) => {
        return response.json();
    }).then((data) => {
        if (data['success']) {
            // Must retrieve new messages once a message is sent because the AI
            // will automatically and immediately respond
            let sessionID = localStorage.getItem('sessionID');
            getMessages(sessionID);
            // console.log(`Successfully sent: "${message}"`);
        } else {
            alert('Issue with sending message! Try again!');
        }
    });
};

const logout = () => {
    // Clears local creds and redirects for logout
    localStorage.clear();
    window.location.href = '/';
};

// Check IDs makes sure that the client ID and current messaging session ID 
// are available in local storage for use
const checkIDs = () => { return localStorage.getItem('clientID') && localStorage.getItem('sessionID'); };

// On page load make sure to update all required current messages
if (checkIDs) {
    let sessionID = localStorage.getItem('sessionID');
    getMessages(sessionID);
} else {
    // Force logout if there is a message issue
    alert('Issue with retrieving messages. Try logging in again.');
    localStorage.clear();
    window.location.href = '/';
}

// On logout force logout action
document.getElementById('logout').addEventListener('click', () => {
    logout();
});

document.getElementById('send').addEventListener('click', () => {
    // On a send button click we must check all required params are available
    let message = document.getElementById('message');
    if (message.value) {
        if (checkIDs) {
            // If all params check out then we can send message with request
            let clientID = localStorage.getItem('clientID');
            let sessionID = localStorage.getItem('sessionID');
            sendMessage(clientID, sessionID, message.value);
            message.value = '';
        } else {
            alert('Issue with session and client IDs. Try logging in again.');
            logout();
        }
    } else {
        alert('Please enter a message to send!');
    }
    
});