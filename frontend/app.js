
document.addEventListener('DOMContentLoaded', () => {
    const messageDiv = document.getElementById('message');

    function showMessage(message, messageType) {
        messageDiv.innerHTML = message;
        messageDiv.className = messageType;
    }

    function submitForm(e, url) {
        e.preventDefault();
        var username = e.target.elements.username.value;
        var password = e.target.elements.password.value;

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({username: username, password: password})
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('loginSection').style.display = 'none';
                document.getElementById('uploadSection').style.display = 'block';
            } else {
                showMessage(data.error, 'error');
            }
        });
    }

    document.querySelector('#signupForm').addEventListener('submit', e => submitForm(e, 'http://localhost:5000/signup'));
    document.querySelector('#loginForm').addEventListener('submit', e => submitForm(e, 'http://localhost:5000/login'));
});

function uploadFile() {
    let fileInput = document.getElementById('csvFile');
    console.log(fileInput + ' ' + fileInput.files.length)
    if (!fileInput.files.length) {
        console.log("No file selected");
        return;
    }
    let file = fileInput.files[0];
    let reader = new FileReader();
    reader.onload = function(event) {
        let csvData = event.target.result;
        console.log(csvData)
        fetch('http://localhost:5000/upload', {
            method: 'POST',
            headers: {
                'Content-Type': 'text/csv'
            },
            body: csvData
        })
        .then(response => response.json())
        .then(data => {
            console.log(data.length);
            console.log(data);
            if (data.success) {
                console.log("successful upload");
            } else {
                console.log("unsuccessful upload");
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });;
    };
    reader.readAsText(file);
}
