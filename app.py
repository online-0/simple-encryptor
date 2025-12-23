from flask import Flask, request, render_template_string
import base64
import hashlib

app = Flask(__name__)

# ---------- ENCRYPTION LOGIC ----------

def key_from_password(password):
    hash_bytes = hashlib.sha256(password.encode()).digest()
    return sum(hash_bytes)

def encrypt(text, key):
    encrypted_bytes = bytes((ord(c) + key) % 256 for c in text)
    return base64.b64encode(encrypted_bytes).decode()

def decrypt(text, key):
    try:
        encrypted_bytes = base64.b64decode(text)
    except Exception:
        return None
    return ''.join(chr((b - key) % 256) for b in encrypted_bytes)

# ---------- WEB UI ----------

HTML = """
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Simple Encryptor</title>
<style>
body {
    background: #1e1e1e;
    color: white;
    font-family: system-ui;
    padding: 20px;
}
textarea, input {
    width: 100%;
    background: #2b2b2b;
    color: white;
    border: none;
    padding: 10px;
    margin-top: 8px;
    border-radius: 6px;
}
button {
    margin-top: 15px;
    padding: 12px;
    width: 100%;
    background: #3a3a3a;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 16px;
}
</style>
</head>
<body>
<h2>🔐 Simple Encryptor</h2>

<form method="post">
    <label>Message / Encrypted Text</label>
    <textarea name="text" rows="5">{{ text }}</textarea>

    <label>Password</label>
    <input type="password" name="password">

    <button name="action" value="encrypt">Encrypt</button>
    <button name="action" value="decrypt">Decrypt</button>
</form>

{% if result %}
<hr>
<h3>Result</h3>
<textarea rows="5" readonly>{{ result }}</textarea>
{% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    text = ""

    if request.method == "POST":
        text = request.form["text"]
        password = request.form["password"]
        action = request.form["action"]

        if text and password:
            key = key_from_password(password)
            if action == "encrypt":
                result = encrypt(text, key)
            else:
                result = decrypt(text, key) or "Invalid encrypted text"

    return render_template_string(HTML, result=result, text=text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
