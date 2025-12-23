from flask import Flask, render_template_string

app = Flask(__name__)

HTML = """
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Secure Encryptor</title>

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
    margin-top: 10px;
    padding: 12px;
    width: 100%;
    background: #3a3a3a;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 16px;
}
.small {
    font-size: 14px;
    opacity: 0.8;
}
</style>
</head>

<body>
<h2>🔐 Secure Encryptor</h2>

<label>Message / Encrypted Text</label>
<textarea id="text" rows="5"></textarea>

<label>Password</label>
<input type="password" id="password">
<button onclick="togglePassword()">👁 Show / Hide Password</button>

<button onclick="encrypt()">Encrypt</button>
<button onclick="decrypt()">Decrypt</button>

<h3>Result</h3>
<textarea id="result" rows="5" readonly></textarea>
<button onclick="copyResult()">📋 Copy to Clipboard</button>

<p class="small">Encryption happens locally in your browser.</p>

<script>
// ---------- CRYPTO (CLIENT SIDE) ----------

async function deriveKey(password, salt) {
    const enc = new TextEncoder();
    const keyMaterial = await crypto.subtle.importKey(
        "raw", enc.encode(password), "PBKDF2", false, ["deriveKey"]
    );
    return crypto.subtle.deriveKey(
        {
            name: "PBKDF2",
            salt: salt,
            iterations: 100000,
            hash: "SHA-256"
        },
        keyMaterial,
        { name: "AES-GCM", length: 256 },
        false,
        ["encrypt", "decrypt"]
    );
}

async function encrypt() {
    const text = document.getElementById("text").value;
    const password = document.getElementById("password").value;
    if (!text || !password) return alert("Missing text or password");

    const enc = new TextEncoder();
    const salt = crypto.getRandomValues(new Uint8Array(16));
    const iv = crypto.getRandomValues(new Uint8Array(12));
    const key = await deriveKey(password, salt);

    const encrypted = await crypto.subtle.encrypt(
        { name: "AES-GCM", iv: iv },
        key,
        enc.encode(text)
    );

    const combined = new Uint8Array([
        ...salt, ...iv, ...new Uint8Array(encrypted)
    ]);

    document.getElementById("result").value =
        btoa(String.fromCharCode(...combined));
}

async function decrypt() {
    const data = document.getElementById("text").value;
    const password = document.getElementById("password").value;
    if (!data || !password) return alert("Missing text or password");

    try {
        const raw = Uint8Array.from(atob(data), c => c.charCodeAt(0));
        const salt = raw.slice(0, 16);
        const iv = raw.slice(16, 28);
        const encrypted = raw.slice(28);

        const key = await deriveKey(password, salt);
        const decrypted = await crypto.subtle.decrypt(
            { name: "AES-GCM", iv: iv },
            key,
            encrypted
        );

        document.getElementById("result").value =
            new TextDecoder().decode(decrypted);
    } catch {
        alert("Wrong password or invalid data");
    }
}

function copyResult() {
    const r = document.getElementById("result");
    r.select();
    document.execCommand("copy");
    alert("Copied!");
}

function togglePassword() {
    const p = document.getElementById("password");
    p.type = p.type === "password" ? "text" : "password";
}

// ---------- PWA ----------

if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register(
        URL.createObjectURL(new Blob([`
            self.addEventListener("fetch", e => {});
        `], { type: "text/javascript" }))
    );
}
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
