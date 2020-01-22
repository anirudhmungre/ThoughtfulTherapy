
const addMessage = (text, time, userMessage) => {
    let datetime = new Date(time);
    let messageBox = document.getElementById('message-box');

    let messageRow = document.createElement('DIV');
    messageRow.className = 'row';

    let blankSpace = document.createElement('DIV');
    blankSpace.className = 'col';

    let messageSlot = document.createElement('DIV');
    messageSlot.className = 'col-7'

    let message = document.createElement('P');
    message.textContent = text;
    message.className = userMessage ? 'message user' : 'message bot';

    let messageTime = document.createElement('P');
    messageTime.textContent = datetime.toLocaleTimeString();
    messageTime.className = 'font-weight-light text-right';

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
    messages = messages.sort((a, b) => { return a.time < b.time; });
    let messageBox = document.getElementById('message-box');
    messageBox.innerHTML = '';
    messages.forEach(m => {
        addMessage(m.message, m.time, m.recipientID == 'b11f6ede-11c7-4705-92cb-d92785903f3d');
    });
    window.scrollTo(0,document.body.scrollHeight);
};

const getMessages = (sessionID) => {
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
            updateMessages(data['messages']);
        } else {
            alert('Issue with retrieving messages. Try logging in again.');
            localStorage.clear();
            window.location.href = '/';
        }
    });
};

const sendMessage = (clientID, sessionID, message) => {
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
            let sessionID = localStorage.getItem('sessionID');
            getMessages(sessionID);
            console.log(`Successfully sent: "${message}"`);
        } else {
            alert('Issue with sending message! Try again!');
        }
    });
};

const checkIDs = () => { return localStorage.getItem('clientID') && localStorage.getItem('sessionID'); };

if (checkIDs) {
    let sessionID = localStorage.getItem('sessionID');
    getMessages(sessionID);
} else {
    alert('Issue with retrieving messages. Try logging in again.');
    localStorage.clear();
    window.location.href = '/';
}

document.getElementById('logout').addEventListener('click', () => {
    localStorage.clear();
    window.location.href = '/';
});

document.getElementById('send').addEventListener('click', () => {
    let message = document.getElementById('message');
    if (message.value) {
        if (checkIDs) {
            let clientID = localStorage.getItem('clientID');
            let sessionID = localStorage.getItem('sessionID');
            sendMessage(clientID, sessionID, message.value);
            message.value = '';
        } else {
            alert('Issue with session and client IDs. Try logging in again.');
            localStorage.clear();
            window.location.href = '/';
        }
    } else {
        alert('Please enter a message to send!');
    }
    
});