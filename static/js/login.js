// If the user is already logged in and accesses this page they should just go straight to their chat
let goToIfLoggedIn = '/chat';

// If the client ID exists it means the user is already logged in
if (localStorage.getItem('clientID')) {
    window.location.href = goToIfLoggedIn;
}

document.getElementById('login').addEventListener('submit', (e) => {
    e.preventDefault();
    // Grabs login credentials
    let username = document.getElementById('username').value;
    let password = document.getElementById('password').value;
    // Hashes the password on client side before sending to the server
    let loginData = {
        username: username,
        password: sha256(password)
    };
    // If both the username and password exist then we can check to login
    if (username && password) {
        // Make a POST request to the login endpoint with the username and password params
        fetch('/request/login', {
            method: 'POST',
            body: JSON.stringify(loginData),
            headers: { 'Content-Type': 'application/json' }
        }).then((response) => {
            return response.json();
        }).then((data) => {
            if (data['success']) {
                // If success in the return JSON then the login was successful and we are given params to store the clientID
                localStorage.setItem('clientID', data['clientID']);
                // Now that we are logged in we must start a new messaging session
                fetch('/start', {
                    method: 'POST',
                    body: JSON.stringify({'clientID': data['clientID']}),
                    headers: { 'Content-Type': 'application/json' }
                }).then((response) => {
                    return response.json();
                }).then((data) => {
                    if (data['success']) {
                        // Once the request comes back we now have a new messaging session ID to use
                        // We can now go to the chat location
                        localStorage.setItem('sessionID', data['sessionID']);
                        window.location.href = goToIfLoggedIn;
                    } else {
                        alert('Issue with session setting.');
                        localStorage.clear();
                    }
                });
            } else {
                // Must retry if login fails
                alert('That username and/or password is incorrect!');
                localStorage.clear();
            }
        });
    }
})