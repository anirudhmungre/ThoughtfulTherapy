let goToIfLoggedIn = '/chat';

if (localStorage.getItem('clientID')) {
    window.location.href = goToIfLoggedIn;
}

document.getElementById('login').addEventListener('submit', (e) => {
    e.preventDefault();
    let username = document.getElementById('username').value;
    let password = document.getElementById('password').value;
    let loginData = {
        username: username,
        password: sha256(password)
    };
    if (username && password) {
        fetch('/request/login', {
            method: 'POST',
            body: JSON.stringify(loginData),
            headers: { 'Content-Type': 'application/json' }
        }).then((response) => {
            return response.json();
        }).then((data) => {
            if (data['success']) {
                localStorage.setItem('clientID', data['clientID']);
                fetch('/start', {
                    method: 'POST',
                    body: JSON.stringify({'clientID': data['clientID']}),
                    headers: { 'Content-Type': 'application/json' }
                }).then((response) => {
                    return response.json();
                }).then((data) => {
                    if (data['success']) {
                        localStorage.setItem('sessionID', data['sessionID']);
                        window.location.href = goToIfLoggedIn;
                    } else {
                        alert('Issue with session setting.');
                        localStorage.clear();
                    }
                });
            } else {
                alert('That username and/or password is incorrect!');
                localStorage.clear();
            }
        });
    }
})