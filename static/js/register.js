localStorage.clear();
document.getElementById('register').addEventListener('submit', (e) => {
    // On button click of Register button we must perform register action
    e.preventDefault();
    // Grabs all required params
    let name = document.getElementById('name').value;
    let username = document.getElementById('username').value;
    let password = document.getElementById('password').value;
    // Hashes password client side to ensure no interferance
    let registerData = {
        name: name,
        username: username,
        password: sha256(password)
    };
    // Checks all values exist
    if (name && username && password) {
        // Makes a request to register
        fetch('/request/register', {
            method: 'POST',
            body: JSON.stringify(registerData),
            headers: { 'Content-Type': 'application/json' }
        }).then((response) => {
            return response.json();
        }).then((data) => {
            if (data['success']) {
                // If success on server side then we can go to login and test out new creds
                window.location.href = '/login';
            }
        });
    }
})