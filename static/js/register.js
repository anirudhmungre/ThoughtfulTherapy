document.getElementById('register').addEventListener('submit', (e) => {
    e.preventDefault();
    let name = document.getElementById('name').value;
    let username = document.getElementById('username').value;
    let password = document.getElementById('password').value;
    let registerData = {
        name: name,
        username: username,
        password: sha256(password)
    };
    if (name && username && password) {
        fetch('/request/register', {
            method: 'POST',
            body: JSON.stringify(registerData),
            headers: { 'Content-Type': 'application/json' }
        }).then((response) => {
            return response.json();
        }).then((data) => {
            if (data['success']) {
                window.location.href = '/login';
            }
        });
    }
})